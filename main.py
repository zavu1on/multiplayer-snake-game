import pygame
import colorama
from db import DB, Apple
from random import randint

# modules initialization
pygame.init()
colorama.init()


def get_random_color():
    return '#%02X%02X%02X' % (randint(0, 255), randint(0, 255), randint(0, 255))


# vars
player = DB(
    input('Input color (hex) or game will generate a random one: ') or get_random_color(),
    0,
    0,
    DB.parse_json([])
)
W = H = 1000
apples_manager = Apple()
win = pygame.display.set_mode((W, H))
dir = 'bottom'
head = [player.color, player.x, player.y]
body = []
apples = []

pygame.display.set_caption('MultiplayerSnakeGame')


def has_collision_with_enemy():
    for p in player.get_other_players():
        for _, bx, by in DB.parse_string(p[4]):
            if (head[0], head[1]) == (bx, by):
                return True
    return False


def death():
    player.delete()
    pygame.quit()
    print(colorama.Fore.RED + f'Вы проиграли, длинна вашего хвоста была - {len(body)}')
    while True:
        input()
        exit()


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            death()

    color, x, y = head

    # draw player
    win.fill((0, 4, 22))
    pygame.draw.rect(win, color, (x, y, 10, 10))
    for bcolor, bx, by in body:
        pygame.draw.rect(win, bcolor, (bx, by, 10, 10))

    # draw other players
    for p in player.get_other_players():
        pygame.draw.rect(win, p[1], (p[2], p[3], 10, 10))

        # draw other players' body
        for bcolor, bx, by in DB.parse_string(p[4]):
            pygame.draw.rect(win, bcolor, (bx, by, 10, 10))

    # animate snake
    body.insert(0, list(head))
    body.pop()

    # handle events
    key = pygame.key.get_pressed()
    if key[pygame.K_w] and dir != 'bottom':
        dir = 'top'
    if key[pygame.K_s] and dir != 'top':
        dir = 'bottom'
    if key[pygame.K_a] and dir != 'right':
        dir = 'left'
    if key[pygame.K_d] and dir != 'left':
        dir = 'right'

    # check death
    if (
            x + 20 == 0 or
            x - 10 == W or
            y + 20 == 0 or
            y - 10 == H or
            has_collision_with_enemy()
    ):
        death()

    # create apples
    apples = apples_manager.get_apples()

    # draw apples
    for id, ax, ay in apples:
        pygame.draw.rect(win, (255, 0, 0), (ax, ay, 10, 10))

        # check collision with apples
        if (ax, ay) == (x, y):
            apples_manager.remove_apple(id)
            body.append((color, ax, ay))

    # move snake
    if dir == 'top':
        y -= 10
    elif dir == 'bottom':
        y += 10
    elif dir == 'left':
        x -= 10
    elif dir == 'right':
        x += 10

    head = [color, x, y]

    player.update(x, y, DB.parse_json(body))
    pygame.display.update()
