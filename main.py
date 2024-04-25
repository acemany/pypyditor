from mlog_lib import mlog_to_python, TextInputManager, TextInputVisualizer
from pygame import (display, event, font, key, mouse, time,
                    Surface, Vector2, Color,
                    init, quit as squit,
                    K_ESCAPE,
                    QUIT)
from typing import List, Tuple
from pathlib import Path
from sys import exit
exec("from math import pi, cos, sin; from mlog_lib import raw2d")  # for made pyflake8 shut up


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

with open(gamedir/"codeexample.mlog", "r") as f:
    exec("from pygame import draw")
    code_textarea: TextInputVisualizer = TextInputVisualizer(TextInputManager(f.read(),
                                                                              validator=lambda i: True),
                                                             FONT, True, Ctxt)
del f


def queuit() -> None:
    with open(gamedir/"codeexample.mlog", "w", encoding="utf-8") as f:
        f.write(str(code_textarea.value))
    squit()
    exit()


processor_width: int = 1
processor_color: Color = (0, 0, 0)
processor_surface: Surface = Surface(SC_RES)
text_surface: Surface
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

    for j, i in enumerate(processor_textbuffer.split("\n")):
        text_surface = FONT.render(i, 1, (127, 255, 127))
        WIN.blit(text_surface, text_surface.get_rect(bottomright=SC_RES/2+(0, font_height*j)))
    processor_textbuffer = ""

    display.flip()
    delta = CLOCK.tick(60)/1000
    if not delta:
        delta = 1/60
