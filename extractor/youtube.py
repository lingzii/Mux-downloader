from youtube_dl import YoutubeDL
from tempfile import gettempdir
from threading import Thread
from os import getcwd, chdir
# from requests import get


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
        ads = [i for i in info['formats'] if 'audio' in i['format']
               and i['ext'] == 'webm']
        audioUrl = sorted(ads, key=lambda i: i['abr'])[-1]['url']
        return {'url': audioUrl, 'tags': mkTags(info)}

    ydl_opts = {"quiet": True, "ignoreerrors": True}
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        if 'Soundcloud' in info['extractor_key']:
            if '_type' in info:
                pass
            else:
                pass
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


class youtubeDL:
    def __init__(self, obj):
        self.curr = 0
        self.size = 0
        self.obj = obj
        self.path = f"{gettempdir()}\{self.obj['tags']['id']}"
        self.th = Thread(target=self.task)
        self.th.start()

    def status(self):
        return (self.curr, self.size)

    def task(self):
        # with get(self.obj['url'], stream=True) as r:
        #     self.size = int(r.headers['Content-length'])
        #     with open(f'{self.path}.webm', 'wb') as f:
        #         for chunk in r.iter_content(4096):
        #             self.curr += len(chunk)
        #             f.write(chunk)

        self.size = 1
        tmp = getcwd()
        chdir(gettempdir())
        ydl_opts = {
            "quiet": True,
            "ignoreerrors": True,
            'outtmpl': r'%(id)s.%(ext)s',
            'postprocessors': [
                {'key': 'FFmpegExtractAudio',
                 'preferredcodec': 'mp3'},
                {'key': 'FFmpegMetadata'},
            ]
        }
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([self.obj['tags']['url']])
        chdir(tmp)
        self.curr = 1

    def info(self):
        return (self.size, self.path, self.obj['tags'])
