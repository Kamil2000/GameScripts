import pygame
from pygame.locals import KEYDOWN, K_ESCAPE, K_UP, K_DOWN, K_LEFT, K_RIGHT, QUIT, K_RETURN
from collections import namedtuple
import math

pygame.init()

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

screen = pygame.display.set_mode([SCREEN_WIDTH,SCREEN_HEIGHT])
clock = pygame.time.Clock()

levels = [
    {
        "block_size" : (10, 50),
        "blocks" : [(40, 20),  (110, 20), (180, 20), (250, 20), (290, 60), (360, 60), (430, 60), (500, 60)],
        "ball_velocity" : 3
    },
    {
        "block_size" : (10, 40),
        "blocks" : [(40, 20), (100, 60), (160, 20), (220, 60), (280, 20), (340, 60), (400, 20), (460, 60), (520, 20)],
        "ball_velocity" : 3
    },
    {
        "block_size" : (10, 30),
        "blocks" : [(40, 20),  (110, 20), (180, 20), (250, 20), (290, 60), (360, 60), (430, 60), (500, 60)],
        "ball_velocity" : 3
    },
    {
        "block_size" : (10, 30),
        "blocks" : [(40, 20),  (100, 60), (160, 20), (220, 60), (280, 20), (340, 60), (400, 20), (460, 60), (520, 20)],
        "ball_velocity" : 4
    },
    {
        "block_size" : (10, 20),
        "blocks" : [
            (40, 20),  (100, 20), (160, 20), (220, 20), (280, 20), (340, 20), (400, 20), (460, 20), (520, 20),
            (40, 60),  (100, 60), (160, 60), (220, 60), (280, 60), (340, 60), (400, 60), (460, 60), (520, 60)
        ],
        "ball_velocity" : 4
    },
]

LEVELS_COUNT = len(levels)
bounce_sound = pygame.mixer.Sound('./sounds/bounce.wav')
metal_block_hit_sound = pygame.mixer.Sound('./sounds/metal-block-hit.wav')
def play_bounce_sound():
    bounce_sound.play()
def play_metal_block_hit_sound():
    metal_block_hit_sound.play()


class AppParams:
    def __init__(self):
        self.clear()

    def clear(self):
        self.score = 0
        self.lives = 3
        self.clear_lvl()

    def clear_lvl(self):
        self.blocks = pygame.sprite.Group()
        self.player = None
        self.ball = None
        self.playergrp = pygame.sprite.Group()

    def get_all_sprites(self):
        yield self.player
        yield self.ball
        for block in self.blocks:
            yield block

def normalize(velocity):
    length = math.sqrt(velocity[0]*velocity[0], velocity[1]*velocity[1])
    return (velocity[0]/length, velocity[1]/length)

class Player(pygame.sprite.Sprite):
    
    def __init__(self, app_params, x, y):
        pygame.sprite.Sprite.__init__(self) 
        self._size = (50, 10)
        self._curr_pos = (x,y)
        self.surf = pygame.image.load("images/belka.png").convert()
        self.surf = pygame.transform.scale(self.surf, self._size)
        self.rect =  self.surf.get_rect(center=self._curr_pos)

    def update(self, pressed_keys):
        if pressed_keys[K_LEFT]:
            self._curr_pos = (self._curr_pos[0] - 3, self._curr_pos[1])
        if pressed_keys[K_RIGHT]:
            self._curr_pos = (self._curr_pos[0] + 3, self._curr_pos[1])

        if self._curr_pos[0] < 0:
            self._curr_pos = (0, self._curr_pos[1])
        if self._curr_pos[0] > SCREEN_WIDTH-self._size[0]:
            self._curr_pos = (SCREEN_WIDTH-self._size[0], self._curr_pos[1])
        self.rect.update(self._curr_pos, self._size)


    def get_pos(self):
        return self._curr_pos
    def get_size(self):
        return self._size

class Block(pygame.sprite.Sprite):
 
    def __init__(self, app_params, x, y):
        pygame.sprite.Sprite.__init__(self)
        self._size = (40, 10)
        self._curr_pos = (x, y)
        self.surf = pygame.image.load("images/klocek.png").convert()
        self.surf = pygame.transform.scale(self.surf, self._size)
        self.rect = self.surf.get_rect(center=self._curr_pos)

    def set_color(self, color):
        self.surf.fill(color)

    def get_pos(self):
        return self._curr_pos
    def get_size(self):
        return self._size

class Ball(pygame.sprite.Sprite):

    def __init__(self, app_params, pos, velocity):
        self._size = (8, 8)
        self._initial_pos = pos
        self._initial_velocity = velocity
        self.surf = pygame.Surface(self._size)
        self.surf = pygame.image.load("images/pilka.png").convert()
        self.surf = pygame.transform.scale(self.surf, self._size)
        self._app_params = app_params
        self.clear()

    def clear(self):
        self._curr_pos = self._initial_pos
        self._velocity = self._initial_velocity
        self.rect = self.surf.get_rect(center=self._curr_pos)

    def process_physics_coll_player(self):
        player = pygame.sprite.spritecollideany(self, self._app_params.playergrp)
        if player == None:
            return
        if self._velocity[1] < 0:
            return
        curr_pos_x = self._curr_pos[0]
        player_pos = player.get_pos()
        player_size = player.get_size()
        diff_x = curr_pos_x + self._size[0]/2 - player_pos[0] - player_size[0]/2
        vel_factor = float(diff_x) /(player_size[0]/2)
        vel_factor = 0.7 if vel_factor > 0.7 else vel_factor
        vel_factor = -0.7 if vel_factor < -0.7 else vel_factor
        self._velocity = (abs(self._velocity[1])*vel_factor, -self._velocity[1])
        play_bounce_sound()

    def process_physics_coll_block(self, coll_block_cb):
        blocks = self._app_params.blocks
        ball = self._app_params.ball
        if pygame.sprite.spritecollideany(self, blocks):
            delete_block = pygame.sprite.spritecollideany(ball, blocks)
            delete_block.kill()
            self._velocity = (self._velocity[0], -self._velocity[1])
            self._app_params.score += 10
            play_metal_block_hit_sound()
            coll_block_cb()

    def process_physics(self, coll_block_cb, left_board_cb):
        self.process_physics_coll_player()
        self.process_physics_coll_block(coll_block_cb)
        self._curr_pos = (self._curr_pos[0] + self._velocity[0], self._curr_pos[1] + self._velocity[1])
        self.rect.update(self._curr_pos, self._size)
        if self._curr_pos[0] < 0:
            self._velocity = (abs(self._velocity[0]), self._velocity[1]) 
            play_bounce_sound()
        if self._curr_pos[0] > SCREEN_WIDTH - self._size[0]:
            self._velocity = (-abs(self._velocity[0]), self._velocity[1])
            play_bounce_sound()
        if self._curr_pos[1] < 0:
            self._velocity = (self._velocity[0], abs(self._velocity[1]))
            play_bounce_sound()
        if self._curr_pos[1] > SCREEN_HEIGHT:
            left_board_cb()

    def get_pos(self):
        return self._curr_pos
    def get_size(self):
        return self._size

pygame.display.set_caption("Arkanoid UJ")
app_params = AppParams()

def populate_app_params(app_params, level):
    print("loading level:" + str(level))
    app_params.clear_lvl()
    curr_lvl = levels[level]
    app_params.player = Player(app_params, 305,450)
    app_params.playergrp.add(app_params.player)
    block_size = curr_lvl["block_size"]
    for block_pos in curr_lvl["blocks"]:
        block = Block(app_params, block_pos[0], block_pos[1])
        app_params.blocks.add(block)
    app_params.ball = Ball(app_params, (200, 100), (0, curr_lvl["ball_velocity"]))  
    app_params.blocks.add(block)

MENU_INIT = 0
MENU_IN_GAME  = 1
MENU_GAME = 2
MENU_GAME_FINISHED = 3
MENU_HIGH_SCORES = 4 
class MenuParams:
    def __init__(self, app_params):
        self.running = True
        self.state = MENU_INIT
        self.item_selected = 0
        self.font = pygame.font.SysFont(None, 24)
        self.big_font = pygame.font.SysFont(None, 48)
        self.game_title = self.big_font.render("Arkanoid", True, (255,255,255))
        self.init_menu_items = self.map_menu([
            ['Play', self.init_menu_play_clicked, (150, 160)],
            ["High scores", self.init_menu_high_score_clicked, (150, 200)],
            ["Quit", self.init_menu_quit_clicked, (150, 240)],
        ])
        self.level = 0
        self.game_menu_title = self.big_font.render("Game Paused", True, (255, 255,255))
        self.game_menu_items = self.map_menu([
            ["Continue", self.game_menu_item_continue_clicked, (150, 160)],
            ["Exit", self.game_menu_item_exit_clicked, (150, 200)]
        ])
        self.state_event_handlers = {
            MENU_INIT: self.init_menu_handle_event,
            MENU_IN_GAME: self.game_menu_handle_event,
            MENU_GAME: self.game_handle_event,
            MENU_GAME_FINISHED: self.handle_event_move_to_main_menu,
            MENU_HIGH_SCORES: self.handle_event_move_to_main_menu,
        }
        self._app_params = app_params
        self.load_best_scores()
    def map_menu(self, menu_items):
        for item in menu_items:
            text = item.pop(0)
            item.insert(0, self.font.render(text, True, (255,255,255)))
            item.insert(0, self.font.render(text, True, (255, 0, 0)))
        return menu_items

    def init_menu_play_clicked(self):
        self.state = MENU_GAME
        self.item_selected = 0
        self._app_params.clear()
        populate_app_params(self._app_params, self.level)

    def init_menu_quit_clicked(self):
        self.running = False

    def init_menu_high_score_clicked(self):
        self.item_selected = 0
        self.state = MENU_HIGH_SCORES

    def init_menu_draw_item(self, idx):
        row = self.init_menu_items[idx]
        img = row[0] if idx != self.item_selected else row[1]
        pos = row[3]
        screen.blit(img, pos)

    def init_menu_get_item_fun(self, idx):
        return self.init_menu_items[idx][2]

    def init_menu_draw(self):
        screen.blit(self.game_title, (200, 80))
        for i in range(0, len(self.init_menu_items)):
            self.init_menu_draw_item(i)

    def init_menu_handle_event(self, event):
        if event.type != KEYDOWN:
            return
        if event.key == K_UP:
            self.item_selected -= 1
            if self.item_selected == -1:
                self.item_selected = 0
            return
        if event.key == K_DOWN:
            self.item_selected += 1
            if self.item_selected == len(self.init_menu_items):
                self.item_selected = len(self.init_menu_items) - 1
            return
        if event.key == K_RETURN:
            self.init_menu_get_item_fun(self.item_selected)()
            return

    def game_menu_draw_item(self, idx):
        row = self.game_menu_items[idx]
        img = row[0] if idx != self.item_selected else row[1]
        pos = row[3]
        screen.blit(img, pos)

    def game_menu_get_item_fun (self, idx):
        return self.game_menu_items[idx][2]

    def game_menu_draw(self):
        screen.blit(self.game_menu_title, (200, 80))
        for i in range(0, len(self.game_menu_items)):
            self.game_menu_draw_item(i)

    def game_menu_item_continue_clicked(self):
        self.state = MENU_GAME
        self.item_selected = 0
        return

    def game_menu_item_exit_clicked(self):
        self.state = MENU_INIT
        self.item_selected = 0
        app_params.clear()

    def game_menu_handle_event(self, event):
        if event.type != KEYDOWN:
            return
        if event.key == K_UP:
            self.item_selected -= 1
            if self.item_selected == -1:
                self.item_selected = 0
            return
        if event.key == K_DOWN:
            self.item_selected += 1
            if self.item_selected == len(self.init_menu_items):
                self.item_selected = len(self.init_menu_items) - 1
            return
        if event.key == K_RETURN:
            self.game_menu_get_item_fun(self.item_selected)()
            return
        if event.key == K_ESCAPE:
            self.game_menu_item_continue_clicked()
            return

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
            return
        if event.type != KEYDOWN:
            return
        handler = self.state_event_handlers.get(self.state)
        if handler != None:
            handler(event)

    def game_handle_event(self, ev):
        if ev.key == K_ESCAPE:
            self.state = MENU_IN_GAME

    def handle_event_move_to_main_menu(self, ev):
        if ev.key == K_ESCAPE:
            self.state = MENU_INIT

    def load_best_scores(self):
        try:
            with open("ArcaScores.txt") as f:
                self.best_scores = list(map(lambda x: int(x), f.readlines()))
        except FileNotFoundError:
            self.best_scores = []

    def save_best_scores(self):
        with open('ArcaScores.txt', 'w') as f:
            f.write("\n".join(map(lambda x: str(x), self.best_scores)))

    def update_best_scores(self):
        self.best_scores.append(self._app_params.score)
        self.best_scores.sort(reverse=True)
        self.best_scores = self.best_scores[0:9]

    def on_game_failed(self):
        self._app_params.lives-=1
        self._app_params.ball.clear()
        if self._app_params.lives == 0:
            self._app_params.clear_lvl()
            self.update_best_scores()
            self.state = MENU_GAME_FINISHED

    def on_block_deleted(self):
        if len(self._app_params.blocks) != 0:
            return
        if self.level == len(levels) - 1:
            self.update_best_scores()
            self.state = MENU_GAME_FINISHED
            return
        self.level+=1
        populate_app_params(self._app_params, self.level)

    def loop(self):
        game_over_txt = self.big_font.render('Game Over', True, (255,255,255))
        won_txt = self.big_font.render('You won', True, (255,255,255))

        while self.running:
            for ev in pygame.event.get():
                self.handle_event(ev)
            screen.fill((20,20,20))
            if self.state == MENU_GAME:
                level_number_txt = self.font.render("Level: " + str(self.level+1), True, (250, 0,0))
                lives_number_txt = self.font.render("Lives: " + str(self._app_params.lives), True, (0, 0, 250))
                score_number_txt = self.font.render("Score: " + str(self._app_params.score), True, (0, 250, 0))
                self._app_params.player.update(pygame.key.get_pressed())
                self._app_params.ball.process_physics(
                    coll_block_cb=self.on_block_deleted,
                    left_board_cb=self.on_game_failed)
                for obj in self._app_params.get_all_sprites():
                    if obj != None:
                        screen.blit(obj.surf, obj.rect)
                screen.blit(level_number_txt, (550, 120))
                screen.blit(lives_number_txt, (550, 140))
                screen.blit(score_number_txt, (550, 160))
            elif self.state == MENU_INIT:
                self.init_menu_draw()
            elif self.state == MENU_IN_GAME:
                self.game_menu_draw()
            elif self.state == MENU_GAME_FINISHED:
                screen.blit(game_over_txt if self._app_params.lives <= 0 else won_txt, (200, 200))
            elif self.state == MENU_HIGH_SCORES:
                best_scores_title = self.big_font.render('Best Scores', True, (250, 250, 250))
                screen.blit(best_scores_title, (250, 30))
                for i in range(0, len(self.best_scores)):
                    text = self.font.render(str(i+1) + ". " +str(self.best_scores[i]), True, (250, 250, 250))
                    screen.blit(text, (200, 80+i*20))

            clock.tick(60)
            pygame.display.flip()
        self.save_best_scores()



pygame.mixer.music.load("sounds/intro.ogg")
volume= 0.2
pygame.mixer.music.set_volume(volume)
pygame.mixer.music.play(-1)

menu = MenuParams(app_params)
menu.loop()
pygame.quit()
