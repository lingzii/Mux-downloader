from extractor.youtube import youtubeParser, youtubeDL
from extractor.streetvoice import streetvoiceParser, streetvoiceDL
from extractor.bandcamp import bandcampParser, bandcampDL
from extractor.convert import converter
from tools.playsound import playsound
from tools.priority_queue import pqueue
from tools.measure import measureTime
from tools.stdscr import Stdscr


from concurrent.futures import ThreadPoolExecutor
from argparse import ArgumentParser
from queue import Queue
from threading import Thread
from time import sleep
from json import load

global_refresh_delay = 0

moduleStatus = {'ps': True, 'dl': True, 'cv': True}
rawList = Queue()
songList = pqueue()
total = None


def load_global_variable() -> None:
    global global_refresh_delay
    try:
        with open('metadata.json') as f:
            _sec = load(f)['refresh-delay']
            global_refresh_delay = _sec
    except:
        from tools.compilation import save
        metadata = {
            "save-dist": '.',
            "refresh-delay": 0.2,
            "debugMode": False
        }
        save('metadata.json', metadata)


class moduleTrack:
    def __init__(self) -> None:
        self.curr = 0

    def status(self):
        return (self.curr, total)


class ParserTrack(moduleTrack):
    def __init__(self, raw) -> None:
        super().__init__()
        self.raw = list(set(raw))
        global total
        total = len(self.raw)
        self.th = Thread(target=self.task)
        self.th.start()

    def task(self):
        def func(url):
            global rawList
            try:
                if 'streetvoice' in url:
                    seq = [(streetvoiceDL, i) for i in streetvoiceParser(url)]
                elif 'bandcamp' in url:
                    seq = [(bandcampDL, i) for i in bandcampParser(url)]
                else:
                    seq = [(youtubeDL, i) for i in youtubeParser(url)]

                [rawList.put(i) for i in seq]

            except Exception as content:
                pass  # print(f"\033[91m{content}\033[96m")

            self.curr += 1

        with ThreadPoolExecutor(max_workers=10) as executer:
            executer.map(func, self.raw)


class DownloaderTrack(moduleTrack):
    def __init__(self) -> None:
        super().__init__()
        self.slotStatus = dict()
        self.th = Thread(target=self.listener)
        self.th.start()

    def listener(self):
        global rawList
        with ThreadPoolExecutor(max_workers=8) as excuter:
            while moduleStatus['ps'] or not rawList.empty():
                sleep(global_refresh_delay)
                if not rawList.empty():
                    pack = rawList.get()
                    excuter.submit(self.task, *pack)

    def task(self, songDL, obj):
        global songList
        DL = songDL(obj)
        ID = str(id(DL))
        while DL.th.is_alive():
            self.slotStatus[ID] = DL.status()
        songList.put(DL.info())
        self.slotStatus.pop(ID)
        self.curr += 1

    def slot(self):
        return self.slotStatus.values()


class ConverterTrack(moduleTrack):
    def __init__(self) -> None:
        super().__init__()
        self.th = Thread(target=self.listener)
        self.th.start()

    def listener(self):
        # return
        global songList
        with ThreadPoolExecutor(max_workers=5) as excuter:
            while moduleStatus['dl'] or not songList.empty():
                sleep(global_refresh_delay)
                if not songList.empty():
                    pack = songList.get()[1:]
                    excuter.submit(self.task, pack)
                else:
                    sleep(global_refresh_delay*4)

    def task(self, pack):
        converter(*pack)
        self.curr += 1


def main():
    ap = ArgumentParser(
        description='MUX donloader for YouTube, Soundcloud, StreetVoice')
    ap.add_argument('-i', '--input', required=False,
                    help='Path to input source URL')
    ap.add_argument('-f', '--file', required=False,
                    help='Path to input source URL of text flie (*.txt)')
    args = vars(ap.parse_args())

    def textToList(file):
        with open(file, 'r') as f:
            return [i for i in f.read().split('\n') if i]

    url, file = args['input'], args['file']
    raw = textToList(file) if file else [url]

    stdscr = Stdscr()
    Parser = ParserTrack(raw)
    Downloader = DownloaderTrack()
    Converter = ConverterTrack()

    def processIsAlive() -> bool:
        moduleStatus['ps'] = Parser.th.is_alive()
        moduleStatus['dl'] = Downloader.th.is_alive()
        moduleStatus['cv'] = Converter.th.is_alive()
        return True in moduleStatus.values()

    while processIsAlive():
        stdscr.ps = Parser.status()
        stdscr.dl = Downloader.status()
        stdscr.cv = Converter.status()
        stdscr.slot = Downloader.slot()
        stdscr.refresh()
        sleep(global_refresh_delay)

    stdscr.finish()


if __name__ == '__main__':
    load_global_variable()
    consum = measureTime(target=main)
    print(f'Total running time: {consum} sec')
    playsound('./material/YU.mp3')
