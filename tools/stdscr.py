import curses


class Stdscr:
    def __init__(self):
        self.scr = curses.initscr()
        self.ps = None
        self.dl = None
        self.cv = None
        self.slot = None
        curses.noecho()
        curses.cbreak()

    def refresh(self):
        self.scr.erase()
        ps_str = f"Mux Parser: {self.pbar(*self.ps)}"
        dl_str = f"Downloader: {self.pbar(*self.dl)}"
        cv_str = f" Converter: {self.pbar(*self.cv)}"
        self.scr.addstr(1, 0, ps_str)
        self.scr.addstr(2, 0, dl_str)
        self.scr.addstr(3, 0, cv_str)
        self.scr.addstr(4, 0, '-'*80)  # Divider
        _n = 1
        for v in self.slot:
            slot = f"slot {_n}: {self.fbar(*v)}"
            self.scr.addstr(_n+4, 0, slot)
            _n += 1
        self.scr.refresh()

    def finish(self):
        curses.echo()
        curses.nocbreak()
        curses.endwin()

    def pbar(self, curr, size):
        if size != 0:
            num = (curr * 40) // size
            bar = f"[{'#'*(num)}{'_'*(40-num)}]"
            percent = str(int(curr/size*100)).rjust(3, ' ')
            return f"{percent}% {bar} {curr}/{size}"

    def fbar(self, curr, size):
        if size == 0:
            bar = f"[{'Empty'.center(40, '_')}]"
            percent = '---'
        else:
            num = (curr * 40) // size
            bar = f"[{'#'*(num)}{'_'*(40-num)}]"
            percent = str(int(curr/size*100)).rjust(3, ' ')
        if size == 1:
            ratio = f'{curr} it / {size} it'
        else:
            ratio = f'{self.toSize(curr) } / {self.toSize(size)}'
        return f"{percent}% {bar} {ratio}"

    def toSize(self, size):
        def strofsize(integer, remainder, level):
            if integer >= 1024:
                remainder = integer % 1024
                integer //= 1024
                level += 1
                return strofsize(integer, remainder, level)
            else:
                return integer, remainder, level

        units = ['B', 'KB', 'MB', 'GB']
        integer, remainder, level = strofsize(size, 0, 0)
        if level+1 > len(units):
            level = -1
        newSize = float(f'{integer}.{remainder:>01d}')
        return (f'{newSize:.1f} {units[level]}')
