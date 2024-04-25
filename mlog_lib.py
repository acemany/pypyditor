from pygame import (event, font, key, time,
                    Rect, Surface,
                    KEYDOWN,
                    K_ESCAPE)
from typing import Callable, List, Tuple
from functools import cache
exec("""from math import (asin, acos, atan,
                  sin, cos, tan,
                  log, ceil,
                  pi)
from random import random""")  # i hate this linter


VRTCS = ((1, 1, 0), (-1, 1, 0), (1, -1, 0), (-1, -1, 0),
         (1, 0, 1), (-1, 0, 1), (1, 0, -1), (-1, 0, -1),
         (0, 1, 1), (0, -1, 1), (0, 1, -1), (0, -1, -1))


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

    def _process_keydown(self, ev: event.Event):
        attrname = f"_process_{key.name(ev.key)}"
        if hasattr(self, attrname):
            getattr(self, attrname)()
        elif ev.key == K_ESCAPE:
            pass
        else:
            self._process_other(ev)

    def _process_delete(self):
        self.right = self.right[1:]

    def _process_backspace(self):
        self.left = self.left[:-1]

    def _process_left(self):
        self.cursor_pos -= 1

    def _process_right(self):
        self.cursor_pos += 1

    def _process_up(self):
        self.cursor_pos -= 10

    def _process_down(self):
        self.cursor_pos += 10

    def _process_end(self):
        self.cursor_pos = len(self.value)

    def _process_home(self):
        self.cursor_pos = 0

    def _process_return(self):
        self.left += "\n"

    def _process_other(self, event: event.Event):
        self.left += event.unicode


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

    return 70*sum(((0 if t0 < 0 else t0**4 * dot(VRTCS[perm(seed, ii + perm(seed, jj)) % 12],           x0, y0)),
                   (0 if t1 < 0 else t1**4 * dot(VRTCS[perm(seed, ii + i1 + perm(seed, jj + j1)) % 12], x1, y1)),
                   (0 if t2 < 0 else t2**4 * dot(VRTCS[perm(seed, ii + 1 + perm(seed, jj + 1)) % 12],   x2, y2))))


def mlog_to_python(code: str) -> str:
    i: Tuple[str] = code.split()
    match i[0]:
        case "draw":
            match i[1]:
                case "clear":
                    return f"processor_surface.fill(({int(i[2])}, {int(i[3])}, {int(i[4])}))"
                case "color":
                    return f"processor_color = ({i[2]}, {i[3]}, {i[4]}, {i[5]})"
                case "col":
                    return "NotImplemented"
                case "stroke":
                    return f"processor_width = {i[2]}"
                case "line":
                    return f"draw.line(processor_surface, processor_color, ({i[2]}, {i[3]}), ({i[4]}, {i[5]}), processor_width)"
                case "rect":
                    return f"draw.rect(processor_surface, processor_color, ({i[2]}, {i[3]}, {i[4]}, {i[5]}))"
                case "lineRect":
                    return f"draw.rect(processor_surface, processor_color, ({i[2]}, {i[3]}, {i[4]}, {i[5]}), processor_width)"
                case "poly":
                    return f"draw.polygon(processor_surface, processor_color, [({i[2]}+cos(pi*2/{i[4]}*j+{i[6]})*{i[5]}, {i[3]}+sin(pi*2/{i[4]}*j+{i[6]})*{i[5]}) for j in range({i[4]})])"
                case "linePoly":
                    return f"draw.polygon(processor_surface, processor_color, [({i[2]}+cos(pi*2/{i[4]}*j+{i[6]})*{i[5]}, {i[3]}+sin(pi*2/{i[4]}*j+{i[6]})*{i[5]}) for j in range({i[4]})], processor_width)"
                case "triangle":
                    return f"draw.polygon(processor_surface, processor_color, (({i[2]}, {i[3]}), ({i[4]}, {i[5]}), ({i[6]}, {i[7]})))"
                case "image":
                    return "NotImplemented"
                case _:
                    return "NotImplemented"
        case "read":
            return f"{i[1]} = {i[2]}[{i[3]}]"
        case "write":
            return f"{i[2]}[{i[3]}] = {i[1]}"
        case "print":
            return f"processor_textbuffer += {i[1]}"
        case "drawflush":
            return f"{i[1]}.blit(processor_surface, (0, 0))"
        case "printflush":
            return 'print("processor_textbuffer"); processor_textbuffer = ""'
        case "op":
            match i[1]:
                case "add":
                    return f"{i[2]} + {i[3]}"
                case "sub":
                    return f"{i[2]} - {i[3]}"
                case "mul":
                    return f"{i[2]} * {i[3]}"
                case "div":
                    return f"{i[2]} / {i[3]}"
                case "idiv":
                    return f"{i[2]} // {i[3]}"
                case "mod":
                    return f"{i[2]} % {i[3]}"
                case "pow":
                    return f"{i[2]} ** {i[3]}"

                case "equal":
                    return f"abs({i[2]} - {i[3]}) < 0.000001"
                case "notEqual":
                    return f"abs({i[2]} - {i[3]}) >= 0.000001"
                case "land":
                    return f"{i[2]} != 0 && {i[3]} != 0"
                case "lessThan":
                    return f"{i[2]} < {i[3]}"
                case "lessThanEq":
                    return f"{i[2]} <= {i[3]}"
                case "greaterThan":
                    return f"{i[2]} > {i[3]}"
                case "greaterThanEq":
                    return f"{i[2]} >= {i[3]}"
                case "strictEqual":
                    return "0"

                case "shl":
                    return f"{i[2]} << {i[3]}"
                case "shr":
                    return f"{i[2]} >> {i[3]}"
                case "or":
                    return f"{i[2]} | {i[3]}"
                case "and":
                    return f"{i[2]} & {i[3]}"
                case "xor":
                    return f"{i[2]} ^ {i[3]}"
                case "not":
                    return f"~{i[2]}"

                case "max":
                    return f"max({i[2]}, {i[3]})"
                case "min":
                    return f"min({i[2]}, {i[3]})"
                case "angle":
                    return f"(atan2({i[3]}, {i[2]}) * 180/pi) % 360"
                case "angleDiff":
                    return f"min(({i[3]} - {i[2]})%360, ({i[2]} - {i[3]})%360)"
                case "len":
                    return f"abs({i[2]} - {i[3]})"
                case "noise":
                    return f"raw2d(0, {i[2]}, {i[3]})"
                case "abs":
                    return f"abs({i[2]})"
                case "log":
                    return f"log({i[2]})"
                case "log10":
                    f"log({i[2]}, 10)"
                case "floor":
                    return f"int({i[2]})"
                case "ceil":
                    return f"ceil({i[2]})"
                case "sqrt":
                    return f"{i[2]} ** 0.5"
                case "rand":
                    f"random() * {i[2]}"

                case "sin":
                    f"sin({i[2]} / 180*pi)"
                case "cos":
                    f"cos({i[2]} / 180*pi)"
                case "tan":
                    f"tan({i[2]} / 180*pi)"

                case "asin":
                    f"asin({i[2]}) / 180*pi)"
                case "acos":
                    f"acos({i[2]}) / 180*pi)"
                case "atan":
                    f"atan({i[2]}) / 180*pi)"
        case _:
            return "NotImplemented"
