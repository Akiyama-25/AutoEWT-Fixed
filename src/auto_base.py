#
# 此模块用于存储通用的工具函数
#

import os
import logging
import time
from abc import ABC, abstractmethod
from functools import cache

import yaml
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By


@cache
def read_config() -> dict:
    """
    配置文件样例：
    # 修改时不要删掉冒号后的空格
    browser: 浏览器名称（首字母大写），如 Chrome, Edge 等
    driver_path: 浏览器驱动路径
    username: 用户名
    password: 密码
    list_url: 课程列表页面的链接
    # 浏览器启动时的参数，这里给了个静音
    options: --mute-audio
    # AutoEwt 模式，选填 watch（看课）/ test（做试卷）
    mode: watch
    """
    if not os.path.exists('config.yml'):
        logging.error('配置文件 config.yml 不存在，请检查！')
        exit(1)
    with open('config.yml', encoding='utf-8') as f:
        config = yaml.load(f, yaml.FullLoader)
        # 密码可能是纯数字
        config['password'] = str(config['password'])
        # 如果转换延迟倍率为浮点数，失败（不存在或不合法）则报错并默认1.0
        try:
            config['delay_multiplier'] = float(config.get('delay_multiplier'))
        except ValueError:
            logging.warning('配置文件中 delay_multiplier 不是合法的浮点数，将使用默认值 1.0')
            config['delay_multiplier'] = 1.0
        except TypeError:
            logging.info('配置文件中未设置 delay_multiplier，将使用默认值 1.0')
            config['delay_multiplier'] = 1.0
        logging.info('成功读取到配置文件')
    # 校验驱动路径
    driver_path = config.get('driver_path')
    if not driver_path or driver_path == 'auto':
        logging.error('请在 config.yml 中手动指定 driver_path（浏览器驱动的完整路径）')
        exit(1)
    if not os.path.exists(driver_path):
        logging.error(f'驱动文件不存在: {driver_path}')
        exit(1)
    logging.info(f'使用驱动: {driver_path}')
    return config


class AutoBase(ABC):
    def __init__(self):
        self.config = read_config()
        self.mode = self.config['mode']
        self.driver = self.init_driver()

        self.token = self.login()
        self.finish_days_list()

    def init_driver(self):
        browser = self.config['browser']

        options = getattr(webdriver, browser.lower()).options.Options()
        options.add_argument(self.config['options'])
        # 禁用通知和 GCM 推送，避免反复注册
        options.add_argument('--disable-notifications')
        options.add_argument('--disable-background-networking')
        options.add_argument('--disable-features=GCM,GCMChannelStatus,PushMessaging')
        options.add_argument('--disable-sync')
        options.add_argument('--disable-domain-reliability')
        options.add_argument('--disable-component-update')
        options.add_argument('--no-first-run')
        driver = getattr(webdriver, browser)(
            service=getattr(webdriver, browser.lower()).service.Service(self.config['driver_path']),
            options=options
        )
        driver.maximize_window()
        driver.get(self.config['list_url'])
        driver.implicitly_wait(3)
        return driver

    def login(self) -> str:
        """
        登录
        :return: token
        """
        logging.info('登录账号……')
        self.driver.find_element(By.ID, 'login__password_userName').send_keys(self.config['username'])
        self.driver.find_element(By.ID, 'login__password_password').send_keys(self.config['password'])
        self.driver.find_element(By.CLASS_NAME, 'ant-btn-block').submit()
        # 等待一段时间，确保页面加载完成并生成 token
        time.sleep(3 * self.config.get('delay_multiplier'))
        # 获取所有 cookie
        cookies = self.driver.get_cookies()
        token = None
        for cookie in cookies:
            if cookie['name'] == 'token':
                token = cookie['value']
                break
        return token

    def click(self, btn: WebElement) -> None:
        """
        通过 CDP Input.dispatchMouseEvent 分发原生鼠标事件
        模拟真实事件 isTrusted=true，绕过 EWT360 的自动化检测
        """
        try:
            rect = self.driver.execute_script(
                'var r = arguments[0].getBoundingClientRect();'
                'return {x: r.x + r.width / 2, y: r.y + r.height / 2};',
                btn
            )
            x, y = rect['x'], rect['y']
            self.driver.execute_cdp_cmd('Input.dispatchMouseEvent',
                {'type': 'mousePressed', 'x': x, 'y': y, 'button': 'left', 'clickCount': 1})
            self.driver.execute_cdp_cmd('Input.dispatchMouseEvent',
                {'type': 'mouseReleased', 'x': x, 'y': y, 'button': 'left', 'clickCount': 1})
        except Exception:
            btn.click()

    def click_and_switch(self, btn: WebElement) -> None:
        """
        点击按钮并切换到新页面
        :param btn: 要点击的按钮
        """
        self.click(btn)
        time.sleep(1 * self.config.get('delay_multiplier'))  # 给新页面反应一会
        # 切换到当前页面
        handles = self.driver.window_handles
        self.driver.switch_to.window(handles[1])
        time.sleep(3 * self.config.get('delay_multiplier'))

    def close_and_switch(self) -> None:
        """关闭当前页面并返回到首页"""
        try:
            handles = self.driver.window_handles
            self.driver.close()
            self.driver.switch_to.window(handles[0])
            time.sleep(1 * self.config.get('delay_multiplier'))
        except Exception:
            logging.warning('关闭页面时浏览器连接已断开')

    def finish_days_list(self) -> None:
        """完成所有天"""
        time.sleep(5 * self.config.get('delay_multiplier'))
        days = self.driver.find_elements(By.CSS_SELECTOR, 'li[data-active="true"], li[data-active="false"]')
        logging.info(f'一共有 {len(days)} 天的任务')
        for i in range(self.config['day_to_start_on'] - 1, len(days)):
            logging.info(f'================ 第 {i + 1} / {len(days)} 天 ================')
            # 每次重新查询，避免 DOM 更新后 stale element
            days = self.driver.find_elements(By.CSS_SELECTOR, 'li[data-active="true"], li[data-active="false"]')
            self.finish_a_day(days[i])

    @abstractmethod
    def finish_a_day(self, day: WebElement) -> None:
        """
        完成一天的任务
        :param day: 该天在网页上的标签
        """
        ...
