from mlog_lib import trans_m_to_p, get_command_color, TextInputManager, TextInputVisualizer, ColorValue
from pygame import (display, draw, event, font, key, mouse, time, transform,
                    BUTTON_LEFT, BUTTON_WHEELDOWN, BUTTON_WHEELUP,
                    FINGERDOWN, QUIT, MOUSEBUTTONDOWN,
                    Color, Surface, Vector2,
                    init, quit as squit,
                    K_ESCAPE)
from pyndustric import Compiler
from math import ceil, log10
from pathlib import Path
from sys import exit

from random import random  # type: ignore # noqa
from mlog_lib import raw2d  # type: ignore # noqa
from time import sleep  # type: ignore # noqa


font.init()

init()
WIN: Surface = display.set_mode()
SC_RES: Vector2 = Vector2(WIN.get_size())
WIDTH, HEIGHT = SC_RES
FONT: font.Font = font.SysFont('Monospace', 12, bold=True)
CLOCK: time.Clock = time.Clock()
COMPILER = Compiler()

save_path: Path = Path(__file__).parent
save_file: Path = save_path/"pyexa.py"
font_width: float = FONT.size("ABCDEFGHIJKLMNOPQRSTUVWXYZ"  # font not monospaced...
                              "abcdefghijklmnopqrstuvwxyz"
                              "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
                              "абвгдеёжзийклмнопрстуфхцчшщъыьэюя")[0]/118
font_height: int = 12

Cbg: ColorValue = Color(18, 18, 18)
Cfg: ColorValue = Color(36, 36, 36)
Ctxt: ColorValue = Color(207, 212, 218)
Ctxt2: ColorValue = Color(164, 161, 171)
Coutline: ColorValue = Color(255, 255, 255)
Cerror: ColorValue = Color(255, 15, 15)
Cwarn: ColorValue = Color(240, 255, 0)

delta: float = 1/60
mouse_pos: Vector2 = Vector2()
mouse_pressed: tuple[bool, bool, bool]
keys_pressed: key.ScancodeWrapper
events: list[event.Event]

key.set_repeat(200, 100)
key.start_text_input()

with open(save_file, "r", encoding="utf-8") as f:
    exec("from pygame import draw")
    code_textarea: TextInputVisualizer = TextInputVisualizer(TextInputManager(f.read().splitlines()),
                                                             FONT, True, Ctxt,
                                                             500, 2)
del f


def queuit() -> None:
    with open(save_file, "w", encoding="utf-8") as f:
        f.write("\n".join(code_textarea.value))
    squit()
    exit()


linelog10: int = ceil(log10(len(code_textarea.value)+1))
processor_width: int = 1
processor_color: ColorValue = (0, 0, 0)
processor_surface: Surface = Surface((176, 176))
processor_speed: float = 1/120
processor_counter: int = 0
processor_textbuffer: str = ""
processor_cursor_pos: list[int | float] = [0, 0]
processor_vertical_offset: float = 0

display1: Surface = Surface(processor_surface.get_size())
text_surface: Surface
cell1: list[str] = ["" for _ in range(64)]
decoded: list[str] = ["" for _ in range(len(code_textarea.value))]
excepp: list[str] = ["" for _ in range(len(code_textarea.value))]
timer: float = 0

processor_surface.fill(Cbg)


while True:
    timer += delta
    WIN.fill(Cbg)

    mouse_pos.update(mouse.get_pos())
    mouse_pressed = mouse.get_pressed()
    keys_pressed = key.get_pressed()
    events = event.get()

    for e in events:
        if e.type == QUIT or keys_pressed[K_ESCAPE]:
            queuit()
        elif e.type == FINGERDOWN:
            key.start_text_input()
        elif e.type == MOUSEBUTTONDOWN:
            if e.button == BUTTON_WHEELDOWN and processor_vertical_offset > -font_height*(len(code_textarea.value)-1):
                processor_vertical_offset -= font_height * 2
            elif e.button == BUTTON_WHEELUP and processor_vertical_offset < 0:
                processor_vertical_offset += font_height * 2
            elif e.button == BUTTON_LEFT:
                code_textarea.manager.cursor_pos.y = min(int(mouse_pos.y-processor_vertical_offset)//font_height, len(code_textarea.manager)-1)
                code_textarea.manager.cursor_pos.x = int(mouse_pos.x//font_width-linelog10)

    code_textarea.update(events)
    processor_cursor_pos[0] = FONT.size(code_textarea.manager.left[-1])[0]/font_width
    processor_cursor_pos[1] = code_textarea.manager.cursor_pos.y

    inputt_len: int = len(code_textarea.value)

    while len(decoded) != inputt_len:
        if len(decoded) < inputt_len:
            decoded.append("")
            excepp.append("")
        elif len(decoded) > inputt_len:
            decoded.pop()
            excepp.pop()

    if 1:
        linelog10 = ceil(log10(inputt_len))

    while timer >= processor_speed:
        timer -= processor_speed
        processor_counter %= inputt_len

        try:
            raw_line: str = COMPILER.compile(code_textarea.value[processor_counter])
            for i in raw_line.splitlines():
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
        print(decoded, excepp, code_textarea.value)
        raise IndexError("These lists not match? Strange...")

    WIN.blit(transform.flip(display1, False, True), (WIDTH/2-176, 0))

    for j, i in enumerate(code_textarea.value):
        if excepp[j]:
            draw.rect(WIN, Cerror, (WIDTH-font_width, j*font_height+processor_vertical_offset, font_width, font_height))
            draw.rect(WIN, (Cerror[0]//4, Cerror[1]//4, Cerror[2]//4),
                      (0, j*font_height+processor_vertical_offset, WIDTH-font_width, font_height))
        elif decoded[j] == trans_m_to_p("NotImplemented"):
            draw.rect(WIN, Cwarn, (WIDTH-font_width, j*font_height+processor_vertical_offset, font_width, font_height))
            draw.rect(WIN, (Cwarn[0]//4, Cwarn[1]//4, Cwarn[2]//4),
                      (0, j*font_height+processor_vertical_offset, WIDTH-font_width, font_height))
        elif i.replace(' ', ''):
            command_color: Color = Color(get_command_color(i.split(maxsplit=1)[0]))  # type: ignore
            draw.rect(WIN, command_color,
                      (0, j*font_height+processor_vertical_offset, font_width*(linelog10), font_height))
            WIN.blit(FONT.render(f"{j}", True, (((command_color[0]+128) % 256)//2,
                                                ((command_color[1]+128) % 256)//2,
                                                ((command_color[2]+128) % 256)//2)), (0, font_height*j+processor_vertical_offset))
        else:
            WIN.blit(FONT.render(f"{j}", True, Ctxt2), (0, font_height*j+processor_vertical_offset))

        WIN.blit(FONT.render(i, True, Ctxt),
                 (font_width*(linelog10+0.5), font_height*j+processor_vertical_offset))

        if mouse_pos.x >= WIDTH-font_width:
            WIN.blit(FONT.render(f"{decoded[j]!r}", True, Ctxt2),
                     (WIDTH-FONT.size(f"{decoded[j]!r}")[0]-font_width, font_height*j+processor_vertical_offset))
            WIN.blit(FONT.render(excepp[j], True, Cerror),
                     (WIDTH-FONT.size(excepp[j])[0]-font_width, font_height*j+processor_vertical_offset))

    for j, i in enumerate(processor_textbuffer):
        text_surface = FONT.render(i, True, (127, 255, 127))
        WIN.blit(text_surface, text_surface.get_rect(bottomright=SC_RES/2+(0, font_height*j+processor_vertical_offset)))

    draw.aaline(WIN, Coutline, (font_width*linelog10, 0), (font_width*linelog10, HEIGHT))
    if code_textarea.cursor_visible:
        draw.rect(WIN, (255, 255, 255),
                  ((processor_cursor_pos[0]+(linelog10+0.5))*font_width, (processor_cursor_pos[1])*font_height+processor_vertical_offset,
                   code_textarea.cursor_width, font_height))

    WIN.blits([(FONT.render(var, True, Ctxt2), (WIDTH/2, font_height*(y+1)))
               for y, var in enumerate((f"{i[0]} = {i[1]!r}"
                                        for i in globals().items()
                                        if i[0] not in ("__name__", "__doc__", "__package__", "__loader__", "__spec__", "__annotations__", "__builtins__", "__file__", "__cached__",
                                                        "mlog_to_python", "TextInputManager", "TextInputVisualizer", "display", "draw", "event", "font", "key", "mouse", "time", "Surface",
                                                        "Vector2", "Color", "init", "squit", "K_ESCAPE", "QUIT", "list", "tuple", "ceil", "log10", "Path", "exit", "raw2d")))])

    display.flip()
    delta = CLOCK.tick()/1000
