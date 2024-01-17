import os
import time
import pygame
import sys
import math
import random

# Инициализация Pygame
pygame.init()
clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()
meteorite_group = pygame.sprite.Group()
bullets_group = pygame.sprite.Group()
width, height = 600, 800


class SpaceShip(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites)
        self.image = pygame.Surface((50, 50))
        self.image.fill((0, 255, 0))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and self.rect.x > 0:
            self.rect.x -= 5
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.rect.x < 600 - self.rect.width:
            self.rect.x += 5
        if (keys[pygame.K_UP] or keys[pygame.K_w]) and self.rect.y > 0:
            self.rect.y -= 5
        if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and self.rect.y < 800 - self.rect.height:
            self.rect.y += 5


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
        x = random.randint(40, 100)
        self.image = pygame.Surface((x, x), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 255, 255), (20, 20), x)  # Рисуем круг
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, width - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        self.speed = random.randint(6, 10)

    def update(self):
        self.rect.y += self.speed
        # Удаляем метеорит, если он выходит за пределы экрана
        if self.rect.y > height:
            self.rect.x = random.randint(0, width - self.rect.width)
            self.rect.y = random.randint(-100, -40)
            self.speed = random.randint(2, 6)


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


def terminate():
    pygame.quit()
    sys.exit()


def end_screen():
    width, height = 600, 300
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("End game")

    all_sprites1 = pygame.sprite.Group()
    sprite = pygame.sprite.Sprite()
    sprite.image = pygame.image.load('data/GameOver.png')
    sprite.rect = sprite.image.get_rect()
    all_sprites1.add(sprite)
    v = 200  # пикселей в секунду
    sprite.rect.x = -600
    running = True
    clock = pygame.time.Clock()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                return
        if sprite.rect.x != 0:
            sprite.rect.x += v / 60
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
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                game()
        pygame.display.flip()
        clock.tick(60)


def game():
    # Определение размеров окна
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Космический корабль")
    # Создание объекта космического корабля
    all_sprites.empty()
    meteorite_group.empty()
    bullets_group.empty()
    spaceship = SpaceShip(width // 2, height // 2)
    [Meteorite() for _ in range(5)]
    for i in all_sprites:
        print(i)
    print()
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
                # Создаем пулю с координатами корабля и точки нажатия
                Bullet(spaceship.rect.centerx, spaceship.rect.centery, mouse_x, mouse_y)

        # Обработка столкновений метеоритов и пуль
        bullet_meteor_collisions = pygame.sprite.groupcollide(bullets_group, meteorite_group, True, True)

        # Пересоздаем метеориты после столкновения
        for meteor in bullet_meteor_collisions.values():
            Meteorite()

        # Обработка столкновений метеоритов и корабля
        spaceship_meteor_collisions = pygame.sprite.spritecollide(spaceship, meteorite_group, False)

        # Если есть столкновение
        if spaceship_meteor_collisions:
            # time.sleep(3)
            # нужна аниамция разрушения корабля
            for i in range(99999):
                # print('Анимация разрушения корабля')
                break
            end_screen()
            pygame.display.flip()
            start_screen()

        all_sprites.update()
        screen.fill((0, 0, 0))
        all_sprites.draw(screen)
        pygame.display.flip()
        pygame.time.Clock().tick(60)

    pygame.quit()
    sys.exit()


start_screen()
