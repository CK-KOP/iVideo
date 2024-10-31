import asyncio
from bilibili_api import video, Credential, HEADERS
import httpx
import os

SESSDATA = "16e65046%2C1745757135%2Cd6af9%2Aa1CjDlyAkKQzxVkbFvziKt2FxbW8lrhJt8wPGeFFQDlDdygtrvCiRgvJJNHBLWsObJfzkSVjlQLVlKOEVLRE1rRkhTTDRJVkJIVXdVeGJSNUlGV2M2TnhSVzVKOGY1MGl3OTBwZHRuREJGbmU1ZFBwVjh3WW93UnQxUDMzY2hjMkhnWnNYTFA1M01RIIEC"
BILI_JCT = "1a37af42cda388868a5c3a13d838bdce"
BUVID3 = "9D78A9BA-2B75-72EB-D065-73FD0F7E43DD62594infoc"

FFMPEG_PATH ="D:\\ffmpeg\\ffmpeg\\bin\\ffmpeg.exe"

class BilibiliVideoDownloader:
    def __init__(self, sessdata, bili_jct, buvid3):
        self.credential = Credential(sessdata=sessdata, bili_jct=bili_jct, buvid3=buvid3)

    async def download_url(self, url: str, out: str, info: str):
        async with httpx.AsyncClient(headers=HEADERS) as sess:
            resp = await sess.get(url)
            length = resp.headers.get('content-length')
            with open(out, 'wb') as f:
                process = 0
                async for chunk in resp.aiter_bytes(1024):
                    if not chunk:
                        break

                    process += len(chunk)
                    print(f'下载 {info} {process} / {length}')
                    f.write(chunk)

    async def download_stream(self, bvid: str, output_file: str = "video.mp4", callback=None):
        v = video.Video(bvid=bvid, credential=self.credential)
        download_url_data = await v.get_download_url(0)
        detecter = video.VideoDownloadURLDataDetecter(data=download_url_data)
        streams = detecter.detect_best_streams()
        # 如果video.mp4文件存在，就删除
        if os.path.exists("video.mp4"):
            os.remove("video.mp4")
        # 有 MP4 流 / FLV 流两种可能
        if detecter.check_flv_stream() == True:
            # FLV 流下载
            await self.download_url(streams[0].url, "flv_temp.flv", "FLV 音视频流")
            # 转换文件格式
            os.system(f'{FFMPEG_PATH} -i flv_temp.flv video.mp4')
            # 删除临时文件
            os.remove("flv_temp.flv")
        else:
            # MP4 流下载
            await self.download_url(streams[0].url, "video_temp.m4s", "视频流")
            await self.download_url(streams[1].url, "audio_temp.m4s", "音频流")
            # 混流
            os.system(f'{FFMPEG_PATH} -i video_temp.m4s -i audio_temp.m4s -vcodec copy -acodec copy video.mp4')
            # 删除临时文件
            os.remove("video_temp.m4s")
            os.remove("audio_temp.m4s")
        
        if callback:
            callback(output_file)

def start_download(bvid, output_file, callback):
    downloader = BilibiliVideoDownloader(SESSDATA, BILI_JCT, BUVID3)
    asyncio.run(downloader.download_stream(bvid, output_file, callback))