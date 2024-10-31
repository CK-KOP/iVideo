import sys
import threading
import time
from bilibilidownload import start_download
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QSlider,
    QLabel,
    QStyleOptionSlider,
    QStyle
)
from PyQt5.QtGui import QIcon, QPixmap, QColor, QLinearGradient, QCursor ,QPainter, QBrush,QFont,QMouseEvent,QPen
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import Qt, QUrl, QTimer, QSize, pyqtSignal, QPoint

# 高光按钮基类:显示高光图标
class HighlightButton(QPushButton):
    def __init__(self, text, size, dark_icon_path,light_icon_path, parent=None):
        super().__init__(text, parent)
        self.size = size # 按钮图标大小
        self.text = text
        self.dark_icon_path = dark_icon_path
        self.light_icon_path = light_icon_path
        self.normal_icon = QIcon(self.dark_icon_path)
        self.highlight_icon = QIcon(self.light_icon_path)
        self.setText(self.text)
        self.setIcon(self.normal_icon)
        self.setIconSize(QSize(size, size))
    def enterEvent(self, event):
        # 鼠标进入时设置高亮图标
        self.setIcon(self.highlight_icon)
        # 设置小手鼠标
        self.setCursor(QCursor(Qt.PointingHandCursor))
        # self.setIconSize(QSize(16, 16))
        super().enterEvent(event)

    def leaveEvent(self, event):
        # 鼠标离开时恢复正常图标
        self.setIcon(self.normal_icon)
        # self.setIconSize(QSize(16, 16))
        super().leaveEvent(event)

# 自定义样式按钮
class Style1Button(HighlightButton):
    def __init__(self, text, size, dark_icon_path,light_icon_path, parent=None):
        super().__init__(text, size, dark_icon_path,light_icon_path, parent)
        self.setFixedSize(38, 38)
        self.setStyleSheet("background: transparent; border: none;")
        
class Style2Button(HighlightButton):
    def __init__(self, text, size, dark_icon_path,light_icon_path, parent=None):
        super().__init__(text, size, dark_icon_path,light_icon_path, parent)
        self.setFixedSize(38, 38)
        self.setStyleSheet("background-color:#232328 ; border-radius: 19px; border: none;")

#  
class HomepageButton(HighlightButton):
    def __init__(self, text, size, dark_icon_path,light_icon_path, parent=None):
        super().__init__(text, size, dark_icon_path,light_icon_path, parent)
        self.setFixedSize(110, 30)
        font = QFont('Microsoft YaHei', 9, QFont.Normal)
        self.setFont(font)
        self.setStyleSheet("padding-left:5px;padding-right:5px; color:white;background-color:#232328 ;border-radius: 15px; border: none;")
    
    def enterEvent(self, event):
        self.setStyleSheet("padding-left:5px;padding-right:5px; color:#D54B2A ;background-color:#232328 ;border-radius: 15px; border: none;")
        return super().enterEvent(event)
    def leaveEvent(self, event):
        self.setStyleSheet("padding-left:5px;padding-right:5px; color:white;background-color:#232328 ;border-radius: 15px; border: none;")
        return super().leaveEvent(event)

class PintotopButton(Style1Button):
    def __init__(self, text, size, dark_icon_path, light_icon_path, parent=None):
        super().__init__(text, size, dark_icon_path, light_icon_path, parent)
        
    def set_icon_path(self, dark_icon_path, light_icon_path,):
        self.normal_icon = QIcon(dark_icon_path)
        self.highlight_icon = QIcon(light_icon_path)       
class VideoSlider(QSlider):
    def __init__(self, parent=None):
        super(VideoSlider, self).__init__(Qt.Horizontal, parent)
        self.setRange(0, 100)
        self.setValue(0)
        self.setToolTipDuration(0)  # 关闭默认的工具提示
        self.setContentsMargins(0, 0, 0, 0)
        # 鼠标点击时8px
        # 平滑过渡问题 to do
        # 实现滑条襄在视频界面里 to do
        self.setStyleSheet("""  
            QSlider::groove:horizontal {  
                height: 4px;  
                background: #a8a8a8; 
                margin-top: 4px; 
            }  
            QSlider::groove:horizontal:hover {  
                height: 8px;
                background: #a8a8a8; 
                margin-top: 2px; 
            }
            QSlider::handle:horizontal {  
                image: url("./icons/circle.png");
                width: 15px;
                height: 15px;  
                margin: -7.5px -7.5px;      
            }  
            QSlider::handle:horizontal:hover { 
                image: url("./icons/circle.png"); 
                width: 20px;
                height: 20px;  
                margin: -10px -10px;  
            }          
            QSlider::sub-page:horizontal {  
                background: #D54B2A;
                height: 4px;  
            }
            QSlider::add-page:horizontal {  
                background: #a8a8a8;  
                height: 4px;
            }  
        """) 

    def enterEvent(self, event):
        # 鼠标变小手
        self.setCursor(QCursor(Qt.PointingHandCursor))
        super(VideoSlider,self).enterEvent(event)
        pass
    def leaveEvent(self, event):
        self.setCursor(QCursor(Qt.ArrowCursor))
        super(VideoSlider,self).leaveEvent(event)
        pass
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            opt = self.style().subControlRect(self.style().CC_Slider, QStyleOptionSlider(), QStyle.SC_SliderHandle, self)
            if not opt.contains(event.pos()):
                value = QStyle.sliderValueFromPosition(self.minimum(), self.maximum(), event.x(), self.width())
                self.setValue(value)
                self.sliderMoved.emit(value)
                # 模拟释放事件以触发 sliderReleased, 确保跳转并恢复播放
                self.mouseReleaseEvent(event)  
        super(VideoSlider, self).mousePressEvent(event)
        
class CustomSlider(QSlider):
    def __init__(self, orientation,parent=None):
        super(CustomSlider, self).__init__(orientation,parent)
        self._is_dragging = False
        self.setRange(0, 100)
        self.setValue(50)
        self.setToolTipDuration(0)  # 关闭默认的工具提示
        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("""  
            QSlider::groove:vertical {  
                width: 4px;  
                background: #a8a8a8; 
            }  
            QSlider::groove:vertical:hover {  
                width: 6px;
                background: #a8a8a8;  
            }
            QSlider::handle:vertical { 
                image: url("./icons/circle_light.png"); 
                width: 15px;
                height: 15px;  
                margin: -7.5px -7.5px;  
            }
            QSlider::sub-page:vertical {
                width: 4px;
                background: #a8a8a8;
            }
            QSlider::add-page:vertical {
                width: 4px;
                background: #ffffff;
            }  
        """)
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            opt = QStyleOptionSlider()
            handle_rect = self.style().subControlRect(self.style().CC_Slider, opt, self.style().SC_SliderHandle, self)
            self._is_dragging = True
            slider_length = handle_rect.height()  # 注意这里应该是高度
            slider_min = self.minimum()
            slider_max = self.maximum()
            slider_range = slider_max - slider_min
            new_value = slider_range * (self.height() - event.y()) / (self.height() - slider_length)
            self.setValue(slider_min + int(new_value))
            self.valueChanged.emit(self.value())
        super(CustomSlider, self).mousePressEvent(event)
    def mouseMoveEvent(self, event: QMouseEvent):
        if self._is_dragging:
            opt = QStyleOptionSlider()
            handle_rect = self.style().subControlRect(self.style().CC_Slider, opt, self.style().SC_SliderHandle, self)
            slider_length = handle_rect.height()  # 注意这里应该是高度
            slider_min = self.minimum()
            slider_max = self.maximum()
            slider_range = slider_max - slider_min
            new_value = slider_range * (self.height() - event.y()) / (self.height() - slider_length)
            self.setValue(slider_min + int(new_value))
            self.valueChanged.emit(self.value())
        super(CustomSlider, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._is_dragging = False
        super(CustomSlider, self).mouseReleaseEvent(event)
    def enterEvent(self, event):
        self.setCursor(QCursor(Qt.PointingHandCursor))
        super(CustomSlider,self).enterEvent(event)
    def leaveEvent(self, event):
        self.setCursor(QCursor(Qt.ArrowCursor))
        super(CustomSlider,self).leaveEvent(event)
        
# 音量组件
class VolumeSlider(QWidget):
    volumeChanged = pyqtSignal(int)
    def __init__(self, parent=None):
        super(VolumeSlider, self).__init__(parent)
        self.is_on_hover = False
        self.init_volume_slider()
        self.init_ui()
    def init_ui(self):
        self.setFixedHeight(200)
        self.setFixedWidth(70)
        self.setAttribute(Qt.WA_TranslucentBackground)
        # 关闭标题栏
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(46, 46, 54, 0);
            }
        """)

        self.volume_message_label = QLabel(str(self.volume_slider.value()))
        font = QFont("Microsoft YaHei", 10)  # 设置字体为等线体，字号为10
        self.volume_message_label.setFont(font)
        self.volume_message_label.setAlignment(Qt.AlignCenter)  # 居中对齐
        self.volume_message_label.setStyleSheet("color: white;")  # 设置文字颜色为白色
        
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        
        widget = QWidget()
        layout = QHBoxLayout()
        layout.addWidget(self.volume_slider)
        widget.setLayout(layout)
        
        self.main_layout.addWidget(self.volume_message_label)
        self.main_layout.addWidget(widget)
    def init_volume_slider(self):
        self.volume_slider = CustomSlider(Qt.Vertical)
        self.volume_slider.setFixedWidth(15)
        self.volume_slider.valueChanged.connect(self.set_volume)
    
    # 绘制圆角
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(QBrush(QColor(46, 46, 54, 220)))
        painter.setPen(QPen(Qt.transparent))
        painter.drawRoundedRect(self.rect(), 15, 15)
        super(VolumeSlider, self).paintEvent(event)
    def set_volume(self, value):
        self.volume_message_label.setText(str(value))
        self.volumeChanged.emit(value)
    
    def enterEvent(self, event):
        self.is_on_hover = True
        self.setVisible(True)
        super(VolumeSlider,self).enterEvent(event)
    
    def leaveEvent(self, event):
        self.is_on_hover = False
        self.setVisible(False)
        super(VolumeSlider,self).leaveEvent(event)
        
              
# VideoControllBar 按钮
class DanmukuButton(HighlightButton):  
    def __init__(self, text, size, dark_icon_path, light_icon_path, parent=None):
        super().__init__(text, size, dark_icon_path, light_icon_path, parent)
        self.setFixedSize(70, 30)
        font = QFont('Microsoft YaHei', 9, QFont.Normal)
        self.setFont(font)
        self.setStyleSheet("padding-left:0px;padding-right:10px; color:white;background-color:#232328 ;border-radius: 15px; border: none;")
    
    def enterEvent(self, event):
        self.setStyleSheet("padding-left:0px;padding-right:10px; color:white;background-color:#232328 ;border-radius: 15px; border: none;background-color:#202026 ;")
        return super().enterEvent(event)
    
    def leaveEvent(self, event):
        self.setStyleSheet("padding-left:0px;padding-right:10px; color:white;background-color:#232328 ;border-radius: 15px; border: none;background-color:#232328 ;")
        return super().leaveEvent(event)
class WriteDanmukuButton(QPushButton):
    def __init__(self, text, size, icon_path, parent=None):
        super().__init__(text, parent)
        self.setFixedSize(100, 30)
        self.setIcon(QIcon(icon_path))
        self.setIconSize(QSize(size, size))
        font = QFont('Microsoft YaHei', 9, QFont.Normal)
        self.setFont(font)
        self.setStyleSheet("padding-left:5px;padding-right:5px; color:rgba(252,255,255,0.5);background-color:#232328 ;border-radius: 15px; border: none;")
    
    def enterEvent(self, event):
        self.setStyleSheet("padding-left:5px;padding-right:5px; color:white ;background-color:#232328 ;border-radius: 15px; border: none;")
        self.setCursor(QCursor(Qt.PointingHandCursor))
        return super().enterEvent(event)
    def leaveEvent(self, event):
        self.setStyleSheet("padding-left:5px;padding-right:5px; color:rgba(252,255,255,0.5);background-color:#232328 ;border-radius: 15px; border: none;")
        return super().leaveEvent(event)
class SetupButton(HighlightButton):
    def __init__(self, text, size, dark_icon_path, light_icon_path, parent=None):
        super().__init__(text, size, dark_icon_path, light_icon_path, parent)
        self.setFixedSize(38, 38)
        self.setStyleSheet("background: transparent; border: none;")
class VolumeButton(HighlightButton):
    def __init__(self, text, size, dark_icon_path, light_icon_path, parent=None):
        super().__init__(text, size, dark_icon_path, light_icon_path, parent)
        self.init_volume_slider()
        self.setFixedSize(38, 38)
        self.setStyleSheet("background: transparent; border: none;")
        # self.clicked.connect(self.set_silence)
    def init_volume_slider(self):
        self.volume_slider = VolumeSlider()
        self.volume_slider.setVisible(False)
        pass
        
    def enterEvent(self, event):
        # 设置可见
        self.volume_slider.setVisible(True)
        
        # 局部坐标转为全局坐标
        button_pos = self.mapToGlobal(self.pos())
        self.volume_slider.move(button_pos.x() - 60, button_pos.y() - 250)
        # 设置2s时间
        timer = QTimer(self)
        timer.singleShot(1000, self.hide_slider)
        
        return super().enterEvent(event)
    # def set_silence(self):
    #     self.current_volume = self.volume_slider.volume_slider.value()
    #     if self.current_volume != 0:
    #         self.volume_slider.volume_slider.setValue(0)
    #         self.previous_volume = self.current_volume
    #     else:
    #         self.volume_slider.volume_slider.setValue(self.previous_volume)
    def hide_slider(self):
        if self.volume_slider.is_on_hover == False:
            self.volume_slider.setVisible(False)
class FullScreenButton(HighlightButton):
    def __init__(self, text, size, dark_icon_path, light_icon_path, parent=None):
        super().__init__(text, size, dark_icon_path, light_icon_path, parent)
        self.setFixedSize(38, 38)
        self.setStyleSheet("background: transparent; border: none;") 
        timer = QTimer()
        #每100ms刷新图标
        timer.timeout.connect(self.update_icon)
        timer.start(100)
          
    def update_icon(self):
        if self.mouse_in_button:
            self.setIcon(self.highlight_icon)
        else:
            self.setIcon(self.normal_icon)
    def set_icon_path(self, dark_icon_path, light_icon_path,):
        self.normal_icon = QIcon(dark_icon_path)
        self.highlight_icon = QIcon(light_icon_path)
                
class PlayButton(Style1Button):
    def __init__(self, text, size, dark_icon_path, light_icon_path, parent=None):
        super().__init__(text, size, dark_icon_path, light_icon_path, parent)
        self.setFixedSize(38, 38)
        self.setStyleSheet("background: transparent; border: none;")
        self.mouse_in_button = False
         # 创建定时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_icon)
        self.timer.start(100)  # 每100毫秒检查一次
    def set_icon_path(self, dark_icon_path, light_icon_path,):
        self.normal_icon = QIcon(dark_icon_path)
        self.highlight_icon = QIcon(light_icon_path)
    def enterEvent(self, event):
        self.mouse_in_button = True
        return super().enterEvent(event)
    
    def leaveEvent(self, event):
        self.mouse_in_button = False
        return super().leaveEvent(event)
    
    def update_icon(self):
        if self.mouse_in_button:
           current_icon = self.highlight_icon
        else:
           current_icon = self.normal_icon
        self.setIcon(current_icon)

class VideoMediaControllerBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        
    def initUI(self):
        # 设置窗口属性
        self.setFixedHeight(75)
        self.setStyleSheet("background-color: #2E2E36;")
        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        
        self.play_button = PlayButton("", 25, "./icons/play_dark.png","./icons/play_light.png" )
        self.next_button = Style1Button("", 20, "./icons/next_dark.png","./icons/next_light.png" )
        self.danmuku_button = DanmukuButton("  弹", 8, "./icons/danmuku_dark.png","./icons/danmuku_light.png" )
        self.write_danmuku_button = WriteDanmukuButton("  发弹幕", 16, "./icons/danmuku_write.png")
        
        widget1 = QWidget()
        widget1.setFixedHeight(75)
        widget1.setFixedWidth(200)
        layout1 = QHBoxLayout()
        widget1.setLayout(layout1)
        layout1.setContentsMargins(0, 0, 0, 0)
        layout1.addWidget(self.play_button)
        layout1.addWidget(self.next_button)
        layout1.addWidget(self.danmuku_button)
      
        self.setup_button = SetupButton("", 22, "./icons/setup_dark.png","./icons/setup_light.png" )
        self.volume_button = VolumeButton("", 28, "./icons/volume_dark.png","./icons/volume_light.png" )
        self.fullscreen_button = FullScreenButton("", 22, "./icons/fullscreen_dark.png","./icons/fullscreen_light.png" )
        
        widget2 = QWidget()
        layout2 = QHBoxLayout()
        widget2.setLayout(layout2)
        widget2.setFixedHeight(75)
        widget2.setFixedWidth(120)
        layout2.setContentsMargins(0, 0, 0, 0)
        layout2.addWidget(self.setup_button)
        layout2.addWidget(self.volume_button)
        layout2.addWidget(self.fullscreen_button)
        
        self.main_layout.addWidget(widget1, Qt.AlignLeft)
        self.main_layout.addWidget(QWidget())
        self.main_layout.addWidget(widget2, Qt.AlignRight)
        
        self.setLayout(self.main_layout)
        pass
class VideoPlayerBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        
    def initUI(self):
        # 设置窗口属性
        self.setFixedHeight(50)
        self.setStyleSheet("background-color: #2E2E36;")
        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.main_layout)

        # 右侧功能按钮
        self.maximize_button = Style1Button("",16,"./icons/maximize_dark.png","./icons/maximize_light.png")
        self.close_button = Style1Button("",16,"./icons/close_dark.png","./icons/close_light.png")
        self.minimize_button = Style1Button("",16,"./icons/minimize_dark.png","./icons/minimize_light.png")
        self.pintotop_button = PintotopButton("",21,"./icons/pintotop1_dark.png","./icons/pintotop1_light.png")
        self.simplify_button = Style1Button("",21,"./icons/simplify_dark.png","./icons/simplify_light.png")
        
        # 中间功能按钮
        self.download_button = Style2Button("",20,"./icons/download_dark.png","./icons/download_light.png")
        self.others_button = Style2Button("",18,"./icons/others_dark.png","./icons/others_light.png")
        self.follow_button = Style2Button("",18,"./icons/follow_dark.png","./icons/follow_light.png")
        self.share_button = Style2Button("",18,"./icons/share_dark.png","./icons/share_light.png")
        self.phone_button = Style2Button("",20,"./icons/phone_dark.png","./icons/phone_light.png")
        
        # 临时widget,用于居中右侧功能模块
        widget1 = QWidget()
        layout1 = QHBoxLayout()
        layout1.setContentsMargins(0, 0, 0, 0)
        widget1.setLayout(layout1)
        layout1.addWidget(self.simplify_button)
        layout1.addWidget(self.pintotop_button)
        layout1.addWidget(self.minimize_button)
        layout1.addWidget(self.maximize_button)
        layout1.addWidget(self.close_button)
        widget1.setFixedHeight(50)
        widget1.setFixedWidth(240)
        
        # 临时widget,用于居中中间功能模块
        widget2 = QWidget()
        layout2 = QHBoxLayout()
        layout2.setContentsMargins(0, 0, 0, 0)
        layout2.addWidget(self.follow_button)
        layout2.addWidget(self.download_button)
        layout2.addWidget(self.phone_button)
        layout2.addWidget(self.share_button)
        layout2.addWidget(self.others_button)
        widget2.setLayout(layout2)
        widget2.setFixedHeight(50)
        widget2.setFixedWidth(265)
        
        # 添加消息显示控件
        self.message_label = QLabel("斗罗大陆Ⅱ绝世唐门 第001话")
        # 设置标签的字体
        font = QFont('Microsoft YaHei', 12, QFont.Normal)
        self.message_label.setFont(font)
        self.message_label.setStyleSheet("color: white;")
        
        # 添加打开主界面控件
        self.homepage_button = HomepageButton("打开主界面",18,"./icons/homepage_dark.png","./icons/homepage_light.png")
        
        # 添加到main_layout并设置间距
        self.main_layout.addStretch(1)
        self.main_layout.addWidget(self.homepage_button)
        self.main_layout.addStretch(10)
        self.main_layout.addWidget(self.message_label)
        self.main_layout.addStretch(2)
        self.main_layout.addWidget(widget2)
        self.main_layout.addStretch(7)
        self.main_layout.addWidget(widget1, alignment=Qt.AlignRight)
class VideoMediaController(QWidget):
    screenChanged = pyqtSignal(bool)
    def __init__(self, parent=None):
        super(VideoMediaController,self).__init__(parent)
        
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.video_widget = QVideoWidget()
        self.video_slider = VideoSlider()
        self.video_bar = VideoMediaControllerBar() 
        
        self.init_ui()
        self.init_media_player()
        
        # self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile("1.mp4")))
        # self.media_player.play()
    def init_ui(self):
        # 创建主窗口的主布局
        self.resize(1080, 720)
        self.setStyleSheet("background-color: #2E2E36;")
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)  # 设置布局的边距为0
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)
        
        self.video_widget.setStyleSheet("background-color: black;")
        
        self.main_layout.addWidget(self.video_widget)
        self.main_layout.addWidget(self.video_slider)
        self.main_layout.addWidget(self.video_bar)
        
        # 设置按钮关联
        self.video_bar.fullscreen_button.clicked.connect(self.toggle_fullscreen)
        self.video_bar.volume_button.volume_slider.volumeChanged.connect(self.set_volume)
        self.video_bar.play_button.clicked.connect(self.toggle_play_pause)
        self.video_slider.sliderMoved.connect(self.set_position)
        self.video_slider.sliderPressed.connect(self.pause_on_slider_press)
        self.video_slider.sliderReleased.connect(self.resume_on_slider_release)
    def init_media_player(self):
        self.media_player.setVideoOutput(self.video_widget)
        self.media_player.stateChanged.connect(self.media_state_changed)
        self.media_player.positionChanged.connect(self.position_changed)
        self.media_player.durationChanged.connect(self.duration_changed)

        # 定时更新进度条
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_slider)
        self.timer.start()
    def toggle_fullscreen(self):
        self.screenChanged.emit(True)
    def set_volume(self, volume):
        self.media_player.setVolume(volume)
    def set_position(self, position):
        self.media_player.setPosition(position)
    def pause_on_slider_press(self):
        self.media_player.pause()
    def resume_on_slider_release(self):
        if self.media_player.state() == QMediaPlayer.PausedState:
            self.media_player.play()
    def position_changed(self, position):
        self.video_slider.setValue(position)
    def duration_changed(self, duration):
        self.video_slider.setRange(0, duration)
    def media_state_changed(self, state):
        if state == QMediaPlayer.PlayingState:
            self.video_bar.play_button.set_icon_path("./icons/play_on_dark.png","./icons/play_on_light.png")
        else:
            self.video_bar.play_button.set_icon_path("./icons/play_dark.png","./icons/play_light.png")
    def load_video(self, video_path):
        self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(video_path)))
        self.media_player.play()
    def update_slider(self):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.video_slider.setValue(self.media_player.position())
    def toggle_play_pause(self):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()         
    
class VideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        # 创建自定义工具栏
        self.init_toolbar()
        # 创建视频播放窗口
        self.init_videoplayer()
        self.main_layout.addWidget(self.toolbar)
        self.main_layout.addWidget(self.video_player)
        
    def init_ui(self):
        self.setWindowTitle("简易流媒体播放器")
        self.setGeometry(200, 200, 1280, 706)
        
        # 创建主窗口的中心部件
        self.central_widget = QWidget()
        self.central_widget.setStyleSheet("background-color: #2E2E36;")
        self.setCentralWidget(self.central_widget)
        # 创建主窗口的主布局
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)  # 设置布局的边距为0
        self.main_layout.setSpacing(0)
        self.central_widget.setLayout(self.main_layout)

        # 关闭标题栏
        self.setWindowFlags(Qt.FramelessWindowHint)
    def init_toolbar(self):
        self.toolbar = VideoPlayerBar()
        # 连接按钮的点击信号
        self.toolbar.close_button.clicked.connect(self.close_window)
        self.toolbar.maximize_button.clicked.connect(self.maximize_window)
        self.toolbar.minimize_button.clicked.connect(self.minimize_window)
        self.toolbar.pintotop_button.clicked.connect(self.pintotop1_window)
        self.toolbar.simplify_button.clicked.connect(self.simplify_window)
        self.toolbar.download_button.clicked.connect(self.download_vedio)
        self.toolbar.others_button.clicked.connect(self.others_vedio)
        self.toolbar.follow_button.clicked.connect(self.follow_vedio)
        self.toolbar.share_button.clicked.connect(self.share_vedio)
        self.toolbar.phone_button.clicked.connect(self.phone_vedio)
        pass
    def init_videoplayer(self):
        self.video_player = VideoMediaController()
        self.video_player.screenChanged.connect(self.full_screen)
    def full_screen(self):
        if self.isFullScreen():
            self.showNormal()
            self.video_player.video_bar.fullscreen_button.set_icon_path("./icons/fullscreen_dark.png","./icons/fullscreen_light.png")
        else:
            self.showFullScreen()
            self.video_player.video_bar.fullscreen_button.set_icon_path("./icons/minscreen_dark.png","./icons/minscreen_light.png")
            
    # 关闭窗口
    def close_window(self):
        self.video_player.media_player.stop()
        self.close()
    # 最大化窗口
    def maximize_window(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
        pass
    # 最小化窗口
    def minimize_window(self):
        self.showMinimized()
    # 置顶窗口
    def pintotop1_window(self):
        # 保存当前窗口状态
        current_geometry = self.geometry()
        self.is_stay_on_top = True
        # 更新图标
        self.toolbar.pintotop_button.set_icon_path("./icons/pintotop2_dark.png","./icons/pintotop2_light.png")
        self.toolbar.pintotop_button.clicked.disconnect(self.pintotop1_window)
        self.toolbar.pintotop_button.clicked.connect(self.pintotop2_window)
        # 设置窗口置顶
        self.setWindowFlags(Qt.WindowStaysOnTopHint|Qt.FramelessWindowHint)
        self.setGeometry(current_geometry)
        
        self.show()
    # 取消置顶
    def pintotop2_window(self):
        # 保存当前窗口状态
        current_geometry = self.geometry()
        self.is_stay_on_top = False
        # 更新图标
        self.toolbar.pintotop_button.set_icon_path("./icons/pintotop1_dark.png","./icons/pintotop1_light.png")
        self.toolbar.pintotop_button.clicked.disconnect(self.pintotop2_window)
        self.toolbar.pintotop_button.clicked.connect(self.pintotop1_window)
        # 设置窗口
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setGeometry(current_geometry)
      
        self.show()
    def download(self, bvid):
        download_thread = threading.Thread(target=start_download, args=(bvid, "temp.mp4", self.on_download_complete))
        download_thread.start()
    
    def on_download_complete(self, path):
        self.load_video("./video.mp4")
    def load_video(self, video_path):
        self.video_player.load_video(video_path)

    # 窗口精简模式
    def simplify_window(self):
        pass   
    def download_vedio(self):
        pass
    def others_vedio(self):
        pass
    def follow_vedio(self):
        pass
    def share_vedio(self):
        pass
    def phone_vedio(self):
        pass
    def homepage(self):
        pass
    # 实现窗口拖动
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_position is not None:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = None
            event.accept()

class VideoPlayerManager:
    _instance = None
    _player_window = None
    
    @classmethod
    def get_instance(cls):
        """获取或创建播放器窗口实例"""
        if cls._player_window is None or not cls._player_window.isVisible():
            cls._player_window = VideoPlayer()
        return cls._player_window


# if __name__ == "__main__":
    
#     app = QApplication(sys.argv)
#     player = VideoPlayerManager.get_instance()
#     player.download("BV1UW4y1N79w")
#     player.show()

#     # 加载一个示例视频 URL
#     # video_url = "https://example.com/path/to/your/video.mp4"  # 替换为实际的视频 URL
#     # player.load_video(video_url)

#     sys.exit(app.exec_())
