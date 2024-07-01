# 截图小工具

* 能快速轻松按设定分辨率和位置截取图片,特别适合快速截取 游戏/视频/图片 中的一部分作为模型训练素材.
* 能快速设定截图路径和图片前缀,目录结构符合sd-scripts

# 使用说明简略版

1. 下载 `抓图.py` 到你的训练素材目录，比如 `d:/训练素材`。(也可以放在任意目录,但图片路径需要填绝对路径)
2. 双击打开 `抓图.py`，设置图片路径（可用文件夹名或绝对路径,设置图片前缀，拖动截图窗口到合适位置,点击窗口空白处避免输入焦点在输入框。 
3. 按键盘数字键 1 截图，听到提示音则截图成功，默认路径为当前程序所在文件夹。

## 图片展示

![1719864526242.png](image/README/1719864526242.png)

## 其他可用功能和快捷键（设置窗口内生效）

### 移动抓图窗口

- 在设置窗口内按住 shift 移动鼠标可以移动抓图窗口。也可以拖拽抓图窗口边缘。配合双击设置窗口全屏和按住alt滚轮设置窗口透明可方便全屏移动.

### 图片浏览

1. 拖拽任意图片文件到设置窗口可以修改背景图，按 V 重设窗口大小适应图片大小，右键单击设置窗口隐藏/显示所有控件。
2. 按 A 切换背景图目录中上一张图片，按 F 切换下一张图片，双击设置窗口空白处能最大化设置窗口。
3. 按住 alt 上下滚动鼠标滚轮可以修改设置窗口透明度，需要注意透明度最低是 0.01，并不是完全透明，会对窗口背后的画面有污染,截图需要移开设置窗口.
4. 鼠标滚轮可以缩放设置窗口大小（缩放算法有点糟糕需要改进,应该修改设置窗口铺满全屏,然后只移动缩放图片可能效果会更好）。

### 文件保存和依赖库安装

1. 截图保存图片路径只填文件夹名为当前 py 文件所在目录，也可以填写绝对路径，比如 `d:/cat`，需要注意路径中斜杠最好用反斜杠 `\`。
2. 每次抓图会检测文件最大后缀和文件数量是否一致，后缀不连贯会自动重命名所有文件，比如你抓了几张图然后觉得其中一些不需要删除了，再抓图他会自动重命名所有文件保证文件名连续，如果你手动改过文件名可能会触发 bug 重命名失败。
3. 程序启动会自动检测依赖库是否安装并安装，如果你是在虚拟环境中执行可能会启动失败，需要先命令行执行命令：`set "QT_PLUGIN_PATH=%VIRTUAL_ENV%\Lib\site-packages\PyQt5\Qt5\plugins"`，理论支持在 Linux 上运行。
4. 如果出现功能无效或者异常退出，大概率是触发了意料之外的 BUG，请自行 DEBUG。
5. 打标功能还未添加，未来会增加可视化打标功能。

## 注意事项

- 测试环境 python 3.10.6 和 3.11.1 都正常运行，其他的没试过。
- 分辨率需要是 64 的倍数，SDXL 默认 1024*1024。
- 默认抓图快捷键 1，大键盘和小键盘的 1 都行。
- 快捷键修改实时生效，如果输入的快捷键无效则不会更改快捷键。
- 支持单个键的快捷键，也支持任意数量组合的快捷键。
- 快捷键格式：快捷键 或者 快捷键+快捷键+快捷键...，比如 `s` 或者 `ctrl+s+d+alt`。
- 特殊键比如 `ctrl` `alt` `esc` `f1` `shift` 写法和键盘上的基本差不多，其他的自行查看 keyboard 库的文档。
- 正常退出会自动保存当前设置。
- keyboard 库是一个全局监听键盘按键的库，可能会被安全软件拦截。
- 只有截图快捷键是全局热键，其他的需要激活设置窗口才有效。
- 启动时默认会加载目录下background.jpg作为背景图,如果不存在会从https://www.bilibili.com/opus/623418398550389428下载一张

## 代码中资源默认路径可以自行查找修改

```python
# 资源默认路径:存放background.jpg的路径
RES_PATH = "P:/0P/lora训练/"
```
