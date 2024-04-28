from pygame import (display, event, font, key, mouse, time,
                    Surface, Vector2, Color,
                    init, quit as squit,
                    K_ESCAPE,
                    QUIT)
from mlog_lib import TextInputManager, TextInputVisualizer
from typing import List, Tuple
from pathlib import Path
from sys import exit
exec("from math import pi, cos, sin")


font.init()

init()
WIN: Surface = display.set_mode()
SC_RES: Vector2 = Vector2(WIN.get_size())
WIDTH, HEIGHT = SC_RES
FONT: font.Font = font.SysFont('Monospace', 18, bold=True)
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

with open(gamedir/"coded.py", "r") as f:
    code_textarea: TextInputVisualizer = TextInputVisualizer(TextInputManager(f.read(),
                                                                              validator=lambda i: True),
                                                             FONT, True, Ctxt)
del f


def queuit() -> None:
    with open(gamedir/"coded.py", "w", encoding="utf-8") as f:
        f.write(str(code_textarea.value))
    squit()
    exit()


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

    code_textarea.update(events)

    excepp.clear()
    for j, i in enumerate(code_textarea.value.split("\n")):
        try:
            excepp.append("")
            exec(i)
        except Exception as e:
            excepp.append(f" ! {e!s}")

    prepared_code: Tuple[str] = f"{code_textarea.manager.left}|{code_textarea.manager.right}".split("\n")
    for m, n in enumerate(prepared_code):
        WIN.blit(FONT.render(f"{n}{excepp[m]}", 1, Ctxt2), (5, font_height*(m+0.5)))

    # WIN.blits(((FONT.render(i, 1, (255, 0, 0)), (5, font_height*j))
    #            for j, i in enumerate(excepp)))

    display.flip()
    delta = CLOCK.tick(60)/1000
    if not delta:
        delta = 1/60
