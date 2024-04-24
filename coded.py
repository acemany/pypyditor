    #from math import *
    
    color = (255, 255, 255)
    widthl = 2
    rang = 10
    rad = 100

    draw.polygon(WIN, color,
                 [(200+cos(pi*2*(j)/rang)*rad,
                   200+sin(pi*2*(j)/rang)*rad)
                  for j in range(rang)], widthl)