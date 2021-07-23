from subprocess import Popen, PIPE, STDOUT
from threading import Thread
from tempfile import gettempdir
from requests import get, post
from json import loads
from re import compile


_header = r"https://streetvoice.com"
pattern = _header + r'/(\w+)/*(songs|playlists)*/*(album|\d+)*/*(\d+)*'


def getJson(url, key=None):
    j = loads(get(url).text)
    return j[key] if key else j


def streetvoiceParser(url):
    def matchInfo(url):
        urlInfo = compile(pattern).search(url).groups()
        user, type, ID, tmp = urlInfo
        if id == 'album':
            type, ID = ID, tmp
        if not type:
            type = 'user'
        if type == 'playlists':
            type = 'playlist'
        return (user, type, ID)

    def toApiUrl(_type, content):
        return f'{_header}/api/v4/{_type}/{content}'

    user, type, ID = matchInfo(url)
    if type == 'user':
        apiUrl = toApiUrl('user', user)
        _count = getJson(apiUrl, 'profile')['songs_count']
        result = getJson(f'{apiUrl}/songs/?limit={_count}', 'results')
        idList = [song['id'] for song in result]
    elif type == 'songs':
        idList = [ID]
    else:
        apiUrl = toApiUrl(type, ID)
        idList = getJson(apiUrl, 'song_ids')

    return [toApiUrl('song', i) for i in idList]


class streetvoiceDL:
    def __init__(self, url):
        self.curr = 0
        self.size = 1
        self.url = url
        self.path = None
        self.tags = None
        self.th = Thread(target=self.task)
        self.th.start()

    def status(self):
        return (self.curr, self.size)

    def task(self):
        self.tags = self.mkTags(getJson(self.url))
        m3u8Url = post(f'{self.url}/hls/file/').json()['file']
        self.path = f'{gettempdir()}\{self.tags["id"]}.mp3'
        cmd = f'ffmpeg -hide_banner -loglevel error -y \
            -i {m3u8Url} -acodec mp3 -ab 128k "{self.path}"'
        Popen(cmd, stdout=PIPE, stderr=STDOUT).wait()
        self.curr += 1

    def mkTags(self, info):
        return {
            'id': info['id'],
            'artist': info['user']['profile']['nickname'],
            'title': info['name'],
            'album': info['album']['name'] if info['album'] else None,
            'track_num': None,
            'url': f"{_header}/{info['user']['username']}/songs/{info['id']}",
            'image': info['image'],
            'lyric': info['lyrics'],
        }

    def info(self):
        return (0, self.path, self.tags)
