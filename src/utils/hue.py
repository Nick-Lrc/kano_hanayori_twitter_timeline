from __future__ import annotations


class Hue:
    DEFAULT = '\u001b[39m'
    BLACK = '\u001b[30m'
    BLUE = '\u001b[34m'
    CYAN = '\u001b[36m'
    GREEN = '\u001b[32m'
    MAGENTA = '\u001b[35m'
    RED = '\u001b[31m'
    WHITE = '\u001b[37m'
    YELLOW = '\u001b[33m'
    BRIGHT_BLACK = '\u001b[90m'
    BRIGHT_BLUE = '\u001b[94m'
    BRIGHT_CYAN = '\u001b[96m'
    BRIGHT_GREEN = '\u001b[92m'
    BRIGHT_MAGENTA = '\u001b[95m'
    BRIGHT_RED = '\u001b[91m'
    BRIGHT_WHITE = '\u001b[97m'
    BRIGHT_YELLOW = '\u001b[93m'
    
    DEFAULT_BG = '\u001b[49m'
    BLACK_BG = '\u001b[40m'
    BLUE_BG = '\u001b[44m'
    CYAN_BG = '\u001b[46m'
    GREEN_BG = '\u001b[42m'
    MAGENTA_BG = '\u001b[45m'
    RED_BG = '\u001b[41m'
    WHITE_BG = '\u001b[47m'
    YELLOW_BG = '\u001b[43m'
    BRIGHT_BLACK_BG = '\u001b[100m'
    BRIGHT_BLUE_BG = '\u001b[104m'
    BRIGHT_CYAN_BG = '\u001b[106m'
    BRIGHT_GREEN_BG = '\u001b[102m'
    BRIGHT_MAGENTA_BG = '\u001b[105m'
    BRIGHT_RED_BG = '\u001b[101m'
    BRIGHT_WHITE_BG = '\u001b[107m'
    BRIGHT_YELLOW_BG = '\u001b[103m'
    
    BOLD = '\u001b[1m'
    REVERSED = '\u001b[7m'
    UNDERLINE = '\u001b[4m'

    RESET = '\u001b[0m'

    def __init__(self) -> None:
        self._buffer = []

    def __repr__(self) -> str:
        return f'{self.__class__}({self.__dict__})'

    def __str__(self) -> str:
        self.reset()
        return ''.join(self._buffer)

    def error(self, text: str = 'ERROR') -> Hue:
        return self.bright_red_bg().bright_white(f' {text} ').reset()

    def info(self, text: str = 'INFO') -> Hue:
        return self.bright_blue_bg().bright_white(f' {text} ').reset()

    def success(self, text: str = 'SUCCESS') -> Hue:
        return self.bright_green_bg().black(f' {text} ').reset()

    def warning(self, text: str = 'WARNING') -> Hue:
        return self.bright_yellow_bg().black(f' {text} ').reset()

    def default(self, text: str = None) -> Hue:
        return self._add(Hue.DEFAULT)._add(text)

    def black(self, text: str = None) -> Hue:
        return self._add(Hue.BLACK)._add(text)

    def blue(self, text: str = None) -> Hue:
        return self._add(Hue.BLUE)._add(text)

    def cyan(self, text: str = None) -> Hue:
        return self._add(Hue.CYAN)._add(text)

    def green(self, text: str = None) -> Hue:
        return self._add(Hue.GREEN)._add(text)

    def magenta(self, text: str = None) -> Hue:
        return self._add(Hue.MAGENTA)._add(text)
  
    def red(self, text: str = None) -> Hue:
        return self._add(Hue.RED)._add(text)

    def white(self, text: str = None) -> Hue:
        return self._add(Hue.WHITE)._add(text)

    def yellow(self, text: str = None) -> Hue:
        return self._add(Hue.YELLOW)._add(text)

    def bright_black(self, text: str = None) -> Hue:
        return self._add(Hue.BRIGHT_BLACK)._add(text)

    def bright_blue(self, text: str = None) -> Hue:
        return self._add(Hue.BRIGHT_BLUE)._add(text)

    def bright_cyan(self, text: str = None) -> Hue:
        return self._add(Hue.BRIGHT_CYAN)._add(text)

    def bright_green(self, text: str = None) -> Hue:
        return self._add(Hue.BRIGHT_GREEN)._add(text)

    def bright_magenta(self, text: str = None) -> Hue:
        return self._add(Hue.BRIGHT_MAGENTA)._add(text)
  
    def bright_red(self, text: str = None) -> Hue:
        return self._add(Hue.BRIGHT_RED)._add(text)

    def bright_white(self, text: str = None) -> Hue:
        return self._add(Hue.BRIGHT_WHITE)._add(text)

    def bright_yellow(self, text: str = None) -> Hue:
        return self._add(Hue.BRIGHT_YELLOW)._add(text)

    def default_bg(self, text: str = None) -> Hue:
        return self._add(Hue.DEFAULT_BG)._add(text)

    def black_bg(self, text: str = None) -> Hue:
        return self._add(Hue.BLACK_BG)._add(text)

    def blue_bg(self, text: str = None) -> Hue:
        return self._add(Hue.BLUE_BG)._add(text)

    def cyan_bg(self, text: str = None) -> Hue:
        return self._add(Hue.CYAN_BG)._add(text)

    def green_bg(self, text: str = None) -> Hue:
        return self._add(Hue.GREEN_BG)._add(text)

    def magenta_bg(self, text: str = None) -> Hue:
        return self._add(Hue.MAGENTA_BG)._add(text)
  
    def red_bg(self, text: str = None) -> Hue:
        return self._add(Hue.RED_BG)._add(text)

    def white_bg(self, text: str = None) -> Hue:
        return self._add(Hue.WHITE_BG)._add(text)

    def yellow_bg(self, text: str = None) -> Hue:
        return self._add(Hue.YELLOW_BG)._add(text)

    def bright_black_bg(self, text: str = None) -> Hue:
        return self._add(Hue.BRIGHT_BLACK_BG)._add(text)

    def bright_blue_bg(self, text: str = None) -> Hue:
        return self._add(Hue.BRIGHT_BLUE_BG)._add(text)

    def bright_cyan_bg(self, text: str = None) -> Hue:
        return self._add(Hue.BRIGHT_CYAN_BG)._add(text)

    def bright_green_bg(self, text: str = None) -> Hue:
        return self._add(Hue.BRIGHT_GREEN_BG)._add(text)

    def bright_magenta_bg(self, text: str = None) -> Hue:
        return self._add(Hue.BRIGHT_MAGENTA_BG)._add(text)
  
    def bright_red_bg(self, text: str = None) -> Hue:
        return self._add(Hue.BRIGHT_RED_BG)._add(text)

    def bright_white_bg(self, text: str = None) -> Hue:
        return self._add(Hue.BRIGHT_WHITE_BG)._add(text)

    def bright_yellow_bg(self, text: str = None) -> Hue:
        return self._add(Hue.BRIGHT_YELLOW_BG)._add(text)

    def bold(self, text: str = None) -> Hue:
        return self._add(Hue.BOLD)._add(text)

    def reversed(self, text: str = None) -> Hue:
        return self._add(Hue.REVERSED)._add(text)

    def underline(self, text: str = None) -> Hue:
        return self._add(Hue.UNDERLINE)._add(text)

    def flush(self) -> str:
        text = str(self)
        self._buffer.clear()
        return text

    def reset(self) -> Hue:
        return self._add(Hue.RESET)

    def _add(self, text: str) -> Hue:
        if text:
            self._buffer.append(text)
        return self


if __name__ == '__main__':
    print(
        Hue().black('  0 ')
             .blue('  1 ')
             .cyan('  2 ')
             .green('  3 ')
             .magenta('  4 ')
             .red('  5 ')
             .white('  6 ')
             .yellow('  7'))
    print(
        Hue().bright_black('  8 ')
             .bright_blue('  9 ')
             .bright_cyan(' 10 ')
             .bright_green(' 11 ')
             .bright_magenta(' 12 ')
             .bright_red(' 13 ')
             .bright_white(' 14 ')
             .bright_yellow(' 15'))
    print(
        Hue().black_bg(' 16 ')
             .blue_bg(' 17 ')
             .cyan_bg(' 18 ')
             .green_bg(' 19 ')
             .magenta_bg(' 20 ')
             .red_bg(' 21 ')
             .white_bg(' 22 ')
             .yellow_bg(' 23 '))
    print(
        Hue().bright_black_bg(' 24 ')
             .bright_blue_bg(' 25 ')
             .bright_cyan_bg(' 26 ')
             .bright_green_bg(' 27 ')
             .bright_magenta_bg(' 28 ')
             .bright_red_bg(' 29 ')
             .bright_white_bg(' 30 ')
             .bright_yellow_bg(' 31 '))
    print()
    print(
        Hue().default('default ')
             .bold('bold ')
             .reset()
             .underline('underline')
             .reset()
             .default(' ')
             .reversed('reversed'))
    print(Hue().error().success().info().warning())
