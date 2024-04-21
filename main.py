from pygame import (K_ESCAPE, K_LSHIFT, K_LEFT, K_RIGHT, K_BACKSPACE, K_RETURN,
                    display, event, font, key, mouse, time,
                    Rect, Surface, Vector2,
                    init, quit as squit,
                    KEYDOWN, QUIT)
from typing import List, Callable
from pathlib import Path
from sys import exit

font.init()


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


init()
WIN = display.set_mode()
WIDTH, HEIGHT = SC_RES = Vector2(WIN.get_size())
FONT = font.SysFont('Monospace', 12, bold=True)
CLOCK = time.Clock()
key.set_repeat(200, 100)
gamedir = Path(__file__).parent
font_width, font_height = font_size = FONT.size("N")

excepp = ""

Cbuttonua = (63, 63, 63)
Cbuttona = (4, 104, 170)
Cbg = (18, 18, 18)
Ctxt = (207, 212, 218)
Ctxt2 = (164, 161, 171)

delta = 0.1/6
mouse_pos = Vector2()

key.start_text_input()

with open(gamedir/"coded.py", "r") as f:
    code_init, code_process = f.read().split("\n\nwhile True:\n")
    exec(code_init)
    code_textarea = TextInputVisualizer(TextInputManager(code_process,
                                                         validator=lambda i: True),
                                        FONT, True, Ctxt)
del f


def queuit():
    with open(gamedir/"coded.py", "w") as f:
        f.write(f"{code_init}\n\nwhile True:\n{code_textarea.value}")
    del f
    squit()
    exit()


while True:
    WIN.fill(Cbg)

    mouse_pos.update(mouse.get_pos())
    mouse_pressed = mouse.get_pressed()
    keys_pressed = key.get_pressed()
    events = event.get()

    code_textarea.update(events)

    for e in events:
        if e.type == QUIT or keys_pressed[K_ESCAPE]:
            queuit()
        elif e.type == KEYDOWN:
            if e.key == K_ESCAPE:
                queuit()
            elif e.key not in (K_LSHIFT, K_LEFT, K_RIGHT, K_BACKSPACE):
                print(key.name(e.key))
            if e.key == K_RETURN:
                code_textarea.manager.left += "\n"

    try:
        exec(f"if True:\n{code_textarea.value}")
        excepp = ""
    except Exception as e:
        excepp = f"{e.__repr__()}"

    WIN.blits(((FONT.render(excepp, 1, (255, 0, 0)), (0, 0)),
              *[(FONT.render(f"{j if j > 0 else '':>3}| {i}", 1, Ctxt2), (0, font_height*j))
                for j, i in enumerate([CLOCK.get_fps(), *[k[4:] for k in f"{code_textarea.manager.left}|{code_textarea.manager.right}".split("\n")]])]))
    display.flip()
    delta = CLOCK.tick(60)/1000
    if not delta:
        delta = 1/60
