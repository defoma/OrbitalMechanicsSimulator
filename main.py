# dependencies
import pygame
import OMS
import math

# constants
BODIES = []
RESOLUTION = (480*2, 360*2)
G = 0.01
pygame.font.init()
SMALL_FONT = pygame.font.SysFont(None, 20)
CRITICAL_FACTOR = 10

# system setup
SYSTEM = OMS.SYSTEM

# initiates the pygame screen
pygame.init()
screen = pygame.display.set_mode(RESOLUTION, vsync=1)
pygame.display.set_caption("")
clock = pygame.time.Clock()

# initiates the camera and render systems
camera = OMS.Camera()
render = OMS.Render()

# creates the celestial bodies
for new in SYSTEM:
    OMS.new_body(BODIES, SYSTEM.index(new), new[0], new[1][0], new[1][1], new[1][2], new[1][3], new[1][4])

# main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # clear screen
    screen.fill((0, 0, 0))

    # body motion
    camera.motion(BODIES)
    for body in BODIES:
        body.tick(G, BODIES)
    for body in BODIES:
        collision = body.collide(BODIES)
        if collision is not None:
            if collision[0]:
                body_a = BODIES[collision[1]]
                body_b = BODIES[collision[2]]
                if CRITICAL_FACTOR > body_a.mass / body_b.mass > 1 / CRITICAL_FACTOR:
                    debris_number = 8
                    radians = math.radians(360 / debris_number)
                    average_mass = (body_a.mass + body_b.mass) / debris_number
                    average_radius = round(math.sqrt((body_a.radius ** 2 + body_b.radius ** 2) / debris_number))
                    average_hue = ((body_a.hue[0] + body_b.hue[0]) / 2, (body_a.hue[1] + body_b.hue[1]) / 2, (body_a.hue[2] + body_b.hue[2]) / 2)
                    for x in range(0, debris_number):
                        if body_a.mass + body_b.mass > 32:
                            position = [collision[3][0] + (body_a.radius + body_b.radius) * math.sin(x * radians), collision[3][1] + (body_a.radius + body_b.radius) * math.cos(x * radians)]
                            velocity = [collision[4][0] + 0.1 * math.sin(x * radians), collision[4][1] + 0.1 * math.cos(x * radians)]
                            OMS.new_body(BODIES, len(BODIES), "debris", average_mass, average_radius, average_hue, position, velocity)
                    body_a.delete()
                    body_b.delete()
                else:
                    if body_a.mass > body_b.mass:
                        body_a.mass += body_b.mass
                        body_a.radius = round(math.sqrt(body_a.radius ** 2 + body_b.radius ** 2))
                        BODIES[body_a.id] = body_a
                        body_b.delete()
                    elif body_a.mass < body_b.mass:
                        body_b.mass += body_a.mass
                        body_b.radius = round(math.sqrt(body_a.radius ** 2 + body_b.radius ** 2))
                        BODIES[body_b.id] = body_b
                        body_a.delete()
    render.render_bodies(BODIES, screen, camera, RESOLUTION)

    # widgets
    render.render_widgets(screen, clock, SMALL_FONT, RESOLUTION)

    # screen update
    pygame.display.flip()
    clock.tick(60)

    # test
    # print(f"{BODIES[0].mass}, {BODIES[0].radius}")

pygame.quit()
