from .easyID3 import EasyID3
from tempfile import gettempdir
from requests import get
from shutil import copy
from io import BytesIO
from PIL import Image
from os import remove, path


def RE(name):
    for i in ['/', '|', '\\', '?', '"', '*', ':', '<', '>']:
        name = name.replace(i, "")
    return name


def url2Image(url):
    res = BytesIO(get(url).content)
    img = Image.open(res).convert('RGB')
    w, h = img.size
    if w > 1920:
        img = img.resize((1920, int(1920*h/w)))
    with BytesIO() as f:
        img.save(f, format='JPEG')
        return f.getvalue()


def embedId3(tags, config):
    name = RE(f"{tags['artist']} - {tags['title']}")
    srcFile = f'{gettempdir()}\{tags["id"]}.mp3'
    distfile = path.join(config.dist, f'{name}.mp3')

    tags['image'] = url2Image(tags['image'])
    audio = EasyID3(srcFile)
    audio.artist = tags['artist']
    audio.title = tags['title']
    audio.album = tags['album']
    audio.track_num = tags['track_num']
    audio.url = tags['url']
    audio.image = tags['image']
    audio.lyric = tags['lyric']
    audio.save()

    copy(srcFile, distfile)
    remove(srcFile)
