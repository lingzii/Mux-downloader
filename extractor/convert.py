from .embedTag import embedId3
from subprocess import Popen, PIPE, STDOUT
from os import remove


def converter(path, tags):
    if 'youtube' in tags['url']:
        cmd = f'ffmpeg -i "{path}.webm" -y -acodec mp3 \
                -ab 128k -ar 48000 "{path}.mp3"'
        Popen(cmd, stdout=PIPE, stderr=STDOUT).wait()
        remove(f"{path}.webm")

    embedId3(tags)
