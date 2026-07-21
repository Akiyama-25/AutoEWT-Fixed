#
# Created by 着火的冰块nya (zhdbk3) on 2025/1/23
#

import time
import logging
import traceback

from tqdm import tqdm

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By

from auto_base import AutoBase


class AutoVideo(AutoBase):
    def finish_a_day(self, day: WebElement) -> None:
        """
        完成一天的任务
        :param day: 该天在网页上的标签
        :return: None
        """
        self.click(day)
        time.sleep(2 * self.config.get('delay_multiplier'))
        btns = self.driver.find_elements(
            By.XPATH,
            "//div[contains(@class, 'btn-AoqsA') "
            "and .//text()[contains(., '学')] "
            "and not(.//text()[contains(., '已学完')])]")
        unit = '节课'
        logging.info(f'该天还剩 {len(btns)} {unit}')
        for i in range(len(btns)):
            logging.info(f'第 {i + 1} / {len(btns)} {unit}')
            try:
                self.finish_a_lesson(btns[i])
            except:
                # 似乎现在不存在这种特殊情况了，但这些逻辑还是留着吧，防止看一半程序暴毙
                # # 出现特殊情况，则跳过，不影响其他课程的完成
                # # 并不是所有课都是视频，还有 FM、试卷等
                # # 对于 FM，只要点进去了就是完成
                # # 对于试卷，留给人来处理
                logging.error(traceback.format_exc())
                logging.warning('该课已跳过')
                logging.warning('如果这是视频课，请报告 bug')
                # 关闭页面，返回首页
                self.close_and_switch()

    def finish_a_lesson(self, btn: WebElement) -> None:
        """
        完成一节课，应对各种突发情况
        :param btn: “学”按钮
        :return: None
        """
        self.click_and_switch(btn)

        video = self.driver.find_element(By.TAG_NAME, 'video')

        # 等待视频元数据加载（duration 有效且 > 0）
        max_wait = 15
        duration = None
        for _ in range(max_wait):
            duration = self.driver.execute_script(
                "var d = arguments[0].duration; return isNaN(d) || !isFinite(d) ? null : d;", video
            )
            if duration is not None and duration > 0:
                break
            time.sleep(1)

        if duration is None or duration <= 0:
            raise RuntimeError(f"视频元数据加载超时（{max_wait}秒），duration={duration}")

        logging.info(f"当前视频总时长: {int(duration)} 秒")

        # 有时需要手动点播放
        try:
            time.sleep(3 * self.config.get('delay_multiplier'))
            self.driver.find_element(By.CLASS_NAME, 'vjs-big-play-button').click()
            logging.info('手动开始播放视频')
        except:
            pass

        with tqdm(total=duration, desc='播放进度', leave=True, ncols=100, unit='秒', unit_scale=True,
                  bar_format='{l_bar}{bar}| {n_fmt}秒/{total_fmt}秒') as pbar:
            while not video.get_attribute('ended'):
                # 更新进度条
                try:
                    current_time = self.driver.execute_script("return arguments[0].currentTime", video)
                except:
                    current_time = self.driver.execute_script(
                        "return videojs('vjs_video_3').currentTime()"
                    )
                pbar.n = current_time
                pbar.refresh()

                # 老师敲黑板，帮你暂停一下
                # 看看你在不在认真听课~
                els: list[WebElement] = self.driver.find_elements(
                    By.XPATH, "//*[contains(text(), '点击通过检查') or contains(text(), '跳过')]"
                )
                els = [e for e in els if e.is_displayed()]
                for e in els:
                    self.click(e)
                    logging.info('点击了检查点或答题点')

                time.sleep(1 * self.config.get('delay_multiplier'))

                # 防止意外暂停，且检测播放完成被暂停的情况
                if self._check_completed_and_paused(video):
                    break

        logging.info('好诶~ 完成啦~')

        self.close_and_switch()

    def _check_completed_and_paused(self, video: WebElement) -> bool:
        """
        检查视频是否因播放完成而被暂停（进度>=99%且处于暂停状态），
        若满足两个条件则视为完成并返回 True；否则恢复播放并返回 False
        """
        try:
            paused = self.driver.execute_script('return arguments[0].paused;', video)
            if paused:
                current_time = self.driver.execute_script('return arguments[0].currentTime;', video)
                duration = self.driver.execute_script('return arguments[0].duration;', video)
                if duration > 0 and current_time / duration >= 0.95:
                    logging.info(f'视频进度 {current_time/duration*100:.1f}% 且已暂停，视为播放完成')
                    return True
                self.driver.execute_script('arguments[0].play();', video)
                logging.info('视频被暂停，已恢复播放')
        except:
            pass
        return False
