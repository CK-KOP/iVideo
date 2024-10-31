
from bilibili_api import search, sync
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QGridLayout
from PyQt5.QtGui import QPixmap
import requests
from functools import lru_cache
import queue
import threading
import datetime

class ThumbnailLoader(QThread):
    """异步缩略图加载器"""
    thumbnail_loaded = pyqtSignal(str, QPixmap)
    
    def __init__(self):
        super().__init__()
        self.queue = queue.Queue()
        self.cache = {}
        self.running = True
        
    def add_task(self, url, card_id):
        self.queue.put((url, card_id))
        
    @lru_cache(maxsize=100)
    def load_image(self, url):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                pixmap = QPixmap()
                pixmap.loadFromData(response.content)
                return pixmap.scaled(320, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        except Exception as e:
            print(f"Error loading image: {e}")
        return None
        
    def run(self):
        while self.running:
            try:
                url, card_id = self.queue.get(timeout=1)
                if url in self.cache:
                    pixmap = self.cache[url]
                else:
                    pixmap = self.load_image(url)
                    if pixmap:
                        self.cache[url] = pixmap
                if pixmap:
                    self.thumbnail_loaded.emit(card_id, pixmap)
            except queue.Empty:
                continue




def extract_video_data(api_response):
    """提取视频数据"""
    video_data = []
    try:
        if 'result' in api_response:
            for item in api_response['result']:
                if item.get('result_type') == 'video':
                    for video in item['data']:
                        pic_url = video.get('pic', '')
                        if pic_url.startswith("//"):
                            pic_url = "https:" + pic_url
                        
                        # 获取时间戳并转换为可读日期
                        timestamp = video.get('pubdate', None)
                        if timestamp:
                            date_time = datetime.datetime.fromtimestamp(timestamp)
                            formatted_date = date_time.strftime('%Y-%m-%d %H:%M:%S')
                        else:
                            formatted_date = 'Unknown date'  # 如果没有时间戳，设为未知日期
                            
                        video_data.append({
                            "thumbnail_url": pic_url,
                            "name": video.get('title', 'Untitled'),
                            "author": video.get('author', 'Unknown'),
                            "bvid": video.get('bvid', ''),
                            "pubdate": formatted_date  # 添加可读日期
                        })
    except Exception as e:
        print(f"Error extracting video data: {e}")
    return video_data

def show_search_results(query):
    """执行搜索并返回结果"""
    try:
        api_response = sync(search.search(query))
        return extract_video_data(api_response)
    except Exception as e:
        print(f"Error in search: {e}")
        return []