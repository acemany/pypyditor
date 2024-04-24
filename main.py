from pygame import (display, event, font, key, mouse, time,
                    Rect, Surface, Vector2, Color,
                    init, quit as squit,
                    KEYDOWN, QUIT,
                    K_ESCAPE)
from typing import Callable, List, Tuple
from pathlib import Path
from sys import exit
exec("from math import pi, cos, sin")  # for made pyflake8 shut up


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


font.init()

init()
WIN: Surface = display.set_mode()
SC_RES: Vector2 = Vector2(WIN.get_size())
WIDTH, HEIGHT = SC_RES
FONT: font.Font = font.SysFont('Monospace', 12, bold=True)
CLOCK: time.Clock = time.Clock()
gamedir: Path = Path(__file__).parent
font_size: Tuple[int, int] = FONT.size("N")
font_width, font_height = font_size

Cbuttonua: Color = (63, 63, 63)
Cbuttona: Color = (4, 104, 170)
Cbg: Color = (18, 18, 18)
Ctxt: Color = (207, 212, 218)
Ctxt2: Color = (164, 161, 171)

delta: float = 0.1/6
mouse_pos: Vector2 = Vector2()
mouse_pressed: Tuple[bool, bool, bool]
keys_pressed: Tuple[bool]
events = Tuple[event.Event]

key.set_repeat(200, 100)
key.start_text_input()

with open(gamedir/"coded.mlog", "r") as f:
    exec("from pygame import draw")
    code_textarea: TextInputVisualizer = TextInputVisualizer(TextInputManager(f.read(),
                                                                              validator=lambda i: True),
                                                             FONT, True, Ctxt)
del f


def queuit() -> None:
    with open(gamedir/"coded.mlog", "w", encoding="utf-8") as f:
        f.write(str(code_textarea.value))
    squit()
    exit()


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
            return f'print("{processor_textbuffer}"); processor_textbuffer = ""'
        case _:
            return "NotImplemented"


processor_width: int = 1
processor_color: Color = (0, 0, 0)
processor_surface: Surface = Surface(SC_RES)
processor_textbuffer: str = ""
cell1: List[str] = ["" for i in range(64)]
decoded: List[str] = []
excepp: List[str] = []


while True:
    WIN.fill(Cbg)

    mouse_pos.update(mouse.get_pos())
    mouse_pressed = mouse.get_pressed()
    keys_pressed = key.get_pressed()
    events = event.get()

    for e in events:
        if e.type == QUIT or keys_pressed[K_ESCAPE]:
            queuit()
        # elif e.type == KEYDOWN:
            # if e.key not in (K_LSHIFT, K_LEFT, K_RIGHT, K_BACKSPACE, K_RETURN):
            #     print(key.name(e.key))
            # if e.key == K_RETURN:
            #     code_textarea.manager.left += "\n"

    code_textarea.update(events)

    decoded.clear()
    excepp.clear()
    for j, i in enumerate(code_textarea.value.split("\n")):
        # print(mlog_to_python(i), i)
        try:
            decoded.append(mlog_to_python(i))
            exec(decoded[j])
        except Exception as e:
            decoded.append("")
            excepp.append(f"{e!s} !!! {i}")

    prepared_code: Tuple[str] = f"{code_textarea.manager.left}|{code_textarea.manager.right}".split("\n")
    for m, n in enumerate(prepared_code):
        WIN.blit(FONT.render(f"{m:>3}| {n} | {decoded[m]}", 1, Ctxt2), (5, font_height*(m+0.5)))

        WIN.blits(((FONT.render(i, 1, (255, 0, 0)), (5, font_height*j))
                   for j, i in enumerate(excepp)))

    display.flip()
    delta = CLOCK.tick(60)/1000
    if not delta:
        delta = 1/60
