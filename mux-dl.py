from extractor.youtube import youtubeParser
from extractor.streetvoice import streetvoiceParser
from extractor.bandcamp import bandcampParser
from tools.sundry import importMeta, measureTime, moduleStatus
from extractor.embedTag import embedId3
from tools.playsound import playsound
from tools.database import dedup
from tools.stdscr import Stdscr

from concurrent.futures import ThreadPoolExecutor
from argparse import ArgumentParser
from threading import Thread
from queue import Queue
from time import sleep

_config = importMeta()
_status = moduleStatus()
_bridge = Queue()


class moduleTrack:
    def __init__(self) -> None:
        self.curr = 0

    def status(self) -> tuple:
        return (self.curr, _status.total)


class ParserTrack(moduleTrack):
    def __init__(self, raw) -> None:
        super().__init__()
        self.raw = list(set(raw))
        _status.total = len(self.raw)
        self.th = Thread(target=self.task)
        self.th.start()

    def task(self):
        def func(url):
            try:
                if 'streetvoice' in url:
                    seq = streetvoiceParser(url)
                elif 'bandcamp' in url:
                    seq = bandcampParser(url)
                else:
                    seq = youtubeParser(url)

                [_bridge.put(i) for i in seq]

            except Exception as content:
                # print(f"\033[91m{content}\033[96m")
                pass

            self.curr += 1

        with ThreadPoolExecutor(_config.worker_ps) as executer:
            executer.map(func, self.raw)


class DownloaderTrack(moduleTrack):
    def __init__(self) -> None:
        super().__init__()
        self.slotStatus = dict()
        self.th = Thread(target=self.listener)
        self.th.start()

    def listener(self):
        with ThreadPoolExecutor(_config.worker_dl) as excuter:
            while _status.ps or not _bridge.empty():
                sleep(_config.delay)
                if not _bridge.empty():
                    pack = _bridge.get()
                    excuter.submit(self.task, *pack)

    def task(self, songDL, obj):
        song = dedup(obj)
        if not (_config.debug and song.exist()):
            DL = songDL(obj)
            ID = str(id(DL))
            while DL.th.is_alive():
                self.slotStatus[ID] = DL.status()
            embedId3(obj, _config)
            song.insert()
            self.slotStatus.pop(ID)
        self.curr += 1

    def slot(self):
        return self.slotStatus.values()


def main():
    ap = ArgumentParser(
        description='MUX donloader for YouTube, Soundcloud, StreetVoice')
    ap.add_argument('-i', '--input', required=False, metavar='url',
                    help='Path to input source URL')
    ap.add_argument('-f', '--file', required=False,
                    help='Path to input source URL of text flie (*.txt)')
    args = vars(ap.parse_args())

    def textToList(file) -> list:
        with open(file, 'r') as f:
            return [i for i in f.read().split('\n') if i]

    url, file = args['input'], args['file']
    raw = textToList(file) if file else [url]

    if raw == [None]:
        print(f"\033[93mInto program without data.\033[96m")
        return

    stdscr = Stdscr()
    Parser = ParserTrack(raw)
    Downloader = DownloaderTrack()

    def processIsAlive():
        _status.ps = Parser.th.is_alive()
        _status.dl = Downloader.th.is_alive()
        return _status.isAlive()

    while processIsAlive():
        stdscr.ps = Parser.status()
        stdscr.dl = Downloader.status()
        stdscr.slot = Downloader.slot()
        stdscr.refresh()
        sleep(_config.delay)

    stdscr.finish()


if __name__ == '__main__':
    consum = measureTime(function=main)
    if _config.debug:
        print(f'Total running time: {consum} sec')
    if _config.ring:
        playsound('./material/YU.mp3')
