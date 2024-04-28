from mlog_lib import mlog_to_python, TextInputManager, TextInputVisualizer
from pygame import (display, draw, event, font, key, mouse, time,
                    Surface, Vector2, Color,
                    init, quit as squit,
                    K_ESCAPE,
                    QUIT)
from typing import List, Tuple
from math import ceil, log10
from pathlib import Path

from sys import exit
exec("from mlog_lib import raw2d")  # for made pyflake8 shut up


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

Cbg: Color = (18, 18, 18)
Cfg: Color = (36, 36, 36)
Ctxt: Color = (207, 212, 218)
Ctxt2: Color = (164, 161, 171)
Coutline: Color = (255, 255, 255)
Cerror: Color = (255, 15, 15)

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


linesqrt10 = ceil(log10(len(code_textarea.value.split("\n"))+1))
processor_width: int = 1
processor_color: Color = (0, 0, 0)
processor_surface: Surface = Surface(SC_RES)
processor_surface.fill(Cbg)
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

    code_textarea.update(events)

    if 1:  # unoptimised
        linesqrt10 = ceil(log10(len(code_textarea.value.split("\n"))+1))

    for m in range(48):
        processor_textbuffer = f"{linesqrt10}   "
        decoded.clear()
        excepp.clear()
        for j, i in enumerate(code_textarea.value.split("\n")):
            try:
                k = i.split()
                if k[0] == "op" and k[2] not in globals():
                    exec(f"global {k[2]};{k[2]} = 0")
                _ = mlog_to_python(i)
                exec(_)
                decoded.append(_)
                excepp.append("")
            except Exception as e:
                decoded.append("")
                excepp.append(f" ! {e!s} !!! {i}")
    if len(decoded) != len(excepp) != len(code_textarea.value.split("\n")):
        print(decoded, excepp, code_textarea.value.split("\n"))

    prepared_code: Tuple[str] = f"{code_textarea.manager.left}|{code_textarea.manager.right}".split("\n")
    for j, i in enumerate(prepared_code):
        WIN.blits(((FONT.render(f"{i} | {decoded[j]}", 1, Ctxt2), (font_width*(linesqrt10+0.5), font_height*j)),
                   (FONT.render(f"{j+1}", 1, Ctxt2), (0, font_height*j))))
        if mouse_pos.x == WIDTH-1:
            WIN.blit(FONT.render(excepp[j], 1, Cerror, Cfg), (0, font_height*j))

    for j, i in enumerate(processor_textbuffer.split("\n")):
        text_surface = FONT.render(i, 1, (127, 255, 127))
        WIN.blit(text_surface, text_surface.get_rect(bottomright=SC_RES/2+(0, font_height*j)))

    draw.aaline(WIN, Coutline, (font_width*linesqrt10, 0), (font_width*linesqrt10, HEIGHT))

    display.flip()

    delta = CLOCK.tick(600)/1000
    if not delta:
        delta = 1/60
