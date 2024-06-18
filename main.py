from mlog_lib import trans_m_to_p, get_command_color, TextInputManager, TextInputVisualizer
from pygame import (display, draw, event, font, key, mouse, time, transform,
                    FINGERDOWN, QUIT, BUTTON_WHEELDOWN, BUTTON_WHEELUP, MOUSEBUTTONDOWN,
                    Surface, Vector2, Color,
                    init, quit as squit,
                    K_ESCAPE)
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
WIN: Surface = display.set_mode()
SC_RES: Vector2 = Vector2(WIN.get_size())
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
Cwarn: Color = Color(240, 255, 0)

delta: float = 1/60
mouse_pos: Vector2 = Vector2()
mouse_pressed: Tuple[bool, bool, bool]
keys_pressed: Tuple[bool]
events: Tuple[event.Event]

key.set_repeat(200, 100)
key.start_text_input()

with open(gamedir/"codeexample.mlog", "r", encoding="utf-8") as f:
    exec("from pygame import draw")
    code_textarea: TextInputVisualizer = TextInputVisualizer(TextInputManager(f.read().splitlines()),
                                                             FONT, True, Ctxt,
                                                             500, 2)
del f


def queuit() -> None:
    with open(gamedir/"codeexample.mlog", "w", encoding="utf-8") as f:
        f.write("\n".join(code_textarea.value))
    squit()
    exit()


linelog10: int = ceil(log10(len(code_textarea.value)+1))
processor_width: int = 1
processor_color: Color = (0, 0, 0)
processor_surface: Surface = Surface((176, 176))
processor_speed: float = 1/120
processor_counter: int = 0
processor_textbuffer: str = ""
processor_cursor_pos: List[int] = [0, 0]
processor_vertical_offset: float = 0

display1: Surface = Surface(processor_surface.size)
text_surface: Surface
cell1: List[str] = ["" for _ in range(64)]
decoded: List[str] = ["" for _ in range(len(code_textarea.value))]
excepp: List[str] = ["" for _ in range(len(code_textarea.value))]
timer: int = 0

processor_surface.fill(Cbg)


while True:
    timer += delta
    WIN.fill(Cbg)

    mouse_pos.update(mouse.get_pos())
    mouse_pressed = mouse.get_pressed()
    keys_pressed = key.get_pressed()
    events = event.get()

    inputt: List[str] = code_textarea.value
    inputt_len: int = len(inputt)

    for e in events:
        if e.type == QUIT or keys_pressed[K_ESCAPE]:
            queuit()
        elif e.type == FINGERDOWN:
            key.start_text_input()
        elif e.type == MOUSEBUTTONDOWN:
            if e.button == BUTTON_WHEELDOWN and processor_vertical_offset > -font_height*(len(code_textarea.value)-1):
                processor_vertical_offset -= font_height
            elif e.button == BUTTON_WHEELUP and processor_vertical_offset < 0:
                processor_vertical_offset += font_height

    code_textarea.update(events)
    processor_cursor_pos[0] = FONT.size(code_textarea.manager.left[-1])[0]/font_width
    processor_cursor_pos[1] = code_textarea.manager.cursor_pos[1]

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
        timer -= processor_speed
        processor_counter %= inputt_len

        raw_line: str = inputt[processor_counter]
        try:
            excepp[processor_counter] = ""
            decoded[processor_counter] = ""
            if not raw_line:  # if empty
                processor_counter += 1
                continue
            k = raw_line.split()
            if k[0] == "op" and k[2] not in globals():
                exec(f"global {k[2]};{k[2]} = 0")
            _ = trans_m_to_p(raw_line)
            decoded[processor_counter] = _
            exec(_)
        except Exception as e:
            decoded[processor_counter] = ""
            excepp[processor_counter] = f"{e!s}"
        processor_counter += 1

    if len(decoded) != len(excepp) != inputt_len:
        print(decoded, excepp, inputt)
        raise IndexError("These lists not match? Strange...")

    WIN.blit(transform.flip(display1, False, True), (0, 0))

    for j, i in enumerate(code_textarea.value):
        if excepp[j]:
            draw.rect(WIN, Cerror, (WIDTH-font_width, j*font_height+processor_vertical_offset, *font_size))
            draw.rect(WIN, (Cerror[0]/4, Cerror[1]/4, Cerror[2]/4),
                      (0, j*font_height+processor_vertical_offset, WIDTH-font_width, font_height))
        if decoded[j] == trans_m_to_p("NotImplemented"):
            draw.rect(WIN, Cwarn, (WIDTH-font_width, j*font_height+processor_vertical_offset, *font_size))
            draw.rect(WIN, (Cwarn[0]/4, Cwarn[1]/4, Cwarn[2]/4),
                      (0, j*font_height+processor_vertical_offset, WIDTH-font_width, font_height))

        WIN.blit(FONT.render(f"{j}", 1, Ctxt2), (0, font_height*j+processor_vertical_offset))
        WIN.blit(FONT.render(i, 1, get_command_color(f"{i} _".split(maxsplit=1)[0])),
                 (font_width*(linelog10+0.5), font_height*j+processor_vertical_offset))

        if mouse_pos.x >= WIDTH-font_width:
            WIN.blit(FONT.render(f"{decoded[j]!r}", 1, Ctxt2),
                     (WIDTH-FONT.size(f"{decoded[j]!r}")[0]-font_width, font_height*j+processor_vertical_offset))
            WIN.blit(FONT.render(excepp[j], 1, Cerror),
                     (WIDTH-FONT.size(excepp[j])[0]-font_width, font_height*j+processor_vertical_offset))

    for j, i in enumerate(processor_textbuffer):
        text_surface = FONT.render(i, 1, (127, 255, 127))
        WIN.blit(text_surface, text_surface.get_rect(bottomright=SC_RES/2+(0, font_height*j+processor_vertical_offset)))

    draw.aaline(WIN, Coutline, (font_width*linelog10, 0), (font_width*linelog10, HEIGHT))
    if code_textarea._cursor_visible:
        draw.rect(WIN, (255, 255, 255),
                  ((processor_cursor_pos[0]+(linelog10+0.5))*font_width, (processor_cursor_pos[1])*font_height+processor_vertical_offset,
                   code_textarea._cursor_width, font_height))

    WIN.blits([(FONT.render(var, 1, Ctxt2), (WIDTH/2, font_height*(y+1)))
               for y, var in enumerate((f"{i[0]} = {i[1]!r}"
                                        for i in globals().items()
                                        if i[0] not in ("__name__", "__doc__", "__package__", "__loader__", "__spec__", "__annotations__", "__builtins__", "__file__", "__cached__",
                                                        "mlog_to_python", "TextInputManager", "TextInputVisualizer", "display", "draw", "event", "font", "key", "mouse", "time", "Surface",
                                                        "Vector2", "Color", "init", "squit", "K_ESCAPE", "QUIT", "List", "Tuple", "ceil", "log10", "Path", "exit", "raw2d")))])

    display.flip()
    delta = CLOCK.tick()/1000
