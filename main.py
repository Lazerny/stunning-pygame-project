import os
import time
import pygame
import sys
import math
import random
import datetime as dt
from database import DatabaseManager

# Инициализация Pygame
pygame.init()
clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()
meteorite_group = pygame.sprite.Group()
bullets_group = pygame.sprite.Group()
width, height = 600, 800


class SpaceShip(pygame.sprite.Sprite):
    def __init__(self, x, y, count_bullets):
        super().__init__(all_sprites)
        self.frames = []
        sheet = pygame.transform.scale(load_image("spaceship-animation.png"), (400, 200))
        self.left = pygame.transform.scale(load_image('left.png'), (100, 200))
        self.right = pygame.transform.scale(load_image('right.png'), (100, 200))
        self.cut_sheet(sheet, 4, 1)
        self.cur_frame = 0
        self.counter = 0
        self.image = self.frames[self.cur_frame]

        self.mask = pygame.mask.from_surface(pygame.transform.scale(load_image('spaceship.png'), (100, 200)))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.on_reload = False
        if count_bullets == 0:
            self.add_magazine = False
            self.ammo = ''
        else:
            self.magazine = count_bullets
            self.add_magazine = True
            self.ammo = self.magazine
        self.last_up_time = 0  # Время последнего выстрела
        self.shoot_cooldown = 500  # Перезарядка в миллисекундах
        self.text_variable = f"{str(self.ammo)}"
        self.text_sprite = TextSprite(self.text_variable, self.rect.x, self.rect.y - 90, all_sprites,
                                      font_size=80, color=(0, 255, 0), font_path=None)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.text_sprite.update_text(str(self.ammo))
        keys = pygame.key.get_pressed()
        if any(keys):
            if self.counter == 5:
                self.cur_frame = (self.cur_frame + 1) % len(self.frames)
                self.image = self.frames[self.cur_frame]
                self.counter = 0
            self.counter += 1
        else:
            self.image = pygame.transform.scale(load_image('spaceship.png'), (100, 200))
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and self.rect.x > 0:
            self.rect.x -= 5
            self.text_sprite.rect.x -= 5
            self.image = self.left
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.rect.x < 600 - self.rect.width:
            self.rect.x += 5
            self.text_sprite.rect.x += 5
            self.image = self.right
        if (keys[pygame.K_UP] or keys[pygame.K_w]) and self.rect.y > 0:
            self.rect.y -= 5
            self.text_sprite.rect.y -= 5
        if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and self.rect.y < 800 - self.rect.height:
            self.rect.y += 5
            self.text_sprite.rect.y += 5

    def can_shot(self):
        if self.add_magazine:
            if self.ammo > 0 and not self.on_reload:
                self.ammo -= 1
                if self.ammo == 0:
                    self.last_up_time = pygame.time.get_ticks()
                return True
            return False
        return True

    def reload(self, current_time):
        if self.add_magazine:
            if self.ammo == 0 or self.on_reload:
                if current_time - self.last_up_time > self.shoot_cooldown:
                    self.on_reload = True
                    self.ammo += 1
                    self.last_up_time = current_time
                    if self.ammo == self.magazine:
                        self.on_reload = False


class Bullet(pygame.sprite.Sprite):
    def __init__(self, start_x, start_y, target_x, target_y):
        super().__init__(all_sprites, bullets_group)
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 0, 0), (10, 10), 5)  # Рисуем круг
        self.rect = self.image.get_rect()
        self.rect.center = (start_x, start_y)

        angle = math.atan2(target_y - start_y, target_x - start_x)
        self.dx = math.cos(angle) * 10
        self.dy = math.sin(angle) * 10

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        # Удаляем пулю, если она выходит за пределы экрана
        if not (0 <= self.rect.x <= width and 0 <= self.rect.y <= height):
            self.kill()


class Meteorite(pygame.sprite.Sprite):
    def __init__(self, meteor_animation_picture, meteor_animation_destroying):
        super().__init__(all_sprites, meteorite_group)
        self.radius = random.randint(40, 100)
        self.meteor_animation_picture = meteor_animation_picture
        self.meteor_animation_destroying = meteor_animation_destroying
        self.animation(self.meteor_animation_picture, self.radius * 8, self.radius * 4, 4, 2)
        self.killed = False
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, width - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        self.speed = random.randint(4, 9)
        self.heal = self.radius // 10 - 4
        self.text_variable = f"{self.heal + 1}"
        self.text_sprite = TextSprite(self.text_variable, self.rect.x + self.radius / 4, self.rect.y - 90, all_sprites,
                                      font_size=80, color=(255, 0, 0), font_path=None)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.rect.y += self.speed
        self.text_sprite.rect.y += self.speed
        self.text_sprite.update_text(str(self.heal + 1))
        if self.counter == 5:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
            self.counter = 0
        self.counter += 1
        if self.killed and self.cur_frame == 9:
            self.kill()
        # Удаляем метеорит, если он выходит за пределы экрана
        if self.rect.y > height:
            self.kill()
            self.text_sprite.kill()
            Meteorite(self.meteor_animation_picture, self.meteor_animation_destroying)

    def hit(self):
        self.heal -= 1
        if self.heal < 0:
            self.text_sprite.kill()
            return True

    def animation(self, sheet, sizex, sizey, columns, rows):
        self.frames = []
        sheet = pygame.transform.scale(sheet, (sizex, sizey))
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.counter = 0
        self.image = self.frames[self.cur_frame]

    def destroy(self):
        self.speed = 0
        x, y = self.rect.x, self.rect.y
        self.animation(self.meteor_animation_destroying, self.radius * 15, self.radius * 5, 5, 2)
        self.rect.x = x - self.radius // 2
        self.rect.y = y - self.radius // 2
        self.mask.clear()
        self.killed = True


class TextSprite(pygame.sprite.Sprite):
    def __init__(self, initial_text, x, y, group, font_size=60, color=(255, 255, 255), font_path=None):
        super().__init__(group)
        if font_path is None:
            font_path = pygame.font.get_default_font()
        self.font = pygame.font.Font(font_path, font_size)
        self.text = initial_text
        self.color = color
        self.update_image()
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def update_image(self):
        self.image = self.font.render(self.text, True, self.color)

    def update_text(self, new_text):
        self.text = new_text
        self.update_image()


class Button:
    def __init__(self, x, y, width_button, height_button, color, text, path_font=None, font_size=20):
        self.rect = pygame.Rect(x, y, width_button, height_button)
        self.color = color
        self.text = text
        self.can_click_flag = True
        if path_font is None:
            path_font = pygame.font.get_default_font()
        self.font = pygame.font.Font(path_font, font_size)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        if self.can_click_flag:
            return self.rect.collidepoint(pos)

    def can_click(self, flag):
        self.can_click_flag = flag
        return flag


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def history_screen():
    screen = pygame.display.set_mode((width, height))
    db = DatabaseManager()
    font_size = 30
    font = pygame.font.Font(None, font_size)

    # Заголовок таблицы
    title_text = font.render("Match history", True, (255, 255, 255))
    title_rect = title_text.get_rect(center=(width // 2, 50))

    query = "select id, time, meteors, hitrate, level from Results"
    results = db.fetch_data(query)[::-1]

    row_height = 40
    back_button = Button(50, 600, 100, 50, (102, 102, 0), '<-')
    next_button = Button(450, 600, 100, 50, (102, 102, 0), '->')
    go_button = Button(225, 700, 125, 50, (102, 102, 0), 'Вернуться')
    a = 0
    b = 10

    def show_result():
        y_position = 100
        for result in results[a:b]:
            result_text = font.render(
                f"{result[0]}. Time: {result[1]}s, Meteors: {result[2]}, Hit Rate: {result[3]}%, Level: {result[4]}",
                True,
                (255, 255, 255))
            result_rect = result_text.get_rect(center=(width // 2, y_position))
            screen.blit(result_text, result_rect)
            y_position += row_height

    show_result()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()
                if back_button.is_clicked(pos):
                    a += 10
                    b += 10
                elif next_button.is_clicked(pos):
                    a -= 10
                    b -= 10
                elif go_button.is_clicked(pos):
                    choose_level_screen()
        pygame.display.flip()
        screen.fill((0, 0, 0))
        screen.blit(title_text, title_rect)
        show_result()
        go_button.draw(screen)
        if back_button.can_click(b < len(results)):
            back_button.draw(screen)
        if next_button.can_click(a != 0):
            next_button.draw(screen)

    pygame.quit()
    sys.exit()


def choose_level_screen():
    all_sprites.empty()
    meteorite_group.empty()
    bullets_group.empty()
    # Определение размеров окна
    screen = pygame.display.set_mode((500, 500))
    pygame.display.set_caption("Космический корабль")
    lvl1 = Button(30, 100, 200, 100, (102, 102, 0), 'lvl1')
    lvl2 = Button(270, 100, 200, 100, (102, 102, 0), 'lvl2')
    lvl3 = Button(30, 300, 200, 100, (102, 102, 0), 'lvl3')
    lvl4 = Button(270, 300, 200, 100, (102, 102, 0), 'lvl4')
    history = Button(270, 15, 200, 50, (200, 102, 0), 'История матчей')
    buttons = [lvl1, lvl2, lvl3, lvl4, history]

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Если нажата левая кнопка мыши
                pos = pygame.mouse.get_pos()
                if lvl1.is_clicked(pos):
                    game(3, 0, 1)
                elif lvl2.is_clicked(pos):
                    game(5, 0, 2)
                elif lvl3.is_clicked(pos):
                    game(3, 5, 3)
                elif lvl4.is_clicked(pos):
                    game(5, 6, 4)
                elif history.is_clicked(pos):
                    history_screen()

        screen.fill((0, 0, 102))
        [i.draw(screen) for i in buttons]
        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


def score_screen():
    width, height = 600, 408
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Score")
    all_sprites1 = pygame.sprite.Group()

    db = DatabaseManager()
    query = '''SELECT time, meteors, HitRate from results WHERE id = (SELECT MAX(id) from results)'''
    res = db.fetch_data(query)[0]

    large_font_path = "ComicoroRu_0.ttf"

    text_variable = f"Время: {res[0]} с"
    text_variable1 = f"Разбито"
    text_variable2 = f"метеоритов: {res[1]}"
    text_variable3 = f"Процент"
    text_variable4 = f"попаданий: {res[2]}%"
    text_sprite = TextSprite(text_variable, 70, 40, all_sprites1, font_size=80, font_path=large_font_path)
    text_sprite1 = TextSprite(text_variable1, 70, 240, all_sprites1, font_size=80, font_path=large_font_path)
    text_sprite2 = TextSprite(text_variable2, 70, 300, all_sprites1, font_size=80, font_path=large_font_path)
    text_sprite3 = TextSprite(text_variable3, 70, 120, all_sprites1, font_size=80, font_path=large_font_path)
    text_sprite4 = TextSprite(text_variable4, 70, 180, all_sprites1, font_size=80, font_path=large_font_path)

    v = 200  # пикселей в секунду
    text_sprite.rect.x = -300
    text_sprite3.rect.x = -500
    text_sprite4.rect.x = -500
    text_sprite1.rect.x = -700
    text_sprite2.rect.x = -700

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                return
        if text_sprite.rect.x < 100:
            text_sprite.rect.x += v / 60
        if text_sprite1.rect.x < 100:
            text_sprite1.rect.x += v / 60
        if text_sprite2.rect.x < 100:
            text_sprite2.rect.x += v / 60
        if text_sprite3.rect.x < 100:
            text_sprite3.rect.x += v / 60
        if text_sprite4.rect.x < 100:
            text_sprite4.rect.x += v / 60

        screen.fill((0, 0, 102))
        all_sprites1.draw(screen)
        all_sprites1.update()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


def end_screen():
    width, height = 600, 300
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("End game")
    all_sprites1 = pygame.sprite.Group()

    sprite = pygame.sprite.Sprite(all_sprites1)
    sprite.image = pygame.image.load('data/GameOver.png')
    sprite.rect = sprite.image.get_rect()

    v = 200  # пикселей в секунду
    sprite.rect.x = -600
    # text_sprite.rect.x = 0
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                return
        if sprite.rect.x != 0:
            sprite.rect.x += v / 60
        screen.fill((0, 0, 255))
        all_sprites1.draw(screen)
        all_sprites1.update()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


def start_screen():
    screen = pygame.display.set_mode((500, 500))
    intro_text = ["Spaceship",
                  '',
                  "Управление:",
                  "стрелочки и wasd"]
    pygame.display.set_caption("Spaceship")
    fon = pygame.transform.scale(load_image('fon.jpg'), (500, 500))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                choose_level_screen()
        pygame.display.flip()
        clock.tick(60)


def game(count_meteors, reload, level):
    start = dt.datetime.now()
    count_meteorite_hit = 0
    count_meteorite = 0
    count_bullets = 0

    screen = pygame.display.set_mode((width, height))
    meteor_animation_picture = load_image("meteor-animation.png")
    meteor_animation_destroying = load_image("destroing-meteor.png")
    shoot_sound = pygame.mixer.Sound("data/bezzvuchnyiy-vyistrel-s-glushitelem.mp3")
    collision_sound = pygame.mixer.Sound("data/gluhoy-zvuk-ne-silnogo-stolknoveniya.mp3")
    end_sound = pygame.mixer.Sound('data/avtomobilnaya-avariya-kuski-otletayuschego-metalla-34427_giZ0TsQh.mp3')
    pygame.display.set_caption("Космический корабль")

    all_sprites.empty()
    meteorite_group.empty()
    bullets_group.empty()
    spaceship = SpaceShip(width // 2, height // 2, reload)
    [Meteorite(meteor_animation_picture, meteor_animation_destroying) for _ in range(count_meteors)]

    running = True
    time.sleep(0.5)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Если нажата левая кнопка мыши
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if spaceship.can_shot():
                    shoot_sound.play()
                    Bullet(spaceship.rect.centerx, spaceship.rect.centery, mouse_x, mouse_y)
                    count_bullets += 1

        # Обработка столкновений метеоритов и пуль
        bullet_meteor_collisions = pygame.sprite.groupcollide(bullets_group, meteorite_group, True, False,
                                                              pygame.sprite.collide_mask)

        # Пересоздаем метеориты после столкновения
        for meteorite in bullet_meteor_collisions.values():
            collision_sound.play()
            count_meteorite_hit += 1
            if meteorite[0].hit():
                meteorite[0].destroy()
                count_meteorite += 1
                Meteorite(meteor_animation_picture, meteor_animation_destroying)

        # Обработка столкновений метеоритов и корабля
        spaceship_meteor_collisions = pygame.sprite.spritecollide(spaceship, meteorite_group, False,
                                                                  pygame.sprite.collide_mask)

        # Если есть столкновение
        if spaceship_meteor_collisions:
            end_sound.play()
            duration_game = dt.datetime.now() - start
            db = DatabaseManager()
            query = '''INSERT INTO results (time, meteors, HitRate, level) VALUES (?, ?, ?, ?)'''
            params = (duration_game.seconds, count_meteorite,
                      round((count_meteorite_hit / count_bullets) * 100) if count_meteorite_hit != 0 else 0, level)
            db.execute_query(query, params)

            end_screen()
            score_screen()
            pygame.display.flip()
            start_screen()

        all_sprites.update()
        current_time = pygame.time.get_ticks()
        spaceship.reload(current_time)
        screen.fill((0, 0, 0))
        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    start_screen()
