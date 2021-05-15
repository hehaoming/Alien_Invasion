import json
import sys
from time import sleep
from typing import NoReturn

import pygame

from alien import Alien
from button import Button
from game_states import GameStats
from scoreboard import ScoreBoard
from setting import Settings
from ship import Ship
from bullet import Bullet


def check_high_scord(stats: GameStats, sb: ScoreBoard) -> NoReturn:
    """检查是否诞生了新的最高分"""
    if stats.score > stats.high_score:
        stats.high_score = stats.score
        sb.prep_high_score()


def check_aliens_bottom(ai_settings: Settings,
                        stats: GameStats,
                        screen: pygame.Surface,
                        ship: Ship,
                        aliens: pygame.sprite.Group,
                        bullets: pygame.sprite.Group,
                        sb: ScoreBoard) -> NoReturn:
    """检查是否有外星人到达了屏幕底端"""
    screen_rect = screen.get_rect()
    for alien in aliens.sprites():
        if alien.rect.bottom >= screen_rect.bottom:
            # 像飞船被撞到一样进行处理
            ship_hit(ai_settings, stats, screen, sb, ship, aliens, bullets)


def ship_hit(ai_settings: Settings,
             stats: GameStats,
             screen: pygame.Surface,
             sb: ScoreBoard,
             ship: Ship,
             aliens: pygame.sprite.Group,
             bullets: pygame.sprite.Group) -> NoReturn:
    """响应被外星人撞到的飞船"""
    if stats.ships_left > 0:
        # 将ships_left减1
        stats.ships_left -= 1

        # 更新记分牌
        sb.prep_ships()

        # 清空外星人列表和子弹列表
        aliens.empty()
        bullets.empty()

        # 创建一群新的外星人， 并将飞创放到屏幕低端中央
        create_fleet(ai_settings, screen, ship, aliens)
        ship.center_ship()

        # 暂停
        sleep(0.5)
    else:
        stats.game_active = False
        pygame.mouse.set_visible(True)


def get_number_rows(ai_settings: Settings, ship_height: int, alien_height: int) -> int:
    """计算屏幕可容纳多少行外星人"""
    available_space_y = (ai_settings.screen_height - (3 * alien_height) - ship_height)
    number_rows = int(available_space_y / (2 * alien_height))
    return number_rows


def get_number_aliens(ai_settings: Settings, alien_width: int) -> int:
    """计算每行可容纳多少个外星人"""
    available_space_x = ai_settings.screen_width - 2 * alien_width
    number_aliens_x = int(available_space_x / (2 * alien_width))
    return number_aliens_x


def create_alien(ai_settings: Settings,
                 screen: pygame.Surface,
                 aliens: pygame.sprite.Group,
                 alien_number: int,
                 row_number: int) -> NoReturn:
    """创建一个外星人并将其放在当前行"""
    alien = Alien(ai_settings, screen)
    alien_width = alien.rect.width
    alien.x = alien_width + 2 * alien_width * alien_number
    alien.rect.x = int(alien.x)
    alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
    aliens.add(alien)


def create_fleet(ai_settings: Settings, screen: pygame.Surface, ship: Ship, aliens: pygame.sprite.Group) -> NoReturn:
    """创建外星人群"""
    # 创建一个外星人， 并计算一行可容纳多少个外星人
    # 外星人间距为外星人宽度
    alien = Alien(ai_settings, screen)
    number_aliens_x = get_number_aliens(ai_settings, alien.rect.width)
    number_rows = get_number_rows(ai_settings, ship.rect.height, alien.rect.height)

    # 创建第一行外星人
    for row_number in range(number_rows):
        for alien_number in range(number_aliens_x):
            # 创建一个外星人并将其加入当前行
            create_alien(ai_settings, screen, aliens, alien_number, row_number)


def fire_bullet(ai_settings: Settings,
                screen: pygame.Surface,
                ship: Ship,
                bullets: pygame.sprite.Group) -> NoReturn:
    """如果还没有到达限制，就发射一颗子弹"""
    if len(bullets) < ai_settings.bullet_allowed:
        new_bullet = Bullet(ai_settings, screen, ship)
        bullets.add(new_bullet)


def check_keydown_events(event: pygame.event.Event,
                         ai_settings: Settings,
                         stats: GameStats,
                         screen: pygame.Surface,
                         ship: Ship,
                         bullets: pygame.sprite.Group) -> NoReturn:
    """响应按键"""
    if event.key == pygame.K_RIGHT:
        ship.moving_right = True
    elif event.key == pygame.K_LEFT:
        ship.moving_left = True
    elif event.key == pygame.K_SPACE:
        fire_bullet(ai_settings, screen, ship, bullets)
    elif event.key == pygame.K_q:
        with open('high_score.json', 'w') as file_object:
            json.dump(stats.high_score, file_object)
        sys.exit()


def check_keyup_events(event: pygame.event.Event,
                       ai_settings: Settings,
                       screen: pygame.Surface,
                       ship: Ship,
                       bullets: pygame.sprite.Group) -> NoReturn:
    """响应松开"""
    if event.key == pygame.K_RIGHT:
        ship.moving_right = False
    elif event.key == pygame.K_LEFT:
        ship.moving_left = False


def check_play_button(ai_settings: Settings,
                      stats: GameStats,
                      screen: pygame.Surface,
                      play_button: Button,
                      sb: ScoreBoard,
                      ship: Ship,
                      aliens: pygame.sprite.Group,
                      bullets: pygame.sprite.Group,
                      mouse_x: int,
                      mouse_y: int) -> NoReturn:
    """在晚间单机play按钮时开始新游戏"""
    button_clicked = play_button.rect.collidepoint(mouse_x, mouse_y)
    if button_clicked and not stats.game_active:
        # 重置游戏设置
        ai_settings.initialize_dynamic_settings()
        # 隐藏光标
        pygame.mouse.set_visible(False)
        # 重置游戏统计信息
        stats.reset_stats()
        stats.game_active = True

        # 重置记分牌图像
        sb.prep_score()
        sb.prep_high_score()
        sb.prep_level()
        sb.prep_ships()

        # 清空外星人列表和子弹列表
        aliens.empty()
        bullets.empty()

        # 创建一群新的外星人，并让飞船居中
        create_fleet(ai_settings, screen, ship, aliens)
        ship.center_ship()


def check_events(ai_settings: Settings,
                 stats: GameStats,
                 screen: pygame.Surface,
                 ship: Ship,
                 aliens: pygame.sprite.Group,
                 bullets: pygame.sprite.Group,
                 play_button: Button,
                 sb: ScoreBoard) -> NoReturn:
    """响应按键和鼠标事件"""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            check_keydown_events(event, ai_settings, stats, screen, ship, bullets)
        elif event.type == pygame.KEYUP:
            check_keyup_events(event, ai_settings, screen, ship, bullets)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            check_play_button(ai_settings, stats, screen, play_button, sb, ship, aliens, bullets, mouse_x, mouse_y)


def update_screen(ai_settings: Settings,
                  screen: pygame.Surface,
                  stats: GameStats,
                  sb: ScoreBoard,
                  ship: Ship,
                  aliens: pygame.sprite.Group,
                  bullets: pygame.sprite.Group,
                  play_button: Button) -> NoReturn:
    """更新屏幕上的图像，并切换到新屏幕"""

    # 每次循环时都重绘屏幕
    screen.fill(ai_settings.bg_color)

    # 在飞船和外星人后面重绘所有子弹
    for bullet in bullets.sprites():
        bullet.draw_bullet()
    ship.blitme()
    aliens.draw(screen)

    # 显示得分
    sb.show_score()

    # 如果游戏处于非活动状态，就绘制Play按钮
    if not stats.game_active:
        play_button.draw_button()

    # 让最近绘制的屏幕可见
    pygame.display.flip()


def update_bullets(ai_settings: Settings,
                   stats: GameStats,
                   screen: pygame.Surface,
                   sb: ScoreBoard,
                   ship: Ship,
                   aliens: pygame.sprite.Group,
                   bullets: pygame.sprite.Group) -> NoReturn:
    """更新子弹的位置，并删除已消失的子弹"""
    # 更新子弹的位置
    bullets.update()

    # 删除已消失的子弹
    for bullet in bullets.copy():
        if bullet.rect.bottom <= 0:
            bullets.remove(bullet)

    check_bullet_alien_collisions(ai_settings, stats, sb, aliens, bullets, screen, ship)


def check_bullet_alien_collisions(ai_settings: Settings,
                                  stats: GameStats,
                                  sb: ScoreBoard,
                                  aliens: pygame.sprite.Group,
                                  bullets: pygame.sprite.Group,
                                  screen: pygame.Surface,
                                  ship: Ship) -> NoReturn:
    """响应子弹和外星人的碰撞"""
    # 删除相应的子弹和外星人
    collisions = pygame.sprite.groupcollide(bullets, aliens, True, True)
    if collisions:
        for alien in collisions.values():
            stats.score += ai_settings.alien_points * len(alien)
            sb.prep_score()
        check_high_scord(stats, sb)
    if len(aliens) == 0:
        # 删除现有的子弹并创建一群外星人
        bullets.empty()
        ai_settings.increase_speed()

        # 提高等级
        stats.level += 1
        sb.prep_level()
        create_fleet(ai_settings, screen, ship, aliens)


def check_fleet_edges(ai_settings: Settings, aliens: pygame.sprite.Group) -> NoReturn:
    """有外星人到达边缘是采取相应的措施"""
    for alien in aliens.sprites():
        if alien.check_edges():
            change_fleet_direction(ai_settings, aliens)
            break


def change_fleet_direction(ai_settings: Settings, aliens: pygame.sprite.Group) -> NoReturn:
    """将整群外星人下移， 并改变他们的方向"""
    for alien in aliens.sprites():
        alien.rect.y += ai_settings.fleet_drop_speed
    ai_settings.fleet_direction *= -1


def update_aliens(ai_settings: Settings,
                  stats: GameStats,
                  screen: pygame.Surface,
                  aliens: pygame.sprite.Group,
                  ship: Ship,
                  bullets: pygame.sprite.Group,
                  sb: ScoreBoard) -> NoReturn:
    """更新外星人群中所有外星人的位置"""
    check_fleet_edges(ai_settings, aliens)
    aliens.update()

    # 检测外星人和飞船之间的碰撞
    if pygame.sprite.spritecollide(ship, aliens, False):
        ship_hit(ai_settings, stats, screen, sb, ship, aliens, bullets)

    # 检查是否有外星人到达了屏幕底端
    check_aliens_bottom(ai_settings, stats, screen, ship, aliens, bullets, sb)
