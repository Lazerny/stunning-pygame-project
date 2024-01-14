import pygame
import sys
import math
import random


class SpaceShip(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites)
        self.image = pygame.Surface((50, 50))
        self.image.fill((0, 255, 0))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a] and self.rect.x > 0:
            self.rect.x -= 5
        if keys[pygame.K_RIGHT] or keys[pygame.K_d] and self.rect.x < 600 - self.rect.width:
            self.rect.x += 5
        if keys[pygame.K_UP] or keys[pygame.K_w] and self.rect.y > 0:
            self.rect.y -= 5
        if keys[pygame.K_DOWN] or keys[pygame.K_s] and self.rect.y < 800 - self.rect.height:
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


# Инициализация Pygame
pygame.init()

# Определение размеров окна
width, height = 600, 800
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Космический корабль")
all_sprites = pygame.sprite.Group()
meteorite_group = pygame.sprite.Group()
bullets_group = pygame.sprite.Group()

# Создание объекта космического корабля
spaceship = SpaceShip(width // 2, height // 2)
meteors = [Meteorite() for _ in range(5)]
# Основной игровой цикл
running = True
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

    # Если есть столкновение, выводим "ААА" в консоль
    if spaceship_meteor_collisions:
        print("ААА")

    all_sprites.update()
    screen.fill((0, 0, 0))
    all_sprites.draw(screen)
    pygame.display.flip()
    pygame.time.Clock().tick(60)

pygame.quit()
sys.exit()
