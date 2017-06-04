import pygame
import numpy as np
import winsound
import threading

DOWN = np.array([0, 1])

GRAVITY = 0.2

screen_width = 600
screen_height = 800

class GameState:
    START = 0
    PLAY = 1
    DEAD = 2

class Potato:
    def __init__(self, sprite, position = np.array([0, 0])):
        scale = 100
        self.original_image = pygame.transform.scale(sprite, (scale, scale))
        self.image = pygame.transform.scale(sprite, (scale, scale))
        self.rect = self.image.get_rect()   # Used for drawing
        self.pos = position # Used for vector calculations
        self.rect.x, self.rect.y = self.pos[0], self.pos[1]
        self.dir = np.zeros(2)  # Potato direction vector
        self.angle = 0        # Potato rotation in degrees
        self.rot_speed = 5  # Speed of potato rotation (angles per frame)
        self.radius = scale/2.
        self.alive = True

    def click(self, mouse_pos):
        """ Returns True if potato was clicked, False otherwise """
        center = np.array([self.rect.centerx, self.rect.centery])
        line_to_center = center - mouse_pos
        # Take care of case where length of line is 0
        if line_to_center is np.zeros(2):
            line_to_center = np.array([0, -1])

        norm = np.linalg.norm(line_to_center)

        # Check if potato was clicked
        if norm <= self.radius:
            normalized_line = line_to_center / norm
            # Move up, even when clicked from above
            if normalized_line[1] > 0:
                normalized_line[1] *= -1
            
            # Change rotation depending on which side of potato was clicked
            rand = np.random.random_integers(3, 6)
            if normalized_line[0] > 0:
                self.rot_speed -= rand
            else:
                self.rot_speed += rand

            self.dir += normalized_line * 15
            return True
        return False

    def rotate(self):
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        x, y = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.pos = np.array([self.rect.x/1., self.rect.y/1.])

    def update(self):
        """ Returns True if potato hit a wall, False otherwise """
        if self.rect.y >= screen_height:
            self.alive = False
            return

        self.angle += self.rot_speed
        self.angle %= 360
        self.rotate()
        self.dir += DOWN * GRAVITY

        hit_wall = False

        new_pos = self.pos + self.dir
        new_rect = self.image.get_rect()
        new_rect.x, new_rect.y = int(new_pos[0]), int(new_pos[1])
        
        center = np.array([new_rect.centerx, new_rect.centery])
        # Wall collisions
        off_left = (center - self.radius)[0] <= 0
        off_right = (center + self.radius)[0] >= screen_width
        if off_left or off_right:
            hit_wall = True
            if off_left:
                self.dir[0] = np.abs(self.dir[0])
            elif off_right:
                self.dir[0] = -np.abs(self.dir[0])

            self.dir[0] *= 0.75 # Dampen horizontal velocity
            # Change rotation depending on which wall was hit
            rand = np.random.random_integers(3, 6)
            if (center - self.radius)[0] <= 0:
                self.rot_speed -= rand
            else:
                self.rot_speed += rand
            self.pos = new_pos
        else:
            self.pos += self.dir

        self.rect.x, self.rect.y = int(self.pos[0]), int(self.pos[1])
        self.center = self.pos + np.array([32, 32])
        return hit_wall

    def draw(self, surface):
        surface.blit(self.image, self.rect)

def play_sound(filename):
    """ Plays a sound file asynchronously """
    threading.Thread(target = winsound.PlaySound, args = (filename, winsound.SND_FILENAME)).start()

def main():
    pygame.init()
    pygame.mixer.pre_init(44100, -16, 1, 512)
    pygame.font.init()
    pygame.mixer.init()
    pygame.display.set_caption("Tuber Tapper 2017")
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((screen_width, screen_height))

    title_image_scale = np.array([300, 300])
    original_title_image = pygame.transform.scale(pygame.image.load("./sprites/logo.png"), title_image_scale)
    title_image = pygame.transform.scale(pygame.image.load("./sprites/logo.png"), title_image_scale)
    title_rect = title_image.get_rect()
    title_rect.centerx = screen_width/2.
    title_rect.centery = screen_height/3.

    # Load fonts
    regular_font = pygame.font.Font("./fonts/Fipps-Regular.otf", 20)
    big_font = pygame.font.Font("./fonts/Fipps-Regular.otf", 40)

    start_font = regular_font.render("CLICK TO START", False, (255, 255, 0))
    start_font_rect = start_font.get_rect()
    start_font_rect.centerx = screen_width / 2.
    start_font_rect.centery = screen_height * 4/5.

    retry_font = regular_font.render("CLICK TO RETRY", False, (255, 255, 0))
    retry_font_rect = retry_font.get_rect()
    retry_font_rect.centerx = screen_width / 2.
    retry_font_rect.centery = screen_height * 4/5.

    # Load sounds
    pop_sounds = ['./sounds/pop1.wav', './sounds/pop2.wav', './sounds/pop3.wav', './sounds/pop4.wav']
    bump_sounds = ['./sounds/bump1.wav', './sounds/bump2.wav', './sounds/bump3.wav', './sounds/bump4.wav']
    beep_sound = './sounds/beep.wav'

    score = 0

    beep_has_played = False

    game_state = GameState.START

    # Load potato things
    potato_sprite = pygame.image.load("./sprites/potato.png")
    potato = Potato(potato_sprite, np.array([screen_width/2., screen_height/4.]))

    pygame.display.set_icon(pygame.transform.scale(potato_sprite, (32, 32)))

    # Do potato things
    while True:
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            break

        screen.fill((0, 0, 0))

        # ------------- START SCREEN ----------------

        if game_state == GameState.START:
            # Gyrate!!!
            old_center = title_rect.center
            scaling = (np.sin(pygame.time.get_ticks() / 500.) + 3) / 3.
            image_scale_x = int(title_image_scale[0] * scaling)
            image_scale_y = int(title_image_scale[1] * scaling)
            title_image = pygame.transform.scale(original_title_image, (image_scale_x, image_scale_y))
            title_rect = title_image.get_rect()
            title_rect.center = old_center

            screen.blit(title_image, title_rect)
            screen.blit(start_font, start_font_rect)

            if event.type == pygame.MOUSEBUTTONDOWN:
                game_state = GameState.PLAY

        # ------------- POTATO HAS ACTIVATED ----------------

        elif game_state == GameState.PLAY:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if potato.click(np.array(pygame.mouse.get_pos())):
                    score += 1
                    play_sound(np.random.choice(pop_sounds))
                    
            hit_wall = potato.update()
            if hit_wall:
                play_sound(np.random.choice(bump_sounds))

            # Draw potato
            potato.draw(screen)
            
            # Draw score
            if potato.alive:
                font_surface = regular_font.render("SCORE: " + str(score), False, (255, 255, 255))
                screen.blit(font_surface, (0, 0))
            else:
                game_state = GameState.DEAD

        # ------------- POTATO HAS FALLEN ----------------

        elif game_state == GameState.DEAD:
            font_surface = big_font.render("FINAL SCORE: " + str(score), False, (255, 0, 255))
            screen.blit(font_surface, (50, screen_height / 2.5))
            screen.blit(retry_font, retry_font_rect)
            if not beep_has_played:
                play_sound(beep_sound)
                beep_has_played = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                game_state = GameState.PLAY
                potato = Potato(potato_sprite, np.array([screen_width/2., screen_height/4.]))
                score = 0
                beep_has_played = False

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()