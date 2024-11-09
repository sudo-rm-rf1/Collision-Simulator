import random
import sys
import pygame
from pygame.locals import QUIT, KEYDOWN, K_q, K_ESCAPE, K_l, MOUSEBUTTONDOWN


MAX_FPS = 30

SIZE = (1280, 720)



class Particle:

    def __init__(self, id=0, pos=(0, 0)):

        self.id = id
        self.s = [float(pos[0]), float(pos[1])]

        self.v = [random.uniform(-200, 200) for _ in range(2)]

        self.a = [0.0, 0.0]

        self.m = random.uniform(1, 256)

        self.r = 20



    def move(self, ms):

        for i in range(len(self.s)):

            self.v[i] += self.a[i] * (ms / 1000.0)

            self.s[i] += self.v[i] * (ms / 1000.0)



    def distance(self, p):

        return sum((x1 - x2) ** 2 for x1, x2 in zip(self.s, p.s)) ** 0.5
    


    def is_clicked(self, x, y):

        return ((self.s[0] - x) ** 2 + (self.s[1] - y) ** 2) ** 0.5 <= self.r


    def momentum_magnitude(self):

        return self.m * (self.v[0] ** 2 + self.v[1] ** 2) ** 0.5
    


    def kinetic_energy(self):

        return 0.5 * self.m * (self.v[0] ** 2 + self.v[1] ** 2)
    


    def velocity_magnitude(self):

        return (self.v[0] ** 2 + self.v[1] ** 2) ** 0.5
    




def dot_product(v1, v2):

    return sum(a * b for a, b in zip(v1, v2))





def scalar_product(v, n):

    return [i * n for i in v]





def normalize(v):

    m = sum(spam ** 2 for spam in v) ** 0.5

    return [spam / m for spam in v] if m != 0 else v




def main():

    pygame.init()

    window_surface = pygame.display.set_mode(SIZE)

    pygame.display.set_caption("Collision Simulator")

    main_clock = pygame.time.Clock()

    particles = []

    show_velocity_lines = False
    selected_particle_info = None


    while True:

        t = main_clock.tick(MAX_FPS)

        show_velocity_lines, selected_particle_info = handle_events(

            particles, window_surface, show_velocity_lines, selected_particle_info
        )




        for i, p1 in enumerate(particles):

            for p2 in particles[i + 1:]:

                d = p1.distance(p2)

                if d <= p1.r + p2.r:

                    N = normalize([p1.s[0] - p2.s[0], p1.s[1] - p2.s[1]])

                    d1 = 1.1 * ((p1.r + p2.r - d) * p2.m) / (p1.m + p2.m)

                    d2 = 1.1 * ((p1.r + p2.r - d) * p1.m) / (p1.m + p2.m)



                    p1.s[0] += N[0] * d1
                    p1.s[1] += N[1] * d1
                    p2.s[0] -= N[0] * d2
                    p2.s[1] -= N[1] * d2


                    T = [-N[1], N[0]]



                    v1n = dot_product(N, p1.v)

                    v1t = dot_product(T, p1.v)

                    v2n = dot_product(N, p2.v)

                    v2t = dot_product(T, p2.v)



                    u1n = v1n
                    v1n = ((v1n * (p1.m - p2.m) + 2.0 * p2.m * v2n) / (p1.m + p2.m))

                    v2n = ((v2n * (p2.m - p1.m) + 2.0 * p1.m * u1n) / (p2.m + p1.m))



                    p1.v = [a + b for a, b in zip(scalar_product(N, v1n), scalar_product(T, v1t))]

                    p2.v = [a + b for a, b in zip(scalar_product(N, v2n), scalar_product(T, v2t))]



        for p in particles:

            for i in range(2):

                if p.s[i] < p.r and p.v[i] < 0:

                    p.v[i] = -p.v[i]

                elif p.s[i] + p.r > SIZE[i] and p.v[i] > 0:

                    p.v[i] = -p.v[i]

            p.move(t)




        window_surface.fill((200, 200, 255))

        for p in particles:

            c = 256 - int(p.m)

            pygame.draw.circle(window_surface, (c, c, c), [int(coord) for coord in p.s], int(p.r))

            if show_velocity_lines:

                velocity_magnitude = p.velocity_magnitude()

                line_length = velocity_magnitude / 10

                end_pos = [int(p.s[0] + p.v[0] * line_length), int(p.s[1] + p.v[1] * line_length)]

                pygame.draw.line(window_surface, (0, 0, 0), [int(coord) for coord in p.s], end_pos, 2)




        if selected_particle_info:

            display_particle_info(window_surface, selected_particle_info)



        pygame.display.update()





def handle_events(particles, window_surface, show_velocity_lines, selected_particle_info):

    for event in pygame.event.get():

        if event.type == QUIT:

            terminate()

        elif event.type == KEYDOWN:

            if event.key in (K_ESCAPE, K_q):

                terminate()

            elif event.key == K_l:

                show_velocity_lines = not show_velocity_lines
        elif event.type == MOUSEBUTTONDOWN:

            x, y = event.pos

            for p in particles:

                if p.is_clicked(x, y):

                    selected_particle_info = {

                        "id": p.id,

                        "position": p.s,

                        "momentum_magnitude": p.momentum_magnitude(),

                        "kinetic_energy": p.kinetic_energy(),

                        "velocity_magnitude": p.velocity_magnitude(),

                    }

                    break
            else:

                new_particle = Particle(id=len(particles), pos=(x, y))

                particles.append(new_particle)

                selected_particle_info = None
    return show_velocity_lines, selected_particle_info




def display_particle_info(surface, info):

    font = pygame.font.Font(None, 36)

    text_y = 10

    for key, value in info.items():
        if isinstance(value, list):


            value_str = f"{key.capitalize()}: ({value[0]/100:.2f}, {value[1]:.2f})"

        else:


            value_str = f"{key.capitalize()}: {value:.2f}"

        text_surface = font.render(value_str, True, (0, 0, 0))

        surface.blit(text_surface, (10, text_y))

        text_y += 30





def terminate():

    pygame.quit()

    sys.exit()





if __name__ == '__main__':

    main()