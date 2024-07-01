import pkg_resources
import subprocess,os



# 检查依赖库是否安装，如果没有安装则自动安装
def install_package(package):
    """安装指定的包"""
    try:
        subprocess.check_call(['pip', 'install', package])
        print(f"成功安装 {package}")
    except subprocess.CalledProcessError as e:
        print(f"安装 {package} 失败: {e}")

def check_and_install_packages(package_list):
    """检查并安装缺失的包"""
    for package in package_list:
        try:
            pkg_resources.get_distribution(package)
            print(f"{package} 已安装")
        except pkg_resources.DistributionNotFound:
            print(f"{package} 未安装，正在安装...")
            install_package(package)

packages_to_check = ['PyQt5', 'keyboard', 'mouse', 'pygame']
check_and_install_packages(packages_to_check)
# 虚拟环境中执行可能会出错,如果出错提示:qt.qpa.plugin: Could not find the Qt platform plugin "windows" in ""
# This application failed to start because no Qt platform plugin could be initialized. Reinstalling the application may fix this problem.
# 命令行先运行命令:set "QT_PLUGIN_PATH=%VIRTUAL_ENV%\Lib\site-packages\PyQt5\Qt5\plugins" 再运行py脚本,这个命令只能在激活虚拟环境后才能运行

# 依赖库说明:PyQt5用来创建GUI界面,keyboard用来设置全局快捷键,pygame播放声音,mouse获取鼠标坐标
import glob, sys, re, keyboard, pygame, mouse, pygame.midi
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QLineEdit, QPushButton, QHBoxLayout,QColorDialog,QSlider
from PyQt5.QtGui import QPainter, QPen, QPixmap, QPalette, QGuiApplication,QFont,QColor,QImage
from PyQt5.QtCore import Qt, QRect, QPoint, QSize,pyqtSignal,QEvent

# 资源默认路径:存放background.jpg的路径
RES_PATH = "P:/0P/lora训练/"
# 背景图文件名
BK_NAME = "background.jpg"
# 无配置文件时的默认乐谱,抓图时播放的提示音,包括C0到B8的范围,支持升降调例如C#4 Cb4
MUSIC_NOTES = ['G3', 'A3', 'C4', 'C4', 'D4', 'D4', 'E4', 'C4', 'A3', 'G3', 'A3', 'C4', 'C4', 'D4', 'D4', 'E4', 'E4', 'C4']
MIDI乐器编号 = 24  # 0为Acoustic Grand Piano, 1为Electric Grand Piano, 2为Harpsichord, 3为Clavinet 10 Musicbox 八音盒 24 Acoustic Guitar(nylon) 尼龙弦吉他 等等...
# 设置窗口
class SettingsWindow(QWidget):
    # Define a custom signal that will be emitted when the window is closed
    config_updated = pyqtSignal(dict)
    def __init__(self, config,capture_window):
        super().__init__()
        self.capture_window = capture_window
        self.config = config
        self.initUI()
        # 连接信号
        self.capture_window.window_moved.connect(self.updateWindowPosition)
        self.is_maximized = False
        self.aspect_ratio = 1
        self.original_width = 547
        self.original_height = 338
        self.lb = 0
        self.image_paths = []  # 存储图片路径
        self.current_image_index = -1  # 当前显示的图片索引
        self.image_label = QLabel()  # 显示图片的标签
        self.layout.addWidget(self.image_label)
        self.setAcceptDrops(True)  # 设置接受拖拽

        self.shift_pressed = False
        self.last_mouse_pos = None
        self.capture_window.isShortcutEnabled = True
        self.opacity = 1.0  # 初始透明度
  
        # self.resize(self.original_width, self.original_height)
    def initUI(self):
        self.MUSIC_NOTES = self.config['MUSIC_NOTES'].split(",")
        self.MIDI乐器编号 = MIDI乐器编号  # MIDI乐器编号
        self.setGeometry(50, 200, 547, 338)
        self.setWindowTitle('设置')
        self.layout = QVBoxLayout(self)
        # 设置窗口的背景图片
        self.loadBackgroundImage(BK_NAME)
        self.setAttribute(Qt.WA_StyledBackground, False)  # 启用自定义背景
        self.setAutoFillBackground(False)  # 禁用自动填充背景
        self.setBackgroundRole(QPalette.Window)  # 设置背景角色为窗口
        self.setMask(self.background_pixmap.mask())  # 设置遮罩


        # Resolution
        self.resolution_layout = QHBoxLayout()
        self.layout.addLayout(self.resolution_layout)
        self.resolution_label = QLabel('分辨率:', self)
        self.resolution_layout.addWidget(self.resolution_label)

        # 创建编辑框，并设置验证器和输入掩码
        self.resolution_width = QLineEdit(self)
        self.resolution_width.setText(str(self.config['resolution']['width']))
        self.resolution_layout.addWidget(self.resolution_width)

        self.resolution_height = QLineEdit(self)
        self.resolution_height.setText(str(self.config['resolution']['height']))
        self.resolution_layout.addWidget(self.resolution_height)
        
        # Window Position
        self.window_layout = QHBoxLayout()
        self.layout.addLayout(self.window_layout)
        self.window_label = QLabel('窗口坐标:', self)
        self.window_layout.addWidget(self.window_label)
        self.window_x = QLineEdit(str(self.config['window']['x']), self)
        self.window_layout.addWidget(self.window_x)
        self.window_y = QLineEdit(str(self.config['window']['y']), self)
        self.window_layout.addWidget(self.window_y)

        # Image Folder
        self.image_folder_layout = QHBoxLayout()
        self.layout.addLayout(self.image_folder_layout)
        self.image_folder_label = QLabel('图片路径:', self)
        self.image_folder_layout.addWidget(self.image_folder_label)
        self.image_folder_edit = QLineEdit(self.config['image_folder'], self)
        self.image_folder_layout.addWidget(self.image_folder_edit)

        # Screenshot Shortcut
        self.shortcut_layout = QHBoxLayout()
        self.layout.addLayout(self.shortcut_layout)
        self.shortcut_label = QLabel('快捷键:', self)
        self.shortcut_layout.addWidget(self.shortcut_label)
        self.shortcut_edit = QLineEdit(self.config['screenshot_shortcut'], self)
        self.shortcut_layout.addWidget(self.shortcut_edit)
        # Image Prefix
        self.image_prefix_layout = QHBoxLayout()
        self.layout.addLayout(self.image_prefix_layout)
        self.image_prefix_label = QLabel('图片前缀:', self)
        self.shortcut_layout.addWidget(self.image_prefix_label)
        self.image_prefix_edit = QLineEdit(self.config['image_prefix'], self)
        self.shortcut_layout.addWidget(self.image_prefix_edit)
        
        # 连接窗口坐标编辑框的textChanged信号
        self.window_x.textChanged.connect(self.updateCaptureWindowPosition)
        self.window_y.textChanged.connect(self.updateCaptureWindowPosition)
        # 连接分辨率编辑框的textChanged信号
        self.resolution_width.textChanged.connect(self.updateCaptureWindowSize)
        self.resolution_height.textChanged.connect(self.updateCaptureWindowSize)

        # 连接screenshot_shortcut编辑框的textChanged信号
        self.shortcut_edit.textChanged.connect(self.updateScreenshotShortcut)

        # 连接image_folder编辑框的textChanged信号
        self.image_folder_edit.textChanged.connect(self.updateImageFolder)

        # 连接image_prefix编辑框的textChanged信号
        self.image_prefix_edit.textChanged.connect(self.updateImagePrefix)

        # 创建按钮布局
        button_layout = QHBoxLayout()
        self.layout.addLayout(button_layout)

        # 添加按钮
        # Save Button
        self.save_button = QPushButton('保存设置', self)
        self.save_button.clicked.connect(self.saveSettings)
        button_layout.addWidget(self.save_button)
        # 添加打开文件夹按钮
        self.open_folder_button = QPushButton('查看文件夹', self)
        self.open_folder_button.clicked.connect(self.openImageFolder)
        self.image_folder_layout.addWidget(self.open_folder_button)
        
        self.toggle_shortcut_button = QPushButton('禁用快捷键', self)
        self.toggle_shortcut_button.clicked.connect(self.toggleShortcut)
        button_layout.addWidget(self.toggle_shortcut_button)
        self.toggle_shortcut_button.setFocus()  # 设置焦点到按钮

        self.toggle_window_button = QPushButton('隐藏窗口', self)
        self.toggle_window_button.clicked.connect(self.toggleWindow)
        button_layout.addWidget(self.toggle_window_button)

        # 创建按钮布局
        button_layout1 = QHBoxLayout()
        self.layout.addLayout(button_layout1)
        # 设置颜色按钮，
        self.color_button = QPushButton('窗口颜色', self)
        self.color_button.clicked.connect(self.onChangeColor)
        button_layout1.addWidget(self.color_button)
        # 初始化颜色属性
        self.draw_color = QColor(self.config['color'])
        # 打标设置按钮
        self.tag_button = QPushButton('打标设置', self)
        self.tag_button.clicked.connect(self.onSetTag)
        button_layout1.addWidget(self.tag_button)
        
        self.quit_button = QPushButton('退出', self)
        self.quit_button.clicked.connect(self.quitApplication)
        button_layout1.addWidget(self.quit_button)
        # 
        self.midi_layout = QHBoxLayout()
        self.layout.addLayout(self.midi_layout)
        self.midi_label = QLabel('MIDI乐器编号:', self)
        self.midi_layout.addWidget(self.midi_label)
        self.midi_edit = QLineEdit(str(self.MIDI乐器编号), self)
        # 绑定 textChanged 信号到自定义的槽函数
        self.midi_edit.textChanged.connect(self.on_midi_edit_changed)

        self.midi_layout.addWidget(self.midi_edit)
        

        self.midi_label = QLabel('音量:', self)
        self.midi_layout.addWidget(self.midi_label)

        # 创建QSlider，设置范围和初始值
        self.midi_slider_velocity = QSlider(Qt.Horizontal, self)
        self.midi_slider_velocity.setRange(0, 100)
        self.midi_slider_velocity.setValue(self.capture_window.velocity)
        
        # 绑定 valueChanged 信号到自定义的槽函数
        self.midi_slider_velocity.valueChanged.connect(self.on_midi_slider_velocity_changed)

        self.midi_layout.addWidget(self.midi_slider_velocity)
        # 设置拉伸因子，让滑块占据更多的宽度
        self.midi_layout.setStretch(0, 1)  
        self.midi_layout.setStretch(1, 1)  
        self.midi_layout.setStretch(2, 1)  
        self.midi_layout.setStretch(3, 3)  # 音量滑块的拉伸因子3
        
        # 
        self.midi_layout1 = QHBoxLayout()
        self.layout.addLayout(self.midi_layout1)
        self.midi_label1 = QLabel('提示音:', self)
        self.midi_layout1.addWidget(self.midi_label1)
        self.midi_edit1 = QLineEdit(','.join(self.MUSIC_NOTES), self)
        # 绑定 textChanged 信号到自定义的槽函数
        self.midi_edit1.textChanged.connect(self.on_midi_edit1_changed)
            
        self.midi_layout1.addWidget(self.midi_edit1)


        # 调用函数为所有控件设置半透明样式
        self.setWidgetsTransparent(self)
        # 设置控件字体大小
        self.set_widget_font_size(self.window(),17)

    def onSetTag(self):
        return

    def on_midi_edit1_changed(self, text):
        # 将编辑框中的文本（字符串）转换回列表
        try:
            notes_list = text.split(',')
            # 更新 MUSIC_NOTES 列表
            self.MUSIC_NOTES = [note.strip() for note in notes_list if note.strip()]
            self.capture_window.MUSIC_NOTES = self.MUSIC_NOTES  # 更新另一个窗口的乐谱列表
        except Exception as e:
            # 处理可能发生的错误
            print(f"Error: {e}")
    def on_midi_edit_changed(self, text):
        # 尝试将编辑框中的文本转换为整数
        try:
            midi_number = int(text)
            # 如果转换成功，则更新变量 MIDI乐器编号
            self.MIDI乐器编号 = midi_number
            self.capture_window.MIDI乐器编号 = midi_number
        except ValueError:
            # 如果转换失败（例如，文本不是有效的整数），则忽略
            pass

    def on_midi_slider_velocity_changed(self, value):
        # 这里处理滑块值变化
        self.capture_window.velocity = value
        

    def openImageFolder(self):
        # 获取当前编辑框中的路径
        folder_path = self.image_folder_edit.text()
        # 打开文件夹
        if os.path.isdir(folder_path):
            # 使用默认的系统应用程序打开文件夹
            os.startfile(folder_path)
        else:
            # 如果路径不存在，提示用户
            self.showDialog(f"路径 '{folder_path}' 不存在。")
    def onChangeColor(self):
        # 弹出颜色选择对话框，并更新颜色属性
        color = QColorDialog.getColor(self.draw_color)
        if color.isValid():
            self.draw_color = color
            # 重新绘制窗口
            self.update()
            self.capture_window.draw_color = color  # 更新另一个窗口的颜色属性
            self.capture_window.config['color'] = self.draw_color.name()
            self.capture_window.update()  # 更新另一个窗口的绘制

            
    def set_widget_font_size(self,parent_widget, font_size):
        """递归设置所有子控件的字体大小"""
        if parent_widget is not None:
            # 遍历父控件的所有子控件
            for child_widget in parent_widget.children():
                # 检查子控件是否是QWidget的实例
                if isinstance(child_widget, QWidget):
                    # 设置子控件的字体大小
                    child_widget.setFont(QFont(child_widget.font().family(), font_size))
                    # 递归调用函数，以设置子控件的所有子控件的字体大小
                    self.set_widget_font_size(child_widget, font_size)
                
    def setWidgetsTransparent(self, parentWidget):
        # 遍历所有子控件
        for childWidget in parentWidget.findChildren(QWidget):
            # 设置控件的样式为半透明
            childWidget.setStyleSheet("QWidget { background-color: rgba(255, 255, 255, 0.618033988749895); }")

    def wheelEvent(self, event):
        angle = event.angleDelta()

        # 根据滚轮的滚动方向，确定缩放因子
        # 这里简单的以120为一个单位，可以根据需要进行调整
        zoom_factor = 1.0 + (angle.y() / 1600.0)

        # 检查Alt键是否被按下
        if event.modifiers() == Qt.AltModifier:
            # 根据鼠标滚轮的滚动方向调整透明度
            # print(event.angleDelta())
            if event.angleDelta().x() > 0:
                self.opacity += 0.05  # 增加透明度
            else:
                self.opacity -= 0.05  # 减少透明度
            if self.opacity <0.01:
                self.opacity = 0.01
            if self.opacity >1.0:
                self.opacity = 1.0
            # 限制透明度在0.1到1.0之间
            # self.opacity = max(0.01, min(self.opacity, 1.0))

            # 设置窗口的透明度
            self.setWindowOpacity(self.opacity)
            # 获取鼠标滚轮的滚动角度
        else:
            # 获取当前窗口的大小和鼠标在窗口中的位置
            current_size = self.size()
            mouse_pos = event.pos()

            # 计算窗口缩放后的中心点位置
            center = QPoint(current_size.width() // 2, current_size.height() // 2)

            # 计算窗口缩放后的新大小
            new_width = current_size.width() * zoom_factor
            new_height = current_size.height() * zoom_factor

            # 计算窗口缩放后的新位置
            new_x = center.x() - (mouse_pos.x() - center.x()) * zoom_factor
            new_y = center.y() - (mouse_pos.y() - center.y()) * zoom_factor

            # 设置新的窗口大小和位置
            self.resize(QSize(int(new_width), int(new_height)))
            self.move(round(self.x() + (center.x() - new_x)), round(self.y() + (center.y() - new_y)))

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Shift:
                pos = mouse.get_position()
                self.last_mouse_pos = QPoint(pos[0], pos[1])
                self.shift_pressed = True
                return True
        elif event.type() == QEvent.KeyRelease:
            if event.key() == Qt.Key_Shift:
                self.shift_pressed = False
            if event.key() == Qt.Key_V:
                image_width = self.background_pixmap.width()
                image_height = self.background_pixmap.height()
                self.resize(QSize(image_width,image_height))
                return True

        elif event.type() == QEvent.MouseButtonPress:
            self.last_mouse_pos = event.globalPos()
            return False
        elif event.type() == QEvent.MouseMove and self.shift_pressed:
            if self.last_mouse_pos is not None:
                delta = QPoint(event.globalPos() - self.last_mouse_pos)
                self.capture_window.move(self.capture_window.x() + delta.x(), self.capture_window.y() + delta.y())
                self.last_mouse_pos = event.globalPos()
            return True

        return super().eventFilter(obj, event)
        return False

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if os.path.isfile(file_path):  # 确保是文件
                # 获取图片所在的目录
                directory = os.path.dirname(file_path)
                # 获取目录中所有图片文件的路径
                self.image_paths = [os.path.join(directory, f) for f in os.listdir(directory) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
                # 对图片路径列表进行排序，例如按文件名
                self.image_paths.sort()
                # 更新背景 pixmap 为当前拖拽的图片
                self.background_pixmap = QPixmap(file_path)
                # self.updateBackground()  # 更新背景
                self.update()  # 请求重新绘制

    def updateBackground(self):
        # 更新背景 pixmap 并调整窗口大小以适应图片
        self.setFixedSize(self.background_pixmap.size())

    def show_next_image(self):
        self.current_image_index = (self.current_image_index + 1) % len(self.image_paths)
        self.show_image(self.current_image_index)

    def show_previous_image(self):
        self.current_image_index = (self.current_image_index - 1) % len(self.image_paths)
        self.show_image(self.current_image_index)

    def show_image(self, index):
        if self.image_paths:
            self.background_pixmap = QPixmap(self.image_paths[index])
            self.update()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_A:
            self.show_previous_image()
        elif event.key() == Qt.Key_F:
            self.show_next_image()
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.is_maximized:
                # 还原窗口
                self.showNormal()
                # 恢复窗口标题栏
                self.setWindowFlags(self.windowFlags() | Qt.WindowTitleHint)
                self.show()
                self.is_maximized = False
            else:
                # 最大化窗口
                self.showMaximized()
                # 隐藏窗口标题栏
                self.setWindowFlags(self.windowFlags() & ~Qt.WindowTitleHint)
                self.show()
                self.is_maximized = True

    def showNormal(self):
        # 还原窗口位置和大小
        self.setGeometry(self.normal_geometry)
        self.show()

    def showMaximized(self):
        # 最大化窗口
        self.normal_geometry = self.geometry()
        self.setGeometry(QApplication.desktop().availableGeometry(self))
        self.show()
    def contextMenuEvent(self, event):
        v = False
        for widget in self.findChildren(QWidget):
            v = widget.isVisible()
            widget.setVisible(not widget.isVisible())
        self.update()  # 请求重绘
        if not v:   
            # 隐藏窗口标题栏
            self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)  # 设置无边框窗口
        
            # self.setWindowFlags(self.windowFlags() & ~Qt.WindowTitleHint)
        
        else:
            # 获取窗口和图片的尺寸
            window_width = self.width()
            window_height = self.height()
            image_width = self.background_pixmap.width()
            image_height = self.background_pixmap.height()
            
            # 使用示例尺寸最终计算缩放后的尺寸
            new_width,new_height = self.calculate_fill_scaled_size_final(window_width, window_height, image_width, image_height)
            self.original_width = new_width
            self.original_height = new_height
            self.resize(new_width, new_height)      
            # self.resize(image_width, image_height)        
        
            # 切换窗口的窗口标志以显示或隐藏标题栏
        if self.windowFlags() & Qt.WindowFlags(Qt.FramelessWindowHint):
            # 如果当前是无边框（即标题栏隐藏），则恢复默认状态
            self.setWindowFlags(Qt.WindowFlags(Qt.Widget))
        else:
            # 否则，设置为无边框窗口以隐藏标题栏
            self.setWindowFlags(Qt.WindowFlags(Qt.FramelessWindowHint ))  # 保持窗口置顶可选
        self.show()
    def loadBackgroundImage(self, file_path):
        # 加载图片到QPixmap对象
        self.background_pixmap = QPixmap(file_path)
        file_path = os.path.abspath(file_path)
        if os.path.isfile(file_path):  # 确保是文件
            # 获取图片所在的目录
            directory = os.path.dirname(file_path)
            # 获取目录中所有图片文件的路径
            self.image_paths = [os.path.join(directory, f) for f in os.listdir(directory) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            # 对图片路径列表进行排序，例如按文件名
            self.image_paths.sort()
    def toggleShortcut(self):
        # 切换快捷键的启用/禁用状态
        if self.capture_window.isShortcutEnabled:
            keyboard.remove_hotkey(self.capture_window.config['screenshot_shortcut'])
            self.capture_window.isShortcutEnabled = False
            self.toggle_shortcut_button.setText('启用快捷键')
        else:
            keyboard.add_hotkey(self.capture_window.config['screenshot_shortcut'], self.capture_window.startCapture)
            self.capture_window.isShortcutEnabled = True
            self.toggle_shortcut_button.setText('禁用快捷键')

    def toggleWindow(self):
        # 切换抓图窗口的显示/隐藏状态
        if self.capture_window.isVisible():
            self.capture_window.hide()
            self.toggle_window_button.setText('显示窗口')
        else:
            self.capture_window.show()
            self.toggle_window_button.setText('隐藏窗口')
    def closeEvent(self, event):
        # Save config on close
        self.quitApplication()
    def paintEvent(self, event):
        # 在窗口上绘制背景图片
        try:
            painter = QPainter(self)
            # 获取窗口和图片的尺寸
            window_width = self.width()
            window_height = self.height()
            image_width = self.background_pixmap.width()
            image_height = self.background_pixmap.height()
            
            # 使用示例尺寸最终计算缩放后的尺寸
            new_width,new_height = self.calculate_fill_scaled_size_final(window_width, window_height, image_width, image_height)
            # 缩放图片
            scaled_pixmap = self.background_pixmap.scaled(new_width, new_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)

            # 绘制缩放后的图片，左上角对齐
            painter.drawPixmap(0, 0, scaled_pixmap)
        except:
            
            self.background_pixmap = QPixmap(BK_NAME)
            pass

    def calculate_fill_scaled_size_final(self, window_width, window_height, image_width, image_height):
        # 判断控件是否隐藏
        controls_visible = any([control.isVisible() for control in self.findChildren(QWidget)])

        # 如果所有控件都隐藏，则根据窗口的实际可用空间重新计算缩放尺寸
        if not controls_visible:
            # 直接使用窗口的宽高作为缩放尺寸
            scaled_width = window_width
            scaled_height = window_height
        else:
            # 计算宽高比
            window_ratio = window_width / window_height
            image_ratio = image_width / image_height

            # 根据宽高比确定缩放尺寸
            if window_ratio < image_ratio:
                # 窗口更窄，以高度为准进行缩放
                scaled_height = window_height
                scaled_width = int(image_width * (scaled_height / image_height))
            else:
                # 窗口更高，以宽度为准进行缩放
                scaled_width = window_width
                scaled_height = int(image_height * (scaled_width / image_width))
        return scaled_width, scaled_height

    def scale_image_to_window(self):
        # 获取窗口的当前尺寸
        window_width = self.width()
        window_height = self.height()

        # 根据图片的宽高比确定窗口的新尺寸
        if window_width / window_height > self.aspect_ratio:
            new_width = int(window_height * self.aspect_ratio)
            new_height = window_height
        else:
            new_width = window_width
            new_height = int(window_width / self.aspect_ratio)

        # 调整窗口大小以适应图片的宽高比
        self.resize(new_width, new_height)
        # # 缩放图片
        # scaled_image = self.image.scaled(scaled_width, scaled_height, aspectRatioMode=Qt.KeepAspectRatio, transformMode=Qt.SmoothTransformation)
        # pixmap = QPixmap.fromImage(scaled_image)
        # self.image_label.setPixmap(pixmap)

    def resizeEvent(self, event):
        # 当窗口大小改变时，重新缩放图片
        # 判断控件是否隐藏
        # controls_visible = any([control.isVisible() for control in self.findChildren(QWidget)])

        # # 如果所有控件都隐藏，则根据窗口的实际可用空间重新计算缩放尺寸
        # if not controls_visible:
            
        
        super().resizeEvent(event)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
            self.lb = 1
            # 设置焦点到窗口
            self.setFocus()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.dragPos)
            event.accept()
        
    def quitApplication(self):
        # 退出应用程序
        self.saveSettings()
        QApplication.instance().quit()


    def updateScreenshotShortcut(self, shortcut):
        try:
            keyboard.add_hotkey(shortcut, self.capture_window.startCapture)
            # 移除所有快捷键
            keyboard.remove_all_hotkeys()
            # 更新抓图窗口的快捷键设置
            self.capture_window.config['screenshot_shortcut'] = shortcut
            # 重新注册新的快捷键
            keyboard.add_hotkey(shortcut, self.capture_window.startCapture)
            
        except Exception as e:
            # 移除所有快捷键
            keyboard.remove_all_hotkeys()
            # 更新抓图窗口的快捷键设置
            
            # 重新注册新的快捷键
            keyboard.add_hotkey(self.capture_window.config['screenshot_shortcut'], self.capture_window.startCapture)
    def updateImageFolder(self, folder):
        # 更新抓图窗口的图像文件夹设置
        self.capture_window.config['image_folder'] = folder
        # 确保文件夹存在
        # if not os.path.exists(folder):
        #     os.makedirs(folder)

    def updateImagePrefix(self, prefix):
        # 更新抓图窗口的图像前缀设置
        self.capture_window.config['image_prefix'] = prefix
        # 更新抓图窗口的图像前缀设置
    def updateCaptureWindowSize(self):
        # 尝试获取分辨率值，如果转换失败，则不改变窗口大小
        try:
            width = int(self.resolution_width.text())
            height = int(self.resolution_height.text())
            self.capture_window.setGeometry(self.config['window']['x'], self.config['window']['y'], width, height)
            self.config['resolution']['width'] = width
            self.config['resolution']['height'] = height
        except ValueError:
            # 如果输入的不是数字，则不进行操作
            pass
    def updateWindowPosition(self, x, y):
        # 更新窗口坐标
        self.config['window']['x'] = x
        self.config['window']['y'] = y
        self.window_x.setText(str(x))
        self.window_y.setText(str(y))

    def updateCaptureWindowPosition(self):
        # 尝试获取坐标值，如果转换失败，则不移动窗口
        try:
            x = int(self.window_x.text())
            y = int(self.window_y.text())
            self.capture_window.move(x, y)
            self.config['window']['x'] = x
            self.config['window']['y'] = y
        except ValueError:
            # 如果输入的不是数字，则不进行操作
            pass
    def saveSettings(self):
        self.config['resolution']['width'] = int(self.resolution_width.text())
        self.config['resolution']['height'] = int(self.resolution_height.text())
        self.config['window']['x'] = int(self.window_x.text())
        self.config['window']['y'] = int(self.window_y.text())
        self.config['screenshot_shortcut'] = self.shortcut_edit.text()
        self.config['image_folder'] = self.image_folder_edit.text()
        self.config['image_prefix'] = self.image_prefix_edit.text()
        self.config['color'] = self.draw_color.name()
        # self.callback(self.config)  # Call the callback with the updated config
        self.config_updated.emit(self.config)  # Emit the signal with the updated config
        # 更新抓图窗口的位置
        self.updateCaptureWindowPosition()
        with open('config.txt', 'w') as f:
            f.write(f"resolution={self.config['resolution']['width']}x{self.config['resolution']['height']}\n")
            f.write(f"window={self.config['window']['x']},{self.config['window']['y']}\n")
            f.write(f"screenshot_shortcut={self.config['screenshot_shortcut']}\n")
            f.write(f"image_folder={self.config['image_folder']}\n")
            f.write(f"image_prefix={self.config['image_prefix']}\n")
            f.write(f"color={self.config['color']}\n")
            f.write(f"MUSIC_NOTES={','.join(self.MUSIC_NOTES)}\n")
        # No need to close the window
    def updateConfig(self, updated_config):
        # Update the config in the main window
        self.config = updated_config

# 抓图窗口
class CaptureWindow(QMainWindow):
    window_moved = pyqtSignal(int, int)
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.initUI()
        # self.createShortcut()
        keyboard.add_hotkey(self.config['screenshot_shortcut'], self.startCapture) 
        # 初始化pygame
        pygame.init()
        pygame.midi.init()
        # 打开虚拟MIDI输出设备
        self.midi_out = pygame.midi.Output(0)
        # self.midi_out.set_instrument(0)  # 设置乐器编号，0 是钢琴
        self.midi_out.set_instrument(MIDI乐器编号)  # 设置乐器编号，0 是钢琴
        self.note_index = 0
        self.draw_color = QColor(self.config['color'])
        self.MIDI乐器编号  = MIDI乐器编号
    
    def initUI(self):
        self.setGeometry(self.config['window']['x'], self.config['window']['y'], self.config['resolution']['width']+12, self.config['resolution']['height']+12)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.show()
        self.path = self.config['image_folder']
        if not os.path.exists(self.path):  
            os.makedirs(self.path)
        n = get_unique_filename(self.config['image_folder'], self.config['image_prefix'])
        if n is None:
            n = 0
        self.screenshot_number = n
        self.shiftd = 0
        self.mouse_offset = QPoint()  # 初始化鼠标偏移量
        self.window_offset = QPoint()  # 初始化窗口偏移量
        self.setmove = 0

        self.MUSIC_NOTES = self.config['MUSIC_NOTES'].split(',')

        self.velocity = 90  # 音量
        # self.duration = 500  # 每个音符的持续时间（毫秒）

        self.note_mapping = {}

        for note_name in ['C', 'D', 'E', 'F', 'G', 'A', 'B']:
            for accidental in ['', '#', 'b']:
                for octave in range(0, 9):  # 包括C0到B8的范围
                    note = f"{note_name}{accidental}{octave}"
                    self.note_mapping[note] = self.parse_note(note)

    def parse_note(self,note):
        # 初始化变量
        note_name = ""
        accidental = ""
        octave = 0

        # 遍历音符名称的每个字符
        for char in note:
            if char.isdigit():
                octave = int(char)
            elif char in ['#', 'b']:
                accidental = char
            else:
                note_name = char

        # 计算MIDI音高
        # C4对应的MIDI音高是60
        base_value = 60
        note_to_base = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
        accidental_to_semitones = {'': 0, '#': 1, 'b': -1}

        midi_value = base_value + note_to_base[note_name] + accidental_to_semitones[accidental] + (octave - 4) * 12
        return midi_value
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.hide()
            # self.close()
    def paintEvent(self, event):  
        painter = QPainter(self)  
        pen = QPen(QColor(self.config['color']), 6, Qt.SolidLine)  # 6像素宽的红色实线边框  
        painter.setPen(pen)  
    
        # 因为窗口大小增加了12像素（每边6像素），绘制边框时要从3像素开始，到窗口内部减去3像素  
        # 这样边框就不会绘制到额外的空间上  
        border_width = 3  
        rect = QRect(border_width, border_width, self.width() - 2*border_width, self.height() - 2*border_width)  
        painter.drawRect(rect)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.dragPos)
            event.accept()
            
    def moveEvent(self, event):
        # 发出信号
        self.window_moved.emit(self.x(), self.y())

    def startCapture(self):  
        self.path =  self.config['image_folder']
        if not os.path.exists(self.path):
            os.makedirs(self.path)

        n = get_unique_filename(self.path, self.config['image_prefix'])
        self.screenshot_number = n+1  
        fmq = self.config['image_prefix']
        filename = self.path + f'/{fmq}_{self.screenshot_number:04d}.png'  
        self.saveScreenshot(filename)  # save screenshot with generated filename  

        # 播放音符
        try:
            # 使用split()方法将字符串转换为列表
            note = self.MUSIC_NOTES[self.note_index % len(self.MUSIC_NOTES)]
            midi_note = self.note_mapping[note]
            self.midi_out.set_instrument(self.MIDI乐器编号)  # 设置乐器编号，0 是钢琴
            self.midi_out.note_off(midi_note, self.velocity)  # 发送音符关闭消息
            self.midi_out.note_on(midi_note, self.velocity)  # 发送音符开启消息
        except:
            midi_note = self.note_mapping["F7"]
            self.midi_out.set_instrument(self.MIDI乐器编号)  # 设置乐器编号，0 是钢琴
            self.midi_out.note_off(midi_note, self.velocity)  # 发送音符关闭消息
            self.midi_out.note_on(midi_note, self.velocity)  # 发送音符开启消息
            pass

        # 更新音符索引
        self.note_index += 1
        if self.note_index>=len(self.MUSIC_NOTES):
            self.note_index=0

    def updateConfig(self, updated_config):
        # Update the config in the main window
        self.config = updated_config
    def saveScreenshot(self, filename):  

        screen = QApplication.primaryScreen()   
        # 获取窗口的实际大小和位置  
        rect = QRect(self.pos() + QPoint(6, 6), self.size() - QSize(12, 12))  
        screenshot = screen.grabWindow(0, rect.x(), rect.y(), rect.width(), rect.height())  
        screenshot.save(filename)
        print(f"Screenshot saved to {filename}")
  
    def closeEvent(self, event):
        # Save config on close
        # # 关闭MIDI输出设备
        del midi_out
        pygame.midi.quit()
        
        self.quitApplication()


class TagsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Tags Window')
        self.setGeometry(100, 100, 600, 400)
        self.setAcceptDrops(True)  # 设置窗口接受拖拽事件
        self.image_label = QLabel(self)  # 创建一个标签用于显示图片
        self.image_label.setGeometry(10, 10, 580, 380)
        self.show()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                self.show_image(file_path)

    def show_image(self, file_path):
        pixmap = QPixmap(file_path)
        self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

        
# 读取配置
def read_config(file_path):
    config = {}
    notes_str = ','.join(MUSIC_NOTES)
    if not os.path.exists(file_path):
        # Save the current values of the variables to the config file
        with open(file_path, 'w') as f:
            f.write(f"resolution={1024}x{1024}\n")
            f.write(f"window={100},{100}\n")
            f.write(f"screenshot_shortcut={1}\n")
            f.write(f"image_folder=1_cat\n")
            f.write(f"image_prefix=cat\n")
            f.write(f"color=#2abfff\n")
            f.write(f"MUSIC_NOTES={notes_str}\n")
            
    with open(file_path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            key, value = line.strip().split('=')
            if key == 'resolution':
                width, height = value.split('x')
                config[key] = {'width': int(width), 'height': int(height)}
            elif key == 'window':
                x, y = value.split(',')
                config[key] = {'x': int(x), 'y': int(y)}
            else:
                config[key] = value
    return config

# 获取图片后缀需要的数
def get_unique_filename(path, prefix):
    # 检查目录是否存在
    if not os.path.exists(path):
        os.makedirs(path)
    
    # 获取目录中所有以指定前缀开头的文件名
    existing_files = glob.glob(os.path.join(path, f'*{prefix}*.png'))
    
    # 如果没有找到任何文件，返回1
    if not existing_files:
        return 0
    
    # 使用正则表达式匹配文件名中的数字
    numbers = []
    for file in existing_files:
        # 根据前缀是否存在，使用不同的正则表达式
        if prefix == '':
            match = re.search(r'(\d+)', os.path.splitext(os.path.basename(file))[0])
        else:
            match = re.search(r'(\d+)', os.path.splitext(os.path.basename(file))[0].split(prefix)[1])
        if match:
            numbers.append(int(match.group()))
    
    # 如果没有匹配到数字，返回1
    if not numbers:
        return 0
    
    # 找到最大的数字
    max_number = max(numbers)
    
    # 检查文件数量是否与最大编号一致
    if len(existing_files) != max_number:
        # 重命名所有文件
        for i, file in enumerate(sorted(existing_files), start=1):
            new_filename = f'{prefix}_{str(i).zfill(4)}.png'
            new_filepath = os.path.join(path, new_filename)
            os.rename(file, new_filepath)
        numbers = []
        for file in existing_files:
            # 根据前缀是否存在，使用不同的正则表达式
            if prefix == '':
                match = re.search(r'(\d+)', os.path.splitext(os.path.basename(file))[0])
            else:
                match = re.search(r'(\d+)', os.path.splitext(os.path.basename(file))[0].split(prefix)[1])
            if match:
                numbers.append(int(match.group()))
        # 获取文件数量作为后缀最大值
        max_number = len(numbers)
    
    return max_number

def get_image(url,filename):
    # 发起请求，下载图片
    try:
        import requests
        response = requests.get(url)
        response.raise_for_status()  # 如果请求错误，将抛出异常
        
        # 使用 QPixmap 加载图片
        pixmap = QPixmap()
        pixmap.loadFromData(response.content)

        # 获取图片尺寸
        width = pixmap.width()
        height = pixmap.height()

        # 计算新的尺寸
        if width>2048 or height>2048:
            if width > height:
                new_width = 2048
                new_height = int(height * (2048 / width))
            else:
                new_height = 2048
                new_width = int(width * (2048 / height))

        # 创建一个新的 QPixmap 并缩放
        scaled_pixmap = pixmap.scaled(new_width, new_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        scaled_pixmap.save(filename)

        print(f'图片已保存并缩放为 {filename}')
    except:
        print(f'下载图片失败')
    
def main():
    app = QApplication(sys.argv)
    config_file = 'config.txt'
    background_image = BK_NAME

    # 检查文件是否存在
    # if not os.path.exists(config_file):
    #     config_file = f'{RES_PATH}config.txt'
    if not os.path.exists(background_image):
        background_image = f'{RES_PATH}{BK_NAME}'
        if not os.path.exists(background_image):

            # 定义图片的URL和保存的文件名
            url = 'https://i0.hdslb.com/bfs/album/6ad25a5643a9357b4c38dea7c096522eb8211e39.jpg'
            # url = 'https://i0.hdslb.com/bfs/album/ef43dee53b9a3481316eeec80c4b4ce18031633c.png'
            # url = 'https://i0.hdslb.com/bfs/album/a9937c43c1f04581e2bf97c20ea925f25acd49f8.jpg'
            filename = BK_NAME
            get_image(url,filename)

        else:
            background_image = f'{RES_PATH}{BK_NAME}'

    config = read_config(config_file)

    capture_window = CaptureWindow(config)
    settings_window = SettingsWindow(config, capture_window)
    # settings_window.loadBackgroundImage(background_image)  # 加载背景图片

    settings_window.config_updated.connect(capture_window.updateConfig)   

    # 安装事件过滤器
    QGuiApplication.instance().installEventFilter(settings_window)

    settings_window.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()