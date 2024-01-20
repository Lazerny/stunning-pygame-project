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
        self.image = pygame.transform.scale(load_image('spaceship.png'), (88, 154))
        self.mask = pygame.mask.from_surface(self.image)
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
        self.shoot_cooldown = 500  # Перезарядка в миллисекундах (1 секунда)
        self.text_variable = f"{str(self.ammo)}"
        self.text_sprite = TextSprite(self.text_variable, self.rect.x, self.rect.y - 90, all_sprites,
                                      font_size=80, color=(0, 255, 0), font_path=None)

    def update(self):
        self.text_sprite.update_text(str(self.ammo))
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and self.rect.x > 0:
            self.rect.x -= 5
            self.text_sprite.rect.x -= 5
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.rect.x < 600 - self.rect.width:
            self.rect.x += 5
            self.text_sprite.rect.x += 5
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

        # Вычисляем угол и расстояние до цели
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
    def __init__(self):
        super().__init__(all_sprites, meteorite_group)
        self.radius = random.randint(40, 100)
        self.image = pygame.transform.scale(load_image('meteorite.png'), (self.radius * 2, self.radius * 2))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, width - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        self.speed = random.randint(6, 10)
        self.heal = self.radius // 10 - 4
        self.text_variable = f"{self.heal + 1}"
        self.text_sprite = TextSprite(self.text_variable, self.rect.x + self.radius / 4, self.rect.y - 90, all_sprites,
                                      font_size=80, color=(255, 0, 0), font_path=None)

    def update(self):
        self.rect.y += self.speed
        self.text_sprite.rect.y += self.speed
        self.text_sprite.update_text(str(self.heal + 1))
        # Удаляем метеорит, если он выходит за пределы экрана
        if self.rect.y > height:
            x = random.randint(0, width - self.rect.width)
            y = random.randint(-100, -40)
            speed = random.randint(3, 6)
            self.text_sprite.rect.x = x
            self.text_sprite.rect.y = y
            self.rect.x = x - self.radius / 4
            self.rect.y = y + 90
            self.speed = speed

    def hit(self):
        self.heal -= 1
        if self.heal < 0:
            self.text_sprite.kill()
            return True


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
    def __init__(self, x, y, width_button, height_button, color, text, path_font=None,  font_size=20):
        self.rect = pygame.Rect(x, y, width_button, height_button)
        self.color = color
        self.text = text
        if path_font is None:
            path_font = pygame.font.get_default_font()
        self.font = pygame.font.Font(path_font, font_size)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


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
    buttons = [lvl1, lvl2, lvl3, lvl4]
    # Основной игровой цикл
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Если нажата левая кнопка мыши
                if lvl1.is_clicked(pygame.mouse.get_pos()):
                    game(3, 0)
                elif lvl2.is_clicked(pygame.mouse.get_pos()):
                    game(5, 0)
                elif lvl3.is_clicked(pygame.mouse.get_pos()):
                    game(3, 5)
                elif lvl4.is_clicked(pygame.mouse.get_pos()):
                    game(5, 6)


        screen.fill((0, 0, 102))
        [i.draw(screen)for i in buttons]
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

        all_sprites1.draw(screen)
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
            # text_sprite.rect.x += v / 60
        all_sprites1.draw(screen)
        screen.fill((0, 0, 255))
        all_sprites1.draw(screen)
        all_sprites1.update()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


def start_screen():
    screen = pygame.display.set_mode((500, 500))
    intro_text = ["ЗАСТАВКА", "",
                  "Правила игры",
                  "Если в правилах несколько строк,",
                  "приходится выводить их построчно"]
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


def game(count_meteors, reload):
    start = dt.datetime.now()
    count_meteorite_hit = 0
    count_meteorite = 0

    count_bullets = 0
    # Определение размеров окна
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Космический корабль")
    # Создание объекта космического корабля
    all_sprites.empty()
    meteorite_group.empty()
    bullets_group.empty()
    spaceship = SpaceShip(width // 2, height // 2, reload)
    [Meteorite() for _ in range(count_meteors)]
    # Основной игровой цикл
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
                    Bullet(spaceship.rect.centerx, spaceship.rect.centery, mouse_x, mouse_y)
                    count_bullets += 1

        # Обработка столкновений метеоритов и пуль
        bullet_meteor_collisions = pygame.sprite.groupcollide(bullets_group, meteorite_group, True, False,
                                                              pygame.sprite.collide_mask)

        # Пересоздаем метеориты после столкновения
        for meteorite in bullet_meteor_collisions.values():
            count_meteorite_hit += 1
            if meteorite[0].hit():
                meteorite[0].kill()
                count_meteorite += 1
                Meteorite()

        # Обработка столкновений метеоритов и корабля
        spaceship_meteor_collisions = pygame.sprite.spritecollide(spaceship, meteorite_group, False,
                                                                  pygame.sprite.collide_mask)

        # Если есть столкновение
        if spaceship_meteor_collisions:
            # time.sleep(3)
            # нужна аниамция разрушения корабля
            for i in range(99999):
                # print('Анимация разрушения корабля')
                break
            a = dt.datetime.now() - start
            db = DatabaseManager()
            query = '''INSERT INTO results (time, meteors, HitRate) VALUES (?, ?, ?)'''
            params = (a.seconds, count_meteorite,
                      round((count_meteorite_hit / count_bullets) * 100) if count_meteorite_hit != 0 else 0)
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
