import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QListWidget, 
                           QLineEdit, QScrollArea, QSizePolicy, QButtonGroup, 
                           QStackedWidget, QGridLayout, QSpacerItem)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QEvent, QTimer, pyqtSignal
from search_function import show_search_results, ThumbnailLoader  # 导入搜索功能的函数
from  videoplayer import VideoPlayer
from bilibili_api import search, sync
from videoplayer import VideoPlayerManager

class VideoRecommendation(QWidget):
    """
    视频推荐卡片组件类
    用于显示单个视频推荐，包含海报图片、标题和描述
    """
    RECOMMENDED_WIDTH = 300
    RECOMMENDED_HEIGHT = 180

    def __init__(self, image_path, title, description):
        """
        初始化视频推荐卡片
        
        参数:
            image_path (str): 海报图片路径
            title (str): 视频标题
            description (str): 视频描述
        """
        super().__init__()
        self.image_path = image_path
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        layout.setContentsMargins(5, 5, 5, 5)

        # 创建海报容器
        self.poster_container = QWidget()
        self.poster_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.poster_container.setFixedSize(self.RECOMMENDED_WIDTH, self.RECOMMENDED_HEIGHT * 9 // 16)
        poster_layout = QVBoxLayout(self.poster_container)
        poster_layout.setContentsMargins(0, 0, 0, 0)

        # 创建并设置海报图片标签
        self.poster = QLabel()
        self.poster.setScaledContents(True)
        self.poster.setAlignment(Qt.AlignCenter)
        poster_layout.addWidget(self.poster)

        # 创建并设置标题和描述标签
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: white;")
        title_label.setWordWrap(True)
        
        desc_label = QLabel(description)
        desc_label.setStyleSheet("font-size: 12px; color: #aaaaaa;")
        desc_label.setWordWrap(True)

        # 将所有元素添加到布局中
        layout.addWidget(self.poster_container)
        layout.addWidget(title_label)
        layout.addWidget(desc_label)

        # 设置卡片的鼠标样式和悬停效果
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                border-radius: 5px;
            }
            QWidget:hover {
                background-color: #2a2a2a;
            }
        """)

        # 初始加载图片
        self.update_poster()

    def update_poster(self):
        """更新海报图片，保持16:9比例"""
        # 获取容器当前宽度
        container_width = self.poster_container.width()
        # 计算16:9比例的高度
        container_height = int(container_width * 9 / 16)
        
        # 加载并缩放图片
        pixmap = QPixmap(self.image_path)
        scaled_pixmap = pixmap.scaled(
            container_width,
            container_height,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        
        # 更新海报标签
        self.poster.setPixmap(scaled_pixmap)
        # 设置固定高度保持比例
        self.poster_container.setFixedHeight(container_height)

    def mousePressEvent(self, event):
        """处理鼠标点击事件"""
        if event.button() == Qt.LeftButton:
            player_manager = VideoPlayerManager.get_instance()
            player_manager.load_video("1.mp4")
            player_manager.show()  # 确保显示播放器
            print(f"Playing video from: {self.image_path}")

class VideoRecommendationCard(QWidget):
    def __init__(self, thumbnail_url, video_name, video_author, video_date, bvid, thumbnail_loader):
        super().__init__()
        self.bvid = bvid
        self.thumbnail_url = thumbnail_url
        self.card_id = str(id(self))
        self.thumbnail_loader = thumbnail_loader
        self.video_name = video_name

        self.setStyleSheet(""" 
        QWidget {
            background-color: transparent;
            border-radius: 5px;
        }
        QWidget:hover {
            background-color: #2a2a2a;
        }
        """)
        
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(5, 5, 5, 5)

        # 创建缩略图标签
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setScaledContents(True)
        self.thumbnail_label.setFixedSize(320, 180)
        
        # 使用占位图
        self.thumbnail_label.setText("加载中...")
        
        # 标题标签
        self.name_label = QLabel(video_name)
        self.name_label.setStyleSheet(""" 
            font-size: 14px;
            font-weight: bold;
            color: white;
            padding: 5px;
        """)
        self.name_label.setWordWrap(True)
        self.name_label.setFixedHeight(60)
        
        # 作者和日期标签
        author_label_text = f"作者: {video_author}"
        self.author_label = QLabel(author_label_text)
        self.author_label.setStyleSheet(""" 
            font-size: 12px;
            color: #aaaaaa;
            padding: 5px;
        """)
        self.author_label.setFixedHeight(30)

        # 新增日期标签
        self.date_label = QLabel(video_date)
        self.date_label.setStyleSheet(""" 
            font-size: 12px;
            color: #aaaaaa;
            padding: 5px;
        """)
        self.date_label.setFixedHeight(30)

        # 创建一个水平布局以放置作者和日期
        h_layout = QHBoxLayout()
        h_layout.addWidget(self.author_label)
        h_layout.addWidget(self.date_label)

        self.setCursor(Qt.PointingHandCursor)

        self.layout.addWidget(self.thumbnail_label)
        self.layout.addWidget(self.name_label)
        self.layout.addLayout(h_layout)  # 添加水平布局
        
    def load_thumbnail(self):
        """请求加载缩略图"""
        self.thumbnail_loader.add_task(self.thumbnail_url, self.card_id)
        
    def set_thumbnail(self, pixmap):
        """设置缩略图"""
        self.thumbnail_label.setPixmap(pixmap)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            print(f"Playing video: {self.bvid}")
            player_manager = VideoPlayerManager.get_instance()
            player_manager.download(self.bvid)
            player_manager.toolbar.message_label.setText(self.video_name)
            player_manager.show()  # 确保显示播放器


class SearchResultsManager:
    def __init__(self, parent):
        self.parent = parent
        self.thumbnail_loader = ThumbnailLoader()
        self.thumbnail_loader.thumbnail_loaded.connect(self.on_thumbnail_loaded)
        self.thumbnail_loader.start()
        self.cards = {}  # 存储卡片引用
        
    def on_thumbnail_loaded(self, card_id, pixmap):
        """当缩略图加载完成时更新UI"""
        if card_id in self.cards:
            self.cards[card_id].set_thumbnail(pixmap)
            
    def handle_search(self, search_text):
        """处理搜索请求"""
        self.clear_search_results()
        
        video_data = show_search_results(search_text)
        
        grid = QGridLayout()
        grid.setSpacing(10)
        grid.setContentsMargins(5, 5, 5, 5)
        
        for i, video in enumerate(video_data):
            self.card = VideoRecommendationCard(
                video['thumbnail_url'],
                video['name'],
                video['author'],
                video['pubdate'],  # 添加日期参数
                video['bvid'],
                self.thumbnail_loader
            )
            self.cards[self.card.card_id] = self.card
            grid.addWidget(self.card, i // 4, i % 4)
            
            QTimer.singleShot(i * 100, self.card.load_thumbnail)
        
        grid_widget = QWidget()
        grid_widget.setLayout(grid)
        grid_widget.setMinimumHeight(600)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(grid_widget)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.parent.search_results_layout.addWidget(scroll_area)
        self.parent.content_stack.setCurrentWidget(self.parent.search_page)
        
    def clear_search_results(self):
        """清除旧的搜索结果"""
        self.cards.clear()
        for i in reversed(range(self.parent.search_results_layout.count())):
            widget_to_remove = self.parent.search_results_layout.takeAt(i).widget()
            if widget_to_remove is not None:
                widget_to_remove.deleteLater()

        
class TencentVideoClone(QMainWindow):
    """
    腾讯视频客户端克隆应用的主窗口类
    实现了主要的UI界面和交互功能
    
    包含:
    - 顶部导航栏（搜索、历史记录等）
    - 左侧菜单栏
    - 主要内容区（轮播图、视频推荐等）
    """
    def __init__(self):
        """
        初始化主窗口
        设置基本窗口属性并创建所有UI元素
        """
        super().__init__()
        self.search_manager = SearchResultsManager(self)
        self.player = VideoPlayer()
        
        # 隐藏窗口自带的按钮
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)

        # 基本窗口设置
        self.setWindowTitle("Tencent Video Clone")
        self.setGeometry(50, 50, 1600, 900)
        self.setMinimumSize(800, 600)

        # 创建主布局    
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # === 创建顶部栏 ===
        top_bar = QWidget()
        top_layout = QHBoxLayout(top_bar)
        top_bar.setStyleSheet("background-color: transparent;")  # 设置任务栏背景为透明
        top_bar.setFixedHeight(50)

        # 创建Logo
        logo_label = QLabel()
        logo_label.setPixmap(QIcon("icons/tencentvideo_icon.png").pixmap(32, 32))
        logo_label.setStyleSheet("padding-left: 10px;")

        logo_text = QLabel("Tencent Video")
        logo_text.setStyleSheet("font-size: 24px; font-weight: bold; color: white; padding-left: 10px;")

        # 创建搜索框
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("搜索")
        self.search_bar.setFixedWidth(400)
        self.search_bar.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                font-size: 18px;
                border-radius: 10px;
                border: 1px solid #555;
            }
        """)

        # 连接回车按键信号到槽函数
        self.search_bar.returnPressed.connect(self.handle_search)

        # 创建顶部功能按钮
        history_button = QPushButton()
        download_button = QPushButton()
        login_button = QPushButton()

        history_button.setIcon(QIcon("icons/history_icon.png"))
        download_button.setIcon(QIcon("icons/download_icon.png"))
        login_button.setIcon(QIcon("icons/user_icon.png"))

        # 设置按钮统一样式
        button_style = """
            QPushButton {
                font-size: 16px;
                padding: 10px;
                color: white;
                background-color: transparent;  /* 按钮背景透明 */
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);  /* 鼠标悬停时按钮高亮 */
            }
        """
        for button in [history_button, download_button, login_button]:
            button.setStyleSheet(button_style)

        # 创建最小化、最大化和关闭按钮
        minimize_button = QPushButton()
        maximize_button = QPushButton()
        close_button = QPushButton()

        minimize_button.setIcon(QIcon("icons/minimize_icon.png"))
        maximize_button.setIcon(QIcon("icons/maximize_icon.png"))
        close_button.setIcon(QIcon("icons/close_icon.png"))

        minimize_button.clicked.connect(self.showMinimized)
        maximize_button.clicked.connect(self.toggle_maximize)
        close_button.clicked.connect(self.close)

        button_style = """
            QPushButton {
                font-size: 16px;
                padding: 10px;
                color: white;
                background-color: transparent;  /* 按钮背景透明 */
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);  /* 鼠标悬停时按钮高亮 */
            }
        """
        for button in [minimize_button, maximize_button, close_button]:
            button.setStyleSheet(button_style)

        # 组织顶部栏布局
        top_layout.addWidget(logo_label)
        top_layout.addWidget(logo_text)
        top_layout.addStretch()
        top_layout.addWidget(self.search_bar)
        top_layout.addStretch()
        top_layout.addWidget(history_button)
        top_layout.addWidget(download_button)
        top_layout.addWidget(login_button)
        top_layout.addStretch()
        top_layout.addWidget(minimize_button)
        top_layout.addWidget(maximize_button)
        top_layout.addWidget(close_button)

        # 确保按钮高度一致
        for widget in [logo_label, logo_text, self.search_bar, history_button, download_button, login_button, minimize_button, maximize_button, close_button]:
            widget.setFixedHeight(40)  # 设置固定高度

        # 将顶部栏添加到主布局
        main_layout.addWidget(top_bar)  # 添加顶部栏到主布局

        # === 创建主内容区域 ===
        content_area = QWidget()
        content_layout = QHBoxLayout(content_area)

        # 创建左侧导航栏
        nav_bar = QListWidget()
        nav_bar.addItems(["首页", "VIP会员", "电视剧", "电影", "综艺", "动漫", 
                         "少儿", "NBA", "纪录片", "短剧", "体育", "科技", "音乐"])
        nav_bar.setMaximumWidth(200)
        nav_bar.setStyleSheet("""
            QListWidget {
                background-color: #1c1c1c;
                border: none;
                font-size: 20px;
            }
            QListWidget::item {
                color: #bfbfbf;
                padding: 13px 10px;
                font-size: 20px;
            }
            QListWidget::item:hover {
                color: #ffffff;
                background-color: #333333;
            }
            QListWidget::item:selected {
                background-color: transparent;
                color: #0078d7;
                outline: none;
            }
            QListWidget::item:selected:hover {
                background-color: #333333;
                color: #0078d7;
            }
            QListWidget::item:focus {
                outline: none;
            }
        """)

        # === 创建右侧内容区 ===
        # 使用QStackedWidget替代原来的QScrollArea
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("QStackedWidget { border: none; background-color: #000000; }")
        
        # 创建主页内容页
        self.home_page = QScrollArea()
        self.home_page.setWidgetResizable(True)
        self.home_page.setStyleSheet("QScrollArea { border: none; background-color: #000000; }")
        
        home_content = QWidget()
        home_layout = QVBoxLayout(home_content)
        home_layout.setContentsMargins(0, 0, 0, 0)

        # 创建大封面区域
        self.large_cover = QLabel("大封面")
        self.large_cover.setAlignment(Qt.AlignCenter)
        self.large_cover.setStyleSheet("QLabel { border: 2px solid #555; background-color: #1c1c1c; }")
        self.large_cover.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.large_cover.setMinimumSize(400, 240)

        # 创建缩略图容器
        self.recommended_container = QWidget(self.large_cover)
        self.recommended_container.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        self.recommended_layout = QHBoxLayout(self.recommended_container)
        self.recommended_layout.setContentsMargins(0, 0, 0, 0)
        self.recommended_layout.setSpacing(5)

        # 设置缩略图数据
        self.thumbnail_data = [
            ("Graph/p1.png", "Graph/pb1.jpg"),
            ("Graph/p2.jpg", "Graph/pb2.jpg"),
            ("Graph/p3.png", "Graph/pb3.jpg")
        ]

        # 初始化缩略图
        self.thumbnails = []
        for thumb_path, large_path in self.thumbnail_data:
            thumbnail = QLabel()
            thumbnail.original_image_path = thumb_path
            thumbnail.large_image_path = large_path
            thumbnail.installEventFilter(self)
            self.thumbnails.append(thumbnail)
            self.recommended_layout.addWidget(thumbnail)
            thumbnail.mousePressEvent = lambda event, path=large_path: self.open_playback_interface(path)
        
        
        
        # 创建定时器
        self.position_timer = QTimer(self)
        self.position_timer.setInterval(300)  # 设置为300毫秒
        self.position_timer.timeout.connect(self.update_recommended_position)

        # 启动定时器
        self.position_timer.start()

        # 设置轮播定时器
        self.current_image_path = "Graph/pb1.png"
        self.timer = QTimer(self)
        self.timer.setInterval(3000)  # 3秒切换一次
        self.timer.timeout.connect(self.cycle_thumbnails)
        self.current_thumbnail_index = 0
        self.timer.start()
        

        # 创建分类选项栏
        category_bar = QWidget()
        category_layout = QHBoxLayout(category_bar)
        category_layout.setSpacing(20)
        categories = ["全部", "电视剧", "综艺", "电影", "动漫", "少儿", "纪录片"]
        
        # 创建分类按钮组
        self.category_group = QButtonGroup(self)
        for category in categories:
            btn = QPushButton(category)
            btn.setCheckable(True)
            btn.setStyleSheet("""
                QPushButton {
                    font-size: 16px;
                    padding: 8px 15px;
                    border: none;
                    border-radius: 15px;
                    color: #bfbfbf;
                    background-color: transparent;
                }
                QPushButton:checked {
                    color: white;
                    background-color: #2979ff;
                }
                QPushButton:hover {
                    color: white;
                }
            """)
            category_layout.addWidget(btn)
            self.category_group.addButton(btn)
        category_layout.addStretch()

        # 创建推荐内容区域
        recommendations_widget = QWidget()
        self.recommendations_layout = QGridLayout(recommendations_widget)  # 改用QGridLayout
        self.recommendations_layout.setSpacing(15)
        
        # 视频推荐数据
        video_data = [
            ("video_posters/1.jpg", "人民警察", "陆毅万茜刑警夫妻破凶案"),
            ("video_posters/2.jpg", "庆余年第二季", "与范闲再探庙堂江湖"),
            ("video_posters/3.webp", "绝地战警:生死与共", "百星威尔·史密斯上演招牌喜剧"),
            ("video_posters/4.webp", "神偷奶爸4·爆笑来袭", "新品种!超级小黄人"),
            ("video_posters/5.webp", "奔跑吧", "白鹿张真源探险茶马古道"),
            ("video_posters/6.webp", "出发2 贾冰厨房营业", "铁锅炖孜然羊肉谁能页得住"),
            ("video_posters/7.jpg", "名侦探柯南[日语版]", "正太小神探"),
            ("video_posters/8.jpg", "伍六七之记忆碎片", "伍六七身世之谜揭开")
        ]
        self.video_recommendations = []

        # 使用网格布局来组织视频推荐卡片
        for index, video in enumerate(video_data):
            row = index // 4  # 每行4个卡片
            col = index % 4
            self.recommendation = VideoRecommendation(*video)
            self.recommendations_layout.addWidget(self.recommendation, row, col)
            self.video_recommendations.append(self.recommendation)
            
        # 组织右侧内容布局
        home_layout.addWidget(self.large_cover)
        home_layout.addWidget(category_bar)
        home_layout.addWidget(recommendations_widget)
        home_layout.addStretch()

        self.home_page.setWidget(home_content)
        
        # 创建搜索结果页
        self.search_page = QWidget()
        self.search_layout = QVBoxLayout(self.search_page)
        
        # 添加返回按钮
        back_button = QPushButton("返回主页")
        back_button.setStyleSheet("""
            QPushButton {
                background-color: #2979ff;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                font-size: 14px;
                max-width: 100px;
            }
            QPushButton:hover {
                background-color: #1e88e5;
            }
        """)
        back_button.clicked.connect(self.show_home_page)
        self.search_layout.addWidget(back_button)

        # 创建搜索结果容器
        self.search_results_container = QWidget()
        self.search_results_layout = QVBoxLayout(self.search_results_container)
        self.search_layout.addWidget(self.search_results_container)

        # 将两个页面添加到堆栈窗口
        self.content_stack.addWidget(self.home_page)
        self.content_stack.addWidget(self.search_page)

        # 组织主布局
        content_layout.addWidget(nav_bar)
        content_layout.addWidget(self.content_stack)
        main_layout.addWidget(content_area)


        # 设置全局样式
        self.setStyleSheet("""
            QWidget {
                background-color: #000000;
                color: #ffffff;
            }
        """)

        # 使顶部栏支持鼠标拖动
        self.draggable = True
        self.dragging = False
        self.offset = None

        top_bar.mousePressEvent = self.mousePressEvent
        top_bar.mouseMoveEvent = self.mouseMoveEvent
        top_bar.mouseReleaseEvent = self.mouseReleaseEvent

        self.update_recommended_position()
        
    

    # 搜索按钮点击事件
    def handle_search(self):
        search_text = self.search_bar.text()
        if search_text:
            self.search_manager.handle_search(search_text)
    
    # 重写关闭事件
    def closeEvent(self, event):
        self.search_manager.thumbnail_loader.running = False
        self.search_manager.thumbnail_loader.wait()
        super().closeEvent(event)

    #返回主页
    def show_home_page(self):
        self.content_stack.setCurrentWidget(self.home_page)
        self.search_bar.clear()

    #重定义鼠标按下事件
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.draggable:
            self.dragging = True
            self.offset = event.pos()

    #重定义鼠标移动事件
    def mouseMoveEvent(self, event):
        if self.dragging and self.offset is not None:
            self.move(self.pos() + (event.pos() - self.offset))

    #重定义鼠标释放事件
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.offset = None
    
    #自制放大按钮
    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    #打开视频播放界面
    def open_playback_interface(self, image_path):
        """
        参数:
            image_path (str): 要播放的视频对应的图片路径
        """
        player_manager = VideoPlayerManager.get_instance()
        player_manager.load_video("1.mp4")
        player_manager.show()  # 确保显示播放器
        print(f"Jumping to playback interface for {image_path}")

    #初始化显示界面, 在布局完成后更新图片显示和推荐位置
    def initialize_display(self):
        self.update_image(self.current_image_path)
        self.update_recommended_position()

    #窗口状态改变事件处理函数, 当窗口进入或退出全屏时，调整缩略图的位置
    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange:
            QTimer.singleShot(100, self.update_recommended_position)  # 延迟调用更新位置
        super().changeEvent(event)

    #循环切换缩略图, 定时更新大封面显示的图片
    def cycle_thumbnails(self):
        self.current_thumbnail_index = (self.current_thumbnail_index + 1) % len(self.thumbnail_data)
        self.current_image_path = self.thumbnail_data[self.current_thumbnail_index][1]
        self.update_image(self.current_image_path)
    
    #更新大封面显示的图片
    def update_image(self, image_path):
        """
        参数:
        image_path (str): 要显示的图片文件路径
        功能:
        - 加载指定路径的图片
        - 按照 2:1 的宽高比缩放图片,填充整个控件区域
        - 保持图片质量的同时适应当前尺寸
        """
        pixmap = QPixmap(image_path)
        self.current_image_path = image_path

        # 计算 2:1 的尺寸
        target_width = self.large_cover.width()
        target_height = target_width / 2

        scaled_pixmap = pixmap.scaled(
            target_width, target_height, Qt.IgnoreAspectRatio, Qt.SmoothTransformation
        )
        self.large_cover.setPixmap(scaled_pixmap)
        self.large_cover.setScaledContents(True)

    #更新右下角推荐缩略图的位置和大小
    def update_recommended_position(self):
        """
        功能:
        - 根据当前大封面的尺寸计算缩略图容器的合适大小
        - 调整缩略图容器的位置到右下角
        - 重新缩放所有缩略图以适应新的容器大小
        - 在窗口大小改变时自动调用
        """
        # 获取大封面的当前尺寸
        cover_width = self.large_cover.width()
        cover_height = self.large_cover.height()
        
        # 计算缩略图容器的尺寸（宽度为大封面的30%，最大380像素）
        thumb_container_width = min(380, cover_width * 0.3)
        thumb_container_height = thumb_container_width * 200/380
        
        # 设置缩略图容器的位置和大小（右下角）
        self.recommended_container.setGeometry(
            cover_width - thumb_container_width,  # x坐标
            cover_height - thumb_container_height,  # y坐标
            thumb_container_width,  # 宽度
            thumb_container_height  # 高度
        )
        
        # 更新每个缩略图的大小并重新缩放
        for thumbnail in self.thumbnails:
            new_thumb_width = thumb_container_width / 3 - 10  # 考虑间距
            new_thumb_height = new_thumb_width * 3/2  # 保持宽高比
            thumbnail.setFixedSize(new_thumb_width, new_thumb_height)
            # 缩放缩略图
            thumbnail.setPixmap(
                QPixmap(thumbnail.original_image_path).scaled(
                    new_thumb_width,
                    new_thumb_height,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
            )

    #窗口显示事件处理函数, 当窗口首次显示时更新显示
    def showEvent(self, event):
        super().showEvent(event)
        self.initialize_display()
        self.update_recommended_position()  # 延迟调用更新位置
    
    #窗口大小改变事件处理函数
    def resizeEvent(self, event):
        """        
        参数:
            event: 改变大小事件对象
            
        功能:
        - 在窗口大小改变时更新大图显示
        - 重新调整推荐缩略图的位置和大小
        """
        super().resizeEvent(event)
        QTimer.singleShot(100, self.update_recommended_position)  # 延迟调用更新位置
        # 更新大图显示
        if hasattr(self, 'current_image_path'):
            self.update_image(self.current_image_path)
        for recommendation in self.video_recommendations:
            recommendation.update_poster()  # 调用更新方法
    
    #事件过滤器，用于处理鼠标悬停事件
    def eventFilter(self, source, event):
        """
        参数:
            source: 事件源对象
            event: 事件对象
            
        返回:
            bool: 是否处理该事件
        
        功能:
        - 处理鼠标进入缩略图时切换大图显示
        - 处理鼠标离开时恢复自动轮播
        - 控制轮播定时器的启停
        """
        if event.type() == QEvent.Enter:
            if isinstance(source, QLabel):
                # 停止轮播定时器
                self.timer.stop()
                if hasattr(source, 'large_image_path'):
                    # 更新当前显示的大图
                    self.current_image_path = source.large_image_path
                    self.update_image(source.large_image_path)
            elif source is self.large_cover:
                # 鼠标进入大封面区域时停止轮播
                self.timer.stop()
        elif event.type() == QEvent.Leave:
            if isinstance(source, QLabel) or source is self.large_cover:
                # 鼠标离开时重新启动轮播
                self.timer.start()
        return super().eventFilter(source, event)

# 主程序入口
if __name__ == '__main__':
    # 创建QApplication实例
    app = QApplication(sys.argv)
    # 创建并显示主窗口
    window = TencentVideoClone()
    window.show()
    # 进入应用程序主循环
    sys.exit(app.exec_())