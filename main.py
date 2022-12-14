import models.menu as menu
import models.level as level
import sys
import pygame as pg
import models.player as player


def escape():
    pg.quit()
    sys.exit()


width, height = 1920//2, 1080//2
sys_width, sys_height = pg.display.Info().current_w, pg.display.Info().current_h
scales = (sys_width/width, sys_height/height)
screen = pg.display.set_mode((sys_width, sys_height))
pg.mixer.music.load("music/Soundtrack.wav")
pg.mixer.music.play(-1)

WHITE = (200, 200, 200)

platforms = []
spikes = []
buttons = []
doors = []
old_platforms = []
old_spikes = []
old_buttons = []
old_doors = []
levels = 0
slide = False
need_slide = 0
count_wind = -1  # номер картинки ветра
tick = 0  # раз в сколько-то тиков меняется картинка ветра
collisable_obj = []
player_position = (0, 0, 0)
count_mouse = 0
knock_count = 0
flag_11 = True

level.read_data(screen, platforms, spikes, buttons, doors, 'docs/objects.json')

collisable_obj = platforms.copy()
collisable_obj.append(doors[0])

level.scale_objects(platforms, scales)
level.scale_objects(spikes, scales)
level.scale_objects(buttons, scales)
level.scale_objects(doors, scales)

for spike in spikes:
     spike.w += 2
     spike.h += 2

for platform in platforms:
    platform.w += 1
    platform.h += 1

title_dict = {
    0:"0.Нулёвка по общесосу",
    1:"1.Повторение-мать учения",
    2:"2.Илон Маск",
    3:"3.Возьми подсказку",
    4:"4.Just chill",
    5:"5.На ступень выше",
    6:"6.Dota-2",
    7:"7.Предел жизней кота",
    8:"8.Сникерсни - притормози",
    9:"9.Тут нет подвоха",
    10:"10.Отл(10)",
    11:"Конец?"
    }

hint_dict = {
    0:"Серьезно?!",
    1:"Просто сильнее",
    2:"SPACE-X",
    3:"ВОЗЬМИ ЁЁ!!!",
    4:"Руки прочь",
    5:"Будь выше жалкой двери",
    6:"Бедная мышка",
    7:"Нет, тут без Тейлора",
    8:"Может, проверить ту кнопочку?",
    9:"Ты даже не пытался",
    10:"Отл(10)",
    11:"Конец."
    }

hero = player.Player(0, (230+40)*scales[1], 40, 40, scales)
fps = 60
fpsClock = pg.time.Clock()
pg.init()

theme = menu.Theme("pic/background.png", sys_width, sys_height)

finished = False
left = False
right = False
up = False
down = False
space = False
mouse = False
last_mouse = False
secret = False


class Game:
    '''Конструктор класса Game
    Args:
    screen - экран
    platforms - список платформ
    spikes - список шипов
    '''
    def __init__(self, screen, up, down, right, left, space, mouse, secret):
        self.screen = screen
        self.up = up
        self.down = down
        self.right = right
        self.left = left
        self.space = space
        self.mouse = mouse
        self.secret = secret

    def start_game(self):
        '''Запуск игры'''
        global levels, old_platforms, old_spikes, old_buttons, old_doors, need_slide, slide, count_wind, tick,\
            player_position, knock_count, count_mouse, last_mouse, flag_11

        finished = False

        while not finished:
            self.screen.fill(WHITE)

            for spike in spikes:
                spike.draw()

            for spike in old_spikes:
                spike.draw()

            for button in buttons:
                button.draw()
                button.update(hero)

            for platform in platforms:
                platform.draw()

            for button in old_buttons:
                button.draw()
                button.update(hero)

            for platform in old_platforms:
                platform.draw()

            for door in old_doors:
                door.draw()

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    finished = True

                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_UP:
                        self.up = True
                    if event.key == pg.K_LEFT:
                        self.left = True
                    if event.key == pg.K_RIGHT:
                        self.right = True
                    if event.key == pg.K_SPACE:
                        self.space = True
                    if event.key == pg.K_UP:
                        self.up = True
                    if event.key == pg.K_BACKQUOTE:
                        self.secret = True

                elif event.type == pg.KEYUP:
                    if event.key == pg.K_UP:
                        self.up = False
                    if event.key == pg.K_LEFT:
                        self.left = False
                    if event.key == pg.K_RIGHT:
                        self.right = False
                    if event.key == pg.K_SPACE:
                        self.space = False

                elif event.type == pg.MOUSEBUTTONDOWN:
                    self.mouse = True

                elif event.type == pg.MOUSEBUTTONUP:
                    self.mouse = False

            for door in doors:
                door.draw()
                flag, player_position, knock_count, count_mouse, last_mouse = level.check_passage(
                    scales, hero, levels, buttons, self.space, player_position, doors, knock_count, self.mouse,
                    count_mouse, last_mouse, self.secret, platforms, spikes, old_platforms, old_spikes, old_buttons,
                    old_doors, flag_11)
                door.update(flag, scales[1])

            if levels == 11 and flag_11:
                platforms.append(level.Platform(screen,  300*scales[0], 330*scales[1], 600*scales[0], 600*scales[1]))
                flag_11 = False

            menu.pause_game.has_been_called = False
            menu.ask_hint.has_been_called = False
            menu.game_buttons(screen, scales, menu.pause_game, menu.ask_hint)
            menu.title(screen, scales, title_dict, levels)

            if menu.pause_game.has_been_called:
                break
            if menu.ask_hint.has_been_called:
                menu.hint(screen, scales, hint_dict, levels)
            collisable_obj = platforms.copy()

            if levels != 9:
                if len(doors) > 0:
                    collisable_obj.append(doors[0])

            hero.update(self.left, self.right, self.up, self.screen, collisable_obj, spikes)

            levels, old_platforms, old_spikes, old_buttons, old_doors, slide, need_slide = level.update_level(
                screen, need_slide, width, levels, hero, scales, platforms, spikes, buttons, doors, old_platforms,
                old_spikes, old_buttons, old_doors, slide)

            need_slide, count_wind, tick = level.level_slide(
                screen, slide, need_slide, width, height, scales,
                platforms, spikes, buttons, doors, old_platforms, old_spikes,
                old_buttons, old_doors, hero, count_wind, tick)
            pg.display.update()
            fpsClock.tick(fps)


game = Game(screen, up, down, right, left, space, mouse, secret)


while not finished:
    screen.fill(WHITE)
    theme.init_theme(screen)
    menu.start_buttons(screen, scales, game.start_game, escape)
    for event in pg.event.get():
        if event.type == pg.QUIT:
            finished = True
    pg.display.update()
    fpsClock.tick(fps)

pg.quit()