import pygame
import math

# self, screen, clock, font, camera, resolution, G, bodies

def tpg_coords(x, y, resolution):
    return [x + resolution[0] / 2, -y + resolution[1] / 2]

def new_body(bodies: list, id_: int, name_: str, mass_: int, radius_: int, hue_: tuple, position_: list, velocity_: list):
    bodies.append(Body(id_=id_, name_=name_, mass_=mass_, radius_=radius_, hue_=hue_, position_=position_, velocity_=velocity_))

class Camera:

    def __init__(self):
        self.position = [0, 0]
        self.mod = [0, 0]
        self.zoom = 1
        self.focus = 0
        self.move = 4
        self.keydown = []
        self.prev_keydown = []

    def motion(self, bodies):
        self.keydown = pygame.key.get_pressed()
        if self.keydown[pygame.K_RIGHT]:
            self.mod[0] += self.move / self.zoom
        if self.keydown[pygame.K_LEFT]:
            self.mod[0] -= self.move / self.zoom
        if self.keydown[pygame.K_UP]:
            self.mod[1] += self.move / self.zoom
        if self.keydown[pygame.K_DOWN]:
            self.mod[1] -= self.move / self.zoom
        if self.keydown[pygame.K_RIGHTBRACKET] and not self.prev_keydown[pygame.K_RIGHTBRACKET]:
            self.focus += 1
            self.focus = self.focus % len(bodies)
            while not bodies[self.focus].active:
                self.focus += 1
                self.focus = self.focus % len(bodies)
        if self.keydown[pygame.K_LEFTBRACKET] and not self.prev_keydown[pygame.K_LEFTBRACKET]:
            self.focus -= 1
            self.focus = self.focus % len(bodies)
            while not bodies[self.focus].active:
                self.focus -= 1
                self.focus = self.focus % len(bodies)
        if self.keydown[pygame.K_BACKQUOTE]:
            self.mod = [0, 0]
        if self.keydown[pygame.K_EQUALS]:
            self.zoom *= 1.1
        if self.keydown[pygame.K_MINUS]:
            self.zoom /= 1.1

        self.prev_keydown = self.keydown

        self.position[0] = bodies[self.focus].position[0] + self.mod[0]
        self.position[1] = bodies[self.focus].position[1] + self.mod[1]

class Render:

    def __init__(self):
        pass

    def render_bodies(self, bodies, screen, camera, resolution):
        for body in bodies:
            pygame.draw.circle(screen, body.hue, tpg_coords(camera.zoom * (body.position[0] - camera.position[0]), camera.zoom * (body.position[1] - camera.position[1]), resolution), body.radius * camera.zoom)

    def render_widgets(self, screen, clock, font, resolution):
        fps_readout = font.render(str(round(clock.get_fps())), True, (255, 255, 255))
        screen.blit(fps_readout, (tpg_coords(10 - resolution[0] / 2, 20 - resolution[1] / 2, resolution)[0], tpg_coords(10 - resolution[0] / 2, 20 - resolution[1] / 2, resolution)[1]))

class Body:

    def __init__(self, id_, name_, mass_, radius_, hue_, position_, velocity_):
        self.id = id_
        self.name = name_
        self.mass = mass_
        self.radius = radius_
        self.hue = hue_
        self.position = position_
        self.velocity = velocity_
        self.acceleration = [0, 0]
        self.active = True

    def tick(self, G, bodies):
        self.accelerate(G, bodies)
        self.move()
        bodies[self.id] = self

    def accelerate(self, G, bodies):
        if self.active:
            self.acceleration = [0, 0]
            for body in bodies:
                if body != self and body.active:
                    x_dist = self.position[0] - body.position[0]
                    y_dist = self.position[1] - body.position[1]
                    acc_lin = G * body.mass / (x_dist ** 2 + y_dist ** 2)
                    acc_dir = math.atan2(x_dist, y_dist)
                    self.acceleration[0] -= acc_lin * math.sin(acc_dir)
                    self.acceleration[1] -= acc_lin * math.cos(acc_dir)

    def move(self):
        self.velocity[0] += self.acceleration[0]
        self.velocity[1] += self.acceleration[1]
        self.position[0] += self.velocity[0]
        self.position[1] += self.velocity[1]

    def collide(self, bodies):
        if self.active:
            for body in bodies:
                if body != self and body.active:
                    x_dist = self.position[0] - body.position[0]
                    y_dist = self.position[1] - body.position[1]
                    if math.sqrt(x_dist ** 2 + y_dist ** 2) < (self.radius + body.radius):
                        if self.id < body.id:
                            return [True, self.id, body.id, [(self.position[0] + body.position[0]) / 2, (self.position[1] + body.position[1]) / 2], [(self.velocity[0] + body.velocity[0]) / 2, (self.velocity[1] + body.velocity[1]) / 2]]
            return [False]

    def delete(self):
        self.name = "deprecated"
        self.mass = 0
        self.radius = 0
        self.hue = 0
        self.position = [0, 0]
        self.velocity = [0, 0]
        self.active = False

    def get_data(self):
        return [self.id, self.mass, self.radius, self.hue, self.position, self.velocity]

class Master:
    pass

SYSTEM = [
    ["a", [100000, 20, (255, 255, 0), [0, 0], [0, 0]]],
    ["b", [100, 4, (0, 255, 0), [50, 0], [0, 4.2]]],
    ["c", [100, 7, (255, 170, 0), [75, 0], [0, 3.9]]],
    ["d", [100, 6, (190, 0, 255), [100, 0], [0, 3.2]]],
    ["e", [100, 3, (0, 255, 255), [125, 0], [0, 2.5]]],
    ["f", [100, 5, (255, 0, 0), [150, 0], [0, 2.3]]]
]

REAL = [
    ["sol", [2.0e30, 7.0e8, (255, 255, 0), [0, 0], [0, 0]]],
    ["mercury", [3.3e23, 2.4e6, (0, 255, 0), [6.4e10, 0], [0, 4.8e4]]],
    ["venus", [4.9e24, 6.1e6, (255, 170, 0), [1.1e11, 0], [0, 3.5e3]]],
    ["earth", [6.0e24, 6.4e6, (190, 0, 255), [1.5e11, 0], [0, 3.0e3]]],
    ["mars", [6.4e23, 3.4e6, (0, 255, 255), [2.5e11, 0], [0, 2.4e3]]]
]
