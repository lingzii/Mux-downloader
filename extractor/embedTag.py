from io import BytesIO
from json import load
from PIL import Image
from tempfile import gettempdir
from .easyID3 import EasyID3
from shutil import copy
from requests import get
from os import remove


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


def archiveFile(tags, srcFile):
    with open('metadata.json', "r") as f:
        dist = load(f)["save-dist"]
    newName = RE(f"{tags['artist']} - {tags['title']}")
    copy(srcFile, f"{dist}/{newName}.mp3")
    remove(srcFile)


def embedId3(tags):
    srcFile = f'{gettempdir()}\{tags["id"]}.mp3'
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
    archiveFile(tags, srcFile)
