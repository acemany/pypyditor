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

exec("""
from random import random
from mlog_lib import raw2d
from time import sleep""")  # for made pyflake8 shut up


font.init()

init()
display1: Surface = display.set_mode()
SC_RES: Vector2 = Vector2(display1.get_size())
WIDTH, HEIGHT = SC_RES
FONT: font.Font = font.SysFont('Monospace', 12, bold=True)
CLOCK: time.Clock = time.Clock()
gamedir: Path = Path(__file__).parent
font_size: Tuple[int, int] = FONT.size("N")
font_width, font_height = font_size

Cbg: Color = Color(18, 18, 18)
Cfg: Color = Color(36, 36, 36)
Ctxt: Color = Color(207, 212, 218)
Ctxt2: Color = Color(164, 161, 171)
Coutline: Color = Color(255, 255, 255)
Cerror: Color = Color(255, 15, 15)

delta: float = 1/60
mouse_pos: Vector2 = Vector2()
mouse_pressed: Tuple[bool, bool, bool]
keys_pressed: Tuple[bool]
events: Tuple[event.Event]

key.set_repeat(200, 100)
key.start_text_input()

with open(gamedir/"codeexample.mlog", "r", encoding="utf-8") as f:
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


linelog10: int = ceil(log10(len(code_textarea.value.split("\n"))+1))
processor_width: int = 1
processor_color: Color = (0, 0, 0)
processor_surface: Surface = Surface((176, 176))
processor_counter: int = 0
text_surface: Surface
processor_textbuffer: str = ""
cell1: List[str] = ["" for _ in range(64)]
decoded: List[str] = ["" for _ in range(len(code_textarea.value.split("\n")))]
excepp: List[str] = ["" for _ in range(len(code_textarea.value.split("\n")))]
timer: int = 0

display1.convert_alpha()
processor_surface.convert_alpha()
processor_surface.fill(Cbg)


while True:
    timer += delta
    display1.fill(Cbg)

    mouse_pos.update(mouse.get_pos())
    mouse_pressed = mouse.get_pressed()
    keys_pressed = key.get_pressed()
    events = event.get()

    for e in events:
        if e.type == QUIT or keys_pressed[K_ESCAPE]:
            queuit()

    code_textarea.update(events)

    inputt = code_textarea.value.split("\n")
    inputt_len: int = len(inputt)

    while len(decoded) != inputt_len:
        if len(decoded) < inputt_len:
            decoded.append("")
            excepp.append("")
        elif len(decoded) > inputt_len:
            decoded.pop()
            excepp.pop()

    if 1:
        linelog10 = ceil(log10(inputt_len+1))

    while timer >= processor_speed:
        processor_textbuffer = f"{linelog10}   "
        processor_counter %= inputt_len

        raw_line: str = inputt[processor_counter]
        try:
            if not raw_line:
                decoded[processor_counter] = ""
                excepp[processor_counter] = ""
                continue
            k = raw_line.split()
            if k[0] == "op" and k[2] not in globals():
                exec(f"global {k[2]};{k[2]} = 0")
            _ = mlog_to_python(raw_line)
            decoded[processor_counter] = _
            excepp[processor_counter] = ""
            exec(_)
        except Exception as e:
            decoded[processor_counter] = ""
            excepp[processor_counter] = f"{e!s}"
        processor_counter += 1
        timer -= processor_speed

    if len(decoded) != len(excepp) != inputt_len:
        print(decoded, excepp, inputt)
        raise IndexError("These lists not match? Strange...")

    for j, i in enumerate(f"{code_textarea.manager.left}|{code_textarea.manager.right}".split("\n")):
        if excepp[j]:
            draw.rect(display1, Cerror, (WIDTH-font_width, j*font_height, *font_size))
            draw.rect(display1, (Cerror[0]/4, Cerror[1]/4, Cerror[2]/4), (0, j*font_height, WIDTH-font_width, font_height))

        display1.blit(FONT.render(f"{j}", 1, Ctxt2), (0, font_height*j))

        display1.blit(FONT.render(i, 1, Ctxt), (font_width*(linelog10+0.5), font_height*j))

        if mouse_pos.x >= WIDTH-font_width:
            display1.blit(FONT.render(decoded[j], 1, Ctxt2), (WIDTH-FONT.size(decoded[j])[0]-font_width, font_height*j))

            display1.blit(FONT.render(excepp[j], 1, Cerror), (WIDTH-FONT.size(excepp[j])[0]-font_width, font_height*j))

    for j, i in enumerate(processor_textbuffer.split("\n")):
        text_surface = FONT.render(i, 1, (127, 255, 127))
        display1.blit(text_surface, text_surface.get_rect(bottomright=SC_RES/2+(0, font_height*j)))

    draw.aaline(display1, Coutline, (font_width*linelog10, 0), (font_width*linelog10, HEIGHT))

    display1.blits([(FONT.render(var, 1, Ctxt2), (WIDTH/2, font_height*(y+1)))
                    for y, var in enumerate((f"{i[0]} = {i[1]!r}"
                                             for i in globals().items()
                                             if i[0] not in ("__name__", "__doc__", "__package__", "__loader__", "__spec__", "__annotations__", "__builtins__", "__file__", "__cached__",
                                                             "mlog_to_python", "TextInputManager", "TextInputVisualizer", "display", "draw", "event", "font", "key", "mouse", "time", "Surface",
                                                             "Vector2", "Color", "init", "squit", "K_ESCAPE", "QUIT", "List", "Tuple", "ceil", "log10", "Path", "exit", "raw2d")))])

    display.flip()
    delta = CLOCK.tick(60)/1000
