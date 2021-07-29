from time import perf_counter
from json import dumps, load
from os.path import exists

_name = 'metadata.json'
_metadata = {
    "save-folder": ".",
    "debug-mode": False,
    "finish-ringtone": True,
    "refresh-delay": 0.2,
    "parse-worker": 3,
    "download-worker": 10
}


def measureTime(function) -> str:
    beg = perf_counter()
    function()
    end = perf_counter()
    return f'{end-beg:.1f}'


def save(file: str, data: dict) -> None:
    with open(file, 'w', encoding="utf-8") as f:
        i = dumps(data, ensure_ascii=False, indent=2)
        f.write(i.encode("utf8").decode())


class importMeta:
    def __init__(self) -> None:
        if not exists(_name):
            save(_name, _metadata)
        with open(_name) as file:
            data = load(file)
        self.dist = data['save-folder']
        self.debug = data['debug-mode']
        self.delay = data['refresh-delay']
        self.ring = data['finish-ringtone']
        self.worker_ps = data['parse-worker']
        self.worker_dl = data['download-worker']


class moduleStatus:
    def __init__(self) -> None:
        self.total = 0
        self.ps = True
        self.dl = True

    def isAlive(self) -> bool:
        return self.ps or self.dl
