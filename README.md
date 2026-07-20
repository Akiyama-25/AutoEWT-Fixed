# AutoEwt v0.9.1 Windows Fix

基于 [zhdbk3/AutoEwt v0.8](https://github.com/zhdbk3/AutoEwt) 的修改版本，由 [しょうてん](https://github.com/Akiyama-25) 维护。

## 相对于原项目的修改

### Bug 修复

- **修复跨天课程识别为空**：原版 `finish_days_list()` 在循环前一次性缓存天数元素，完成一天后页面 DOM 重新渲染导致 stale element，后续天数课程被识别为 0 节并跳过。现在每次循环重新查询。
- **视频播放完成自动切换**：平台有时在视频播放到末尾时暂停视频，但不触发 `ended` 事件，导致脚本卡死。新增逻辑：当视频进度 >= 95% 且处于暂停状态时，自动视为播放完成并切换下一课程。

### 功能改进

- **CDP 原生鼠标事件**：`click()` 方法改用 Chrome DevTools Protocol 的 `Input.dispatchMouseEvent`，模拟 `isTrusted=true` 的真实鼠标事件，绕过 e网通平台对自动化点击的检测。
- **支持从源码运行**：新增 `run.bat`，可直接运行 Python 源码，无需每次修改后重新打包。

### 行为变更

- **移除驱动自动查找**：`driver_path` 不再支持 `auto` 值，必须手动指定驱动文件的完整路径。

## 使用方法

> **注意：** 不要把本软件或浏览器驱动放在包含中文或其他特殊字符的路径下。

### 1. 下载浏览器驱动

查看浏览器版本，下载**对应版本**的驱动并解压：

- [ChromeDriver](https://www.cnblogs.com/aiyablog/articles/17948703)
- [Edge WebDriver](https://developer.microsoft.com/zh-cn/microsoft-edge/tools/webdriver)
- [GeckoDriver (Firefox)](https://github.com/mozilla/geckodriver/releases)

### 2. 配置

将 `config.yml.default` 复制为 `config.yml`，按实际情况填写：

```yaml
browser: Chrome                              # 浏览器名称（首字母大写）
driver_path: chromedriver-win64/chromedriver.exe  # 驱动文件路径
username: 你的用户名
password: 你的密码
list_url: 课程列表页面链接

delay_multiplier: 1.0     # 延迟倍率（浮点数，默认 1.0）
mode: video               # video（看课）/ paper（做试卷）
choose_correctly: true    # 选择题是否自动选正确答案
report_id: reportId       # 已完成试卷的 reportId（choose_correctly 为 true 时填写）
day_to_start_on: 1        # 从第几天开始扫描
options: --mute-audio     # 浏览器启动参数
```

> **提示：** Windows 右键"复制文件地址"或 Ctrl+Shift+C 得到的路径带引号，需手动删除。

### 3. 运行

| 方式 | 命令 |
|------|------|
| exe | 双击 `AutoEwt.exe` |
| 源码 | 双击 `run.bat`，或在项目根目录执行 `python src/main.py` |

## 已知问题

- 课程完成后偶尔不自动切换、进度不刷新，手动刷新也无效。可能与网络代理有关，待复现。
- 不建议在脚本运行时手动切换课程，可能导致脚本跳转到其他日期。
- 网易云音乐键盘快捷键可能干扰视频播放。

## 开发环境

- Python 3.10
- Chrome 150.0.7871.125 64-bit

## 协议

[GNU General Public License v3.0](LICENSE)

**本软件仅用于 Python 技术研究。使用本软件做不当之事产生的后果由使用者自行承担，与原作者及开发者无关。开始使用即代表同意上述声明。**
