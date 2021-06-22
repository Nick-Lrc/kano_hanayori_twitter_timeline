from __future__ import annotations


class ProgressBar:
    BLOCK = '█'
    PLACEHOLDER = '─'
    SEPARATOR = '│'
    MAX_WIDTH = 25

    def __init__(self, total: int):
        self._cursor = Cursor()
        self._count = 0
        self._total = total
        self._total_digits = len(str(self._total))

    def start(self):
        self._cursor.save()
        self._print_bar()
    
    def increment(self):
        if not self._is_complete():
            self._count += 1
            self._cursor.restore()
            self._print_bar()

    def end(self):
        print()
        self._cursor.save()

    def _is_complete(self):
        return self._count >= self._total

    def _print_bar(self):
        percent = self._count / self._total
        width = int(percent * ProgressBar.MAX_WIDTH)
        bar = [
            f'{self._count:{self._total_digits}}/{self._total} ',
            ProgressBar.SEPARATOR,
            ProgressBar.BLOCK * width,
            ProgressBar.PLACEHOLDER * (ProgressBar.MAX_WIDTH - width),
            ProgressBar.SEPARATOR,
            f' {int(percent * 100):3}%',
        ]
        print(''.join(bar), end='')


class Cursor:
    SAVE = u'\u001b[s'
    RESTORE = u'\u001b[u'
    
    def save(self):
        print(end=Cursor.SAVE)
        return self

    def restore(self):
        print(end=Cursor.RESTORE)
        return self


if __name__ == '__main__':
    total = 1000
    progress_bar = ProgressBar(total)
    progress_bar.start()
    for i in range(total):
        progress_bar.increment()
    progress_bar.end()
