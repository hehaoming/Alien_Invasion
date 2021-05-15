from typing import NoReturn

import pygame
from pygame.sprite import Group

import game_functions as gf
from alien import Alien
from setting import Settings
from ship import Ship
from game_states import GameStats
from button import Button
from scoreboard import ScoreBoard


def run_game() -> NoReturn:
    # 初始化游戏并创建一个屏幕对象
    pygame.init()
    ai_settings = Settings()
    screen = pygame.display.set_mode((ai_settings.screen_width, ai_settings.screen_height))
    pygame.display.set_caption('Alien Invasion')
    # 创建Play按钮
    play_button = Button(ai_settings, screen, "Play")

    # 创建一个用于统计信息的实例
    stats = GameStats(ai_settings)

    # 创建游戏记分牌
    sb = ScoreBoard(ai_settings, screen, stats)

    # 创建一艘飞船
    ship = Ship(ai_settings, screen)

    # 创建一个用于存储子弹的编组
    bullets = Group()

    # 创建一个外星人
    alien = Alien(ai_settings, screen)

    # 创建一个外星人编组
    aliens = Group()
    # 创建外星人群
    gf.create_fleet(ai_settings, screen, ship, aliens)

    # 开始游戏的主循环
    while True:

        gf.check_events(ai_settings, stats, screen, ship, aliens, bullets, play_button, sb)
        if stats.game_active:
            ship.update()
            gf.update_bullets(ai_settings, stats, screen, sb, ship, aliens, bullets)
            gf.update_aliens(ai_settings, stats, screen, aliens, ship, bullets, sb)
        gf.update_screen(ai_settings, screen, stats, sb, ship, aliens, bullets, play_button)


run_game()

