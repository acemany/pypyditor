if __name__ == "__main__":
    from pygame import display, event, Surface, Vector2, init
    from mlog_lib import raw2d

    init()
    WIN: Surface = display.set_mode()
    SC_RES: Vector2 = Vector2(WIN.get_size())
    WIDTH: int = int(SC_RES[0])
    HEIGHT: int = int(SC_RES[1])

    while True:
        WIN.fill(0)
        event.get()

        for y in range(0, HEIGHT):
            if y & 0b111111 == 0:
                display.flip()
            for x in range(0, WIDTH):
                WIN.set_at((x, y), [raw2d(0, x/50, y/50)*127+127]*3)
