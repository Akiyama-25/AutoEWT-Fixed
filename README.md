# AutoEwt Fiexed by [しょうてん](https://github.com/Akiyama-25)

## 相对于原项目的调整

本项目，在 [zhdbk3/AutoEwt v0.8](https://github.com/zhdbk3/AutoEwt) 的基础上做了以下修改：

### Bug 修复

- **修复跨天课程识别为空的问题**：原版 `finish_days_list()` 在循环前一次性缓存所有天数元素，完成一天后页面 DOM 重新渲染导致后续元素引用失效（stale element），使得下一天的课程被识别为 0 节并跳过。现在每次循环重新查询天数列表。

### 功能改进

- **CDP 原生鼠标事件点击**：`click()` 方法改用 Chrome DevTools Protocol 的 `Input.dispatchMouseEvent`，模拟 `isTrusted=true` 的真实鼠标事件，绕过 e网通平台对自动化点击的检测。
- **驱动自动查找**：`config.yml` 中 `driver_path` 设置为 `auto` 时，程序自动在同一目录下查找对应浏览器的驱动（Chrome → `chromedriver-win64/chromedriver.exe`，Edge → `msedgedriver.exe`）。当然自定义也可以。


## 下面的描述基本复制自原项目自述文件
当然我有意地保留了自己的话，~~还是废话~~
另外，试卷部分我没有测试，不保证可以正常使用
**当前还会出现本课程已完成，但是没自动切换的问题，也许是我开着代理的原因？总之待复现修复**

## 协议与声明

- 本软件遵循 [GNU General Public License v3.0](LICENSE) 开源许可证。
- **本软件的目的仅在研究 `Python` 技术，您不得使用它来应付学校的任务，或是做其他违反纪律、法律的事。**
- **如果您擅自使用本软件做不当的事，产生的任何后果和影响均由您自己承担，与我们无关。**
- **开始使用本软件即代表您同意上述协议和声明，同意原作者 [着火的冰块nya](https://space.bilibili.com/551409211) 与本人及其他开发者不为您的行为承担任何责任。**

## 如何使用

> [!NOTE]
> **不要把本软件或浏览器驱动放在包含中文或其他特殊字符的路径下！**

### 1. 下载浏览器驱动

请打开您的浏览器，查看它的版本。

然后下载**对应版本**的浏览器驱动，**解压**后放在您喜欢的位置。非对应版本可嫩导致该脚本无法正常运作。

以下是一些您可能用得到的链接：

- [Chrome 驱动文件下载 (chromedriver)](https://www.cnblogs.com/aiyablog/articles/17948703)
- [Edge 驱动文件下载 (msedgedriver)](https://developer.microsoft.com/zh-cn/microsoft-edge/tools/webdriver)
- [Firefox 驱动文件下载 (geckodriver)](https://github.com/mozilla/geckodriver/releases)

以下是所有**可能**支持的浏览器：

- Firefox
- Chrome（如果你是 Chromium，也请在下面的浏览器名中填写 Chrome）
- Ie
- Edge
- Safari
- WebKitGTK
- WPEWebKit

推荐使用 **Edge**，因为我们的开发就在 Edge 上进行。别的浏览器不保证能用。

### 2. 修改配置文件

请根据您自己的情况，修改 `config.yml.default` 中的内容，并删去 `.default` 后缀：

```yaml
# 修改时不要删掉冒号后的空格

browser: 浏览器名称（首字母大写），如 Chrome, Edge 等
driver_path: 浏览器驱动路径
username: 用户名
password: 密码
list_url: 课程列表页面的链接

# 延迟倍率（默认1.0，如需修改请输入浮点数）
delay_multiplier: 1.0

# AutoEwt 模式，选填 video（看课）/ paper（做试卷）
mode: video

# 是否 (true / false) 给选择题选择正确答案
choose_correctly: true
# 如果 choose_correctly 为 true，请填写 report_id 字段，否则可以不动
# 一张**已经完成**的试卷的 reportId（请到浏览器上方链接中获取该参数的值）
report_id: reportId

# 开发者选项
# 从第几天开始扫描（用于开发者调试程序方便，当然用户也可以设置，每次启动能省一丢丢时间）
day_to_start_on: 1
# 浏览器启动时的参数，这里给了个静音（--mute-audio），参数还有：无头——隐藏浏览器窗口（--headless）
options: --mute-audio
```

> [!NOTE]
> 填写 `driver_path` 字段时，您可能会使用 Windows 11 右键菜单的“复制文件地址”或是使用快捷键**Ctrl+Shift+C**，这样得到的路径是**带引号的**。请**删除引号**。

### 3. 启动！

双击运行 `AutoEwt`，然后用您的双手去做更有意义的事！

> [!NOTE]
> 在该程序运行时启动 Minecraft 可能会导致视频被暂停，建议 Minecraft 启动完成之后检查一下视频播放情况，以免造成不必要的损失。
> 
> 该 bug 作用机理尚不明确，难以稳定复现，且不存在任何日志记录，无法修复，见谅。
> 
> 如果您找到了稳定复现的方法，欢迎提 issue 报告。
>
> ~~当然[しょうてん](https://github.com/Akiyama-25)这条区没测试~~

## 开发环境

- Python 3.10
- Chrome 150.0.7871.125 64位
