from .embedTag import embedId3
from subprocess import run, PIPE, STDOUT
from os import remove


def converter(path, tags):
    # if 'youtube' in tags['url']:
    #     cmd = [
    #         'ffmpeg', '-i',
    #         f'{path}.webm', '-y',
    #         '-acodec', 'mp3',
    #         '-ab', '128k',
    #         '-ar', '48000',
    #         f'{path}.mp3'
    #     ]

    #     run(cmd, stderr=STDOUT,
    #         stdout=PIPE, stdin=PIPE,
    #         universal_newlines=True)

    #     remove(f"{path}.webm")

    embedId3(tags)
