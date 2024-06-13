from pygame import (event, font, time,
                    Rect, Surface,
                    KEYDOWN)
from typing import Callable, List, Tuple
from functools import cache
exec("""
from random import random""")  # i hate this linter


class TextInputManager:
    def __init__(self,
                 initial: str = "",
                 validator: Callable[[str], bool] = lambda x: True):

        self.left = initial  # string to the left of the cursor
        self.right = ""  # string to the right of the cursor
        self.validator = validator

    @property
    def value(self):
        return self.left + self.right

    @value.setter
    def value(self, value):
        cursor_pos = self.cursor_pos
        self.left = value[:cursor_pos]
        self.right = value[cursor_pos:]

    @property
    def cursor_pos(self):
        return len(self.left)

    @cursor_pos.setter
    def cursor_pos(self, value):
        complete = self.value
        self.left = complete[:value]
        self.right = complete[value:]

    def update(self, events: List[event.Event]):
        for e in events:
            if e.type == KEYDOWN:
                v_before = self.value
                c_before = self.cursor_pos
                self._process_keydown(e)
                if not self.validator(self.value):
                    self.value = v_before
                    self.cursor_pos = c_before

    def _process_keydown(self, e: event.Event):
        match e.key:
            case 27:  # K_ESCAPE
                pass
            case 127:  # K_DELETE
                self.right = self.right[1:]
            case 8:  # K_BACKSPACE
                self.left = self.left[:-1]
            case 1073741904:  # K_LEFT
                self.cursor_pos -= 1 if self.cursor_pos > 0 else 0
            case 1073741903:  # K_RIGHT
                self.cursor_pos += 1
            case 1073741906:  # K_UP
                self.cursor_pos -= 10 if self.cursor_pos > 9 else self.cursor_pos
            case 1073741905:  # K_DOWN
                self.cursor_pos += 10
            case 1073741901:  # K_END
                self.cursor_pos = len(self.value)
            case 1073741898:  # K_HOME
                self.cursor_pos = 0
            case 13:  # K_RETURN
                self.left += "\n"
            case _:
                self.left += e.unicode


class TextInputVisualizer:
    def __init__(self,
                 manager: TextInputManager = None,
                 font_object: font.Font = None,
                 antialias: bool = True,
                 font_color: List[int] = (0, 0, 0),
                 cursor_blink_interval: int = 300,
                 cursor_width: int = 3,
                 cursor_color: List[int] = (0, 0, 0)):

        self.manager = TextInputManager() if manager is None else manager
        self._font_object = font.Font(font.get_default_font(), 25) if font_object is None else font_object
        self._antialias = antialias
        self._font_color = font_color

        self._clock = time.Clock()
        self._cursor_blink_interval = cursor_blink_interval
        self._cursor_visible = False
        self._last_blink_toggle = 0

        self._cursor_width = cursor_width
        self._cursor_color = cursor_color

        self._surface = Surface((self._cursor_width, self._font_object.get_height()))
        self._rerender_required = True

    @property
    def value(self):
        return self.manager.value

    @value.setter
    def value(self, v: str):
        self.manager.value = v

    @property
    def surface(self):
        if self._rerender_required:
            self._rerender()
            self._rerender_required = False
        return self._surface

    @property
    def antialias(self):
        return self._antialias

    @antialias.setter
    def antialias(self, v: bool):
        self._antialias = v
        self._require_rerender()

    @property
    def font_color(self):
        return self._font_color

    @font_color.setter
    def font_color(self, v: List[int]):
        self._font_color = v
        self._require_rerender()

    @property
    def font_object(self):
        return self._font_object

    @font_object.setter
    def font_object(self, v: font.Font):
        self._font_object = v
        self._require_rerender()

    @property
    def cursor_visible(self):
        return self._cursor_visible

    @cursor_visible.setter
    def cursor_visible(self, v: bool):
        self._cursor_visible = v
        self._last_blink_toggle = 0
        self._require_rerender()

    @property
    def cursor_width(self):
        return self._cursor_width

    @cursor_width.setter
    def cursor_width(self, v: int):
        self._cursor_width = v
        self._require_rerender()

    @property
    def cursor_color(self):
        return self._cursor_color

    @cursor_color.setter
    def cursor_color(self, v: List[int]):
        self._cursor_color = v
        self._require_rerender()

    @property
    def cursor_blink_interval(self):
        return self._cursor_blink_interval

    @cursor_blink_interval.setter
    def cursor_blink_interval(self, v: int):
        self._cursor_blink_interval = v

    def update(self, events: List[event.Event]):
        value_before = self.manager.value
        self.manager.update(events)
        if self.manager.value != value_before:
            self._require_rerender()

        self._clock.tick()
        self._last_blink_toggle += self._clock.get_time()
        if self._last_blink_toggle > self._cursor_blink_interval:
            self._last_blink_toggle %= self._cursor_blink_interval
            self._cursor_visible = not self._cursor_visible

            self._require_rerender()

        if [event for event in events if event.type == KEYDOWN]:
            self._last_blink_toggle = 0
            self._cursor_visible = True
            self._require_rerender()

    def _require_rerender(self):
        self._rerender_required = True

    def _rerender(self):
        rendered_surface = self.font_object.render(self.manager.value + " ",
                                                   self.antialias,
                                                   self.font_color)
        w, h = rendered_surface.get_size()
        self._surface = Surface((w + self._cursor_width, h))
        self._surface = self._surface.convert_alpha(rendered_surface)
        self._surface.fill((0, 0, 0, 0))
        self._surface.blit(rendered_surface, (0, 0))

        if self._cursor_visible:
            str_left_of_cursor = self.manager.value[:self.manager.cursor_pos]
            cursor_y = self.font_object.size(str_left_of_cursor)[0]
            cursor_rect = Rect(cursor_y, 0, self._cursor_width, self.font_object.get_height())
            self._surface.fill(self._cursor_color, cursor_rect)


def dot(g: Tuple[int], x: float, y: float):
    return g[0] * x + g[1] * y


@cache
def perm(seed: int, x: int):
    x = ((x//0xffff) ^ x)*0x45d9f3b
    x = ((x//0xffff) ^ x)*(0x45d9f3b+seed)
    return ((x//0xffff) ^ x) & 0xff


def raw2d(seed: int, x: float, y: float):
    "idk how i translated this from java but it works"

    s: float = (x + y) * 0.3660254037844386
    i: int = int(x + s)
    j: int = int(y + s)

    t: float = (i + j) * 0.21132486540518713

    X0: float = i - t
    Y0: float = j - t

    x0: float = x - X0
    y0: float = y - Y0

    i1 = x0 > y0
    j1 = not i1

    x1: float = x0 - i1 + 0.21132486540518713
    y1: float = y0 - j1 + 0.21132486540518713
    x2: float = x0 - 1 + 2 * 0.21132486540518713
    y2: float = y0 - 1 + 2 * 0.21132486540518713

    ii: int = i & 255
    jj: int = j & 255

    t0: float = 0.5 - x0**2 - y0**2
    t1: float = 0.5 - x1**2 - y1**2
    t2: float = 0.5 - x2**2 - y2**2

    return 70*sum(((0 if t0 < 0 else t0**4 * dot(((1, 1, 0), (-1, 1, 0), (1, -1, 0), (-1, -1, 0),
                                                  (1, 0, 1), (-1, 0, 1), (1, 0, -1), (-1, 0, -1),
                                                  (0, 1, 1), (0, -1, 1), (0, 1, -1), (0, -1, -1)
                                                  )[perm(seed, ii + perm(seed, jj)) % 12],           x0, y0)),
                   (0 if t1 < 0 else t1**4 * dot(((1, 1, 0), (-1, 1, 0), (1, -1, 0), (-1, -1, 0),
                                                  (1, 0, 1), (-1, 0, 1), (1, 0, -1), (-1, 0, -1),
                                                  (0, 1, 1), (0, -1, 1), (0, 1, -1), (0, -1, -1)
                                                  )[perm(seed, ii + i1 + perm(seed, jj + j1)) % 12], x1, y1)),
                   (0 if t2 < 0 else t2**4 * dot(((1, 1, 0), (-1, 1, 0), (1, -1, 0), (-1, -1, 0),
                                                  (1, 0, 1), (-1, 0, 1), (1, 0, -1), (-1, 0, -1),
                                                  (0, 1, 1), (0, -1, 1), (0, 1, -1), (0, -1, -1)
                                                  )[perm(seed, ii + 1 + perm(seed, jj + 1)) % 12],   x2, y2))))


def mlog_to_python(code: str) -> str:
    """Transforms Mlog code(from processors from Mindustry) to python code.\n
    args[0] is the name of command\n
    args[1] is the type of command if command is draw or op, else it is first arg\n
    other args is just args"""

    args: Tuple[str] = code.split()

    match args[0]:
        case "read":
            return f"{args[1]} = {args[2]}[{args[3]}]"
        case "write":
            return f"{args[2]}[{args[3]}] = {args[1]}"
        case "draw":
            match args[1]:
                case "clear":
                    return f"processor_surface.fill(({int(args[2])}, {int(args[3])}, {int(args[4])}))"
                case "color":
                    return f"processor_color = ({args[2]}, {args[3]}, {args[4]}, {args[5]})"
                case "col":
                    return f"processor_color = ({int(args[1][1:3], base=16)}, {int(args[1][3:5], base=16)}, {int(args[1][5:7], base=16)})"
                case "stroke":
                    return f"processor_width = {args[2]}"
                case "line":
                    return f"draw.line(processor_surface, processor_color, ({args[2]}, {args[3]}), ({args[4]}, {args[5]}), processor_width)"
                case "rect":
                    return f"draw.rect(processor_surface, processor_color, ({args[2]}, {args[3]}, {args[4]}, {args[5]}))"
                case "lineRect":
                    return f"draw.rect(processor_surface, processor_color, ({args[2]}, {args[3]}, {args[4]}, {args[5]}), processor_width)"
                case "poly":
                    return f"draw.polygon(processor_surface, processor_color, [({args[2]}+cos(pi*2/{args[4]}*j+{args[6]})*{args[5]}, {args[3]}+sin(pi*2/{args[4]}*j+{args[6]})*{args[5]}) for j in range({args[4]})])"
                case "linePoly":
                    return f"draw.polygon(processor_surface, processor_color, [({args[2]}+cos(pi*2/{args[4]}*j+{args[6]})*{args[5]}, {args[3]}+sin(pi*2/{args[4]}*j+{args[6]})*{args[5]}) for j in range({args[4]})], processor_width)"
                case "triangle":
                    return f"draw.polygon(processor_surface, processor_color, (({args[2]}, {args[3]}), ({args[4]}, {args[5]}), ({args[6]}, {args[7]})))"
                case "image":
                    return "NotImplemented"
                case _:
                    return "NotImplemented"
        case "print":
            return f"processor_textbuffer += str({args[1]})"
        case "drawflush":
            return f"{args[1]}.blit(processor_surface, (0, 0))"
        case "printflush":
            return ''
        case "set":
            return f"global {args[1]};{args[1]} = {args[2]}"
        case "op":
            match args[1]:
                case "add":
                    opeq = f"{args[3]} + {args[4]}"
                case "sub":
                    opeq = f"{args[3]} - {args[4]}"
                case "mul":
                    opeq = f"{args[3]} * {args[4]}"
                case "div":
                    opeq = f"{args[3]} / {args[4]}"
                case "idiv":
                    opeq = f"{args[3]} // {args[4]}"
                case "mod":
                    opeq = f"{args[3]} % {args[4]}"
                case "pow":
                    opeq = f"{args[3]} ** {args[4]}"

                case "equal":
                    opeq = f"abs({args[3]} - {args[4]}) < 0.000001"
                case "notEqual":
                    opeq = f"abs({args[3]} - {args[4]}) >= 0.000001"
                case "land":
                    opeq = f"{args[3]} != 0 && {args[4]} != 0"
                case "lessThan":
                    opeq = f"{args[3]} < {args[4]}"
                case "lessThanEq":
                    opeq = f"{args[3]} <= {args[4]}"
                case "greaterThan":
                    opeq = f"{args[3]} > {args[4]}"
                case "greaterThanEq":
                    opeq = f"{args[3]} >= {args[4]}"
                case "strictEqual":
                    "0"

                case "shl":
                    opeq = f"{args[3]} << {args[4]}"
                case "shr":
                    opeq = f"{args[3]} >> {args[4]}"
                case "or":
                    opeq = f"{args[3]} | {args[4]}"
                case "and":
                    opeq = f"{args[3]} & {args[4]}"
                case "xor":
                    opeq = f"{args[3]} ^ {args[4]}"
                case "not":
                    opeq = f"~{args[3]}"

                case "max":
                    opeq = f"max({args[3]}, {args[4]})"
                case "min":
                    opeq = f"min({args[3]}, {args[4]})"
                case "angle":
                    opeq = f"(atan2({args[4]}, {args[3]}) * 180/pi) % 360"
                case "angleDiff":
                    opeq = f"min(({args[4]} - {args[3]})%360, ({args[3]} - {args[4]})%360)"
                case "len":
                    opeq = f"abs({args[3]} - {args[4]})"
                case "noise":
                    opeq = f"raw2d(0, {args[3]}, {args[4]})"
                case "abs":
                    opeq = f"abs({args[3]})"
                case "log":
                    opeq = f"log({args[3]})"
                case "log10":
                    opeq = f"log({args[3]}, 10)"
                case "floor":
                    opeq = f"int({args[3]})"
                case "ceil":
                    opeq = f"ceil({args[3]})"
                case "sqrt":
                    opeq = f"{args[3]} ** 0.5"
                case "rand":
                    opeq = f"random() * {args[3]}"

                case "sin":
                    opeq = f"sin({args[3]} / 180*pi)"
                case "cos":
                    opeq = f"cos({args[3]} / 180*pi)"
                case "tan":
                    opeq = f"tan({args[3]} / 180*pi)"

                case "asin":
                    opeq = f"asin({args[3]}) / 180*pi)"
                case "acos":
                    opeq = f"acos({args[3]}) / 180*pi)"
                case "atan":
                    opeq = f"atan({args[3]}) / 180*pi)"
                case _:
                    return "NotImplemented"
            return f"{args[2]} = {opeq}"
        case _:
            return "NotImplemented"
