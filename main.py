import pygame
import math
import random


class Spaceship(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__(all_sprites)
        self.image = pygame.Surface((width, height))
        self.image.fill((0, 128, 255))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.velocity = 0.2  # Скорость перемещения корабля
    def update(self):
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and self.rect.x > 0:
            self.rect.x -= self.velocity
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.rect.x < 600 - self.rect.width:
            self.rect.x += self.velocity
        if (keys[pygame.K_UP] or keys[pygame.K_w]) and self.rect.y > 0:
            self.rect.y -= self.velocity
        if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and self.rect.y < 800 - self.rect.height:
            self.rect.y += self.velocity


class Bullet(pygame.sprite.Sprite):
    def __init__(self, start_x, start_y, target_x, target_y):
        super().__init__(all_sprites, bullets)
        self.image = pygame.Surface((10, 10))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.x = start_x
        self.rect.y = start_y
        self.speed = 0.5

        # Расчет угла и направления движения пули
        angle = math.atan2(target_y - start_y, target_x - start_x)
        self.dx = self.speed * math.cos(angle)
        self.dy = self.speed * math.sin(angle)

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy


class Meteor(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites, meteors)
        self.image = pygame.Surface((50, 50))
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, 600)  # Случайная начальная позиция по горизонтали
        self.rect.y = random.randint(-200, -100)  # Случайная начальная позиция по вертикали
        self.speed = random.uniform(0.1, 0.3)  # Случайная скорость метеорита

    def update(self):
        self.rect.y += self.speed
        if self.rect.y > 800:  # Если метеорит достиг нижней границы, вернуть его наверх
            self.rect.y = random.randint(-200, -100)
            self.rect.x = random.randint(0, 600)


# Инициализация Pygame
pygame.init()
clock = pygame.time.Clock()
# Размеры окна
width, height = 600, 800
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Spaceship Game")

# Создание группы спрайтов
all_sprites = pygame.sprite.Group()

# Создание объекта Spaceship и добавление в группу
spaceship = Spaceship(400, 300, 50, 50)

# Создание группы для пуль
bullets = pygame.sprite.Group()

# Создание группы для метеоритов
meteors = pygame.sprite.Group()
for _ in range(5):
    meteor = Meteor()

# Основной игровой цикл
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Левая кнопка мыши
            mouse_x, mouse_y = pygame.mouse.get_pos()
            bullet = Bullet(spaceship.rect.x, spaceship.rect.y, mouse_x, mouse_y)

    # Очистка экрана
    # screen.fill((0, 0, 0))

    # Отрисовка всех спрайтов
    all_sprites.draw(screen)

    # Обновление всех спрайтов
    all_sprites.update()

    # Обновление экрана
    pygame.display.flip()
    clock.tick(60)

# Завершение Pygame
pygame.quit()
