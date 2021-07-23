from mutagen.id3 import ID3, TIT2, TALB, TPE1, TRCK, WOAS, USLT, APIC


class EasyID3:
    def __init__(self, file):
        self._audio = ID3(file)
        self._audio.delete()
        self.artist = None
        self.title = None
        self.album = None
        self.track_num = None
        self.url = None
        self.image = None
        self.lyric = None

    def pprint(self):
        return self._audio.pprint()

    def save(self):
        if self.artist:
            self._audio.add(TPE1(text=self.artist))
        if self.title:
            self._audio.add(TIT2(text=self.title))
        if self.album:
            self._audio.add(TALB(text=self.album))
        if self.track_num:
            self._audio.add(TRCK(text=self.track_num))
        if self.url:
            self._audio.add(WOAS(url=self.url))
        if self.lyric:
            self._audio.add(USLT(lang='zho', text=self.lyric))
        if self.image:
            self._audio.add(APIC(mime='image/jpeg', data=self.image))

        self._audio.save()
