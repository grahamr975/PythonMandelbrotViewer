from numpy import zeros, empty, uint8, sqrt
import pygame
import random
from numba import njit, prange

#Controls:
# move: WASD
# zoom in: e
# zoom out: q
# Increase iterations: r
# Decrease iterations: f
# Take Screenshot: t
try:
    @njit(cache=True, fastmath=True, parallel=False, nogil=True)
    def brot(sx, sy, fxs, fxf, fys, fyf, mx):
        field = zeros((sx, sy))
        for py1 in prange(0,sy):
            for px1 in range(0,sx):
                #NEW X = ((NEW MAX - NEW MIN) * (x - OLD MIN) / (OLD MAX - OLD MIN)) + NEW MIN
                x0 = (((fxf-fxs)*px1)/sx) + fxs
                y0 = (((fyf-fys)*py1)/sy) + fys
                x = 0
                y = 0
                iteration = 0
                while (x*x + y*y <= 4 and iteration < mx):
                    xtemp = x*x - y*y + x0
                    y = 2*x*y + y0
                    x = xtemp
                    iteration += 1
                field[px1,py1] = iteration
        return field

    @njit(cache=True)
    def palette(im): #I snatched this from stack exchange
        im = 255 * (im / im.max())
        w, h = im.shape
        ret = empty((w, h, 3), dtype=uint8)
        ret[:, :, 0] = ret[:,:,1] = ret[:,:,2] = im
        return ret

    def center_of_cam(cam):
        x,y=zip(*cam)
        return [(max(x)+min(x))/2.0, (max(y)+min(y))/2.0]

    def translate(cam, amount):
        return [[p[0]+amount[0],p[1]+amount[1]] for p in cam]

    def scalen(cam, amount, center):
        temp = translate(cam, [center[0]*-1, center[1]*-1])
        cam = [[p[0]*amount, p[1]*amount] for p in cam]
        return translate(cam, center)

    RESOLUTION = [1050, 600]
    #Suggest a 1.75 : 1 ratio to maintain accuracy

    pygame.init()
    pygame.font.init()
    font = pygame.font.SysFont("timesnewroman", 32)
    timer = pygame.time.Clock()
    screen = pygame.display.set_mode(RESOLUTION)
    scale = 1
    samples = 32
    camera = [[-2.5,-1], [1,-1], [-2.5, 1], [1,1]]
    center = center_of_cam(camera)

    print("Loading... This may take quite some time.")

    cam_ = scalen(camera, scale, center)

    while True:
        delta = timer.tick()

        cam_ = scalen(camera, scale, center)

        screen.fill([0,0,0])

        keys = pygame.key.get_pressed()

        if keys[pygame.K_r]:
            samples += 16
        if keys[pygame.K_f]:
            samples -= 16
        if keys[pygame.K_q]:
            scale *= 1.05
        if keys[pygame.K_e]:
            scale *= 0.95

        if keys[pygame.K_w]:
            center[1] -= 0.1*scale
        if keys[pygame.K_s]:
            center[1] += 0.1*scale
        if keys[pygame.K_a]:
            center[0] -= 0.1*scale
        if keys[pygame.K_d]:
            center[0] += 0.1*scale

        if samples < 16:
            samples = 16

        brot_surf = pygame.surfarray.make_surface(
                        palette(
                            brot(
                                RESOLUTION[0],
                                RESOLUTION[1],
                                cam_[0][0],
                                cam_[1][0],
                                cam_[0][1],
                                cam_[2][1],
                                samples)
                            )
                        )

        screen.blit(
            brot_surf,
            [0,0]
        )

        if keys[pygame.K_t]:
            pygame.image.save(screen, f"{random.randint(10000,99999)}.png")

        screen.blit(font.render(f"{delta} ms, iters: {samples}", True, [255,0,0]), [0,0])
        screen.blit(
            pygame.transform.scale(
                font.render(f"cords: TL {cam_[0]} TR {cam_[1]} BL {cam_[2]} BR {cam_[3]}", True, [255,50,0]),
                [RESOLUTION[0],32]
            ),
            [0,50]
        )

        pygame.display.flip()

        events = pygame.event.poll()
        if events.type == pygame.QUIT:
            pygame.quit()
            break
except Exception as e:
    print(e)

input()
