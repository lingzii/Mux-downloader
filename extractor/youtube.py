from youtube_dl import YoutubeDL
from tempfile import gettempdir
from threading import Thread


class youtubeDL:
    def __init__(self, obj):
        self.curr = 0
        self.size = 1
        self.obj = obj
        self.url = obj['url']
        self.th = Thread(target=self.task)
        self.th.start()

    def status(self):
        return (self.curr, self.size)

    def task(self):
        ydl_opts = {
            "quiet": True,
            "ignoreerrors": True,
            'format': 'bestaudio/best',
            'postprocessors': [
                {'key': 'FFmpegMetadata'},
                {'key': 'FFmpegExtractAudio',
                 'preferredquality': '128',
                 'preferredcodec': 'mp3'}
            ],
            'outtmpl': f'{gettempdir()}/%(id)s.%(ext)s',
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([self.url])
        self.curr = 1


def youtubeParser(url):
    def mkTags(info):
        tags = {
            'id': info['id'],
            'artist':  info['uploader'],
            'title': info['title'],
            'album':  None,
            'track_num':  None,
            'url': info['webpage_url'],
            'image': info['thumbnail'],
            'lyric': None,
        }

        if info["extractor"] == 'youtube' and 'creator' in info:
            tags['artist'] = info['creator']

        return tags

    def mkPack(info):
        return (youtubeDL, mkTags(info))

    ydl_opts = {"quiet": True, "ignoreerrors": True}
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        if 'Soundcloud' in info['extractor_key']:
            pass  # if '_type' in info: else:
        elif 'Youtube' in info['extractor_key']:
            if '_type' in info:
                if info['webpage_url_basename'] == 'playlist':
                    return [mkPack(i) for i in info['entries']]
                else:
                    for ls in info['entries']:
                        if ls['webpage_url_basename'] == 'videos':
                            return [mkPack(i) for i in ls['entries']]
            else:
                return [mkPack(info)]
