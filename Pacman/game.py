#!/usr/bin/env python3

import pygame as pg
import level
import ghost
import pacman

black  = pg.Color('black')
pink   = pg.Color('pink')

from enum import Enum

class GameMode(Enum):
    ### The game can be in one of these modes
    TITLE_SCREEN = 0
    PLAYING = 1
    GAME_OVER = 2
    GAME_WON = 3
    DONE = -1

class Game:
    def __init__(self, level_info : level.Level, ghost_info : list[tuple[str, pg.Color]]) -> None:
        """Create a new game on a given level, with a given list of ghosts"""
        self.level = level_info
        self.ghosts : list[ghost.Ghost] = [ghost.Ghost(self.level, name, color) for (name, color) in ghost_info]
        self.pacman : pacman.Pacman = pacman.Pacman(self.level)
        self.state : GameMode = GameMode.TITLE_SCREEN
        self.title_font = pg.font.SysFont('Arial', 72, bold=True)
        self.info_font = pg.font.SysFont('Arial', 24)
        self.score_font = pg.font.SysFont('Courier', 20, bold=True)
        self.reset()

    def reset(self) -> None:
        """Reset on the current level"""
        self.level.reset()
        for g in self.ghosts: g.reset()
        self.pacman.reset()

    def is_done(self) -> bool:
        """Is the game over?"""
        return self.state == GameMode.DONE

    def process_event(self, event : pg.event.Event) -> None:
        """Handle user input"""
        if event.type == pg.QUIT:
            self.state = GameMode.DONE
            return

        if self.state == GameMode.TITLE_SCREEN:
            # only process enter and escape
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    self.state = GameMode.PLAYING
                elif event.key == pg.K_ESCAPE:
                    self.state = GameMode.DONE
        elif self.state == GameMode.PLAYING:
            if event.type in [pg.KEYDOWN, pg.KEYUP]:
                # event.key contains the code of the key that was pressed or released
                self.pacman.process_event(event)
        elif self.state == GameMode.GAME_OVER:
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.state = GameMode.DONE
                elif event.key == pg.K_RETURN:
                    self.reset()
                    self.state = GameMode.PLAYING
        elif self.state == GameMode.GAME_WON:
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.state = GameMode.DONE

    def update(self, millis : int) -> None:
        """Update the ghosts and the pacman. The parameter `millis` is the number of
        milliseconds since the last call to update()"""
        if self.state == GameMode.PLAYING:
            ## Update pacman
            self.pacman.update(millis, self.ghosts)

            ## Update ghosts
            for ghost in self.ghosts:
                ghost.update(millis)
                ## check for collisions
                if self.pacman.pos == ghost.pos:
                    score_delta = ghost.collide()
                    if score_delta < 0:
                        self.state = GameMode.GAME_OVER
                    else:
                        self.pacman.score += score_delta

            # Check if there are 0 pills
            if self.level.num_pills == 0:
                self.state = GameMode.GAME_WON

    def render_message(self, window : pg.surface.Surface, title : str, firstline : str, secondline : (str | None) = None) -> None:
        """Draw a centered box with text like at the start or the end of a level"""
        width = window.get_width()
        height = window.get_height()
        black_x = width // 5
        black_y = height // 5
        black_width = width - black_x * 2
        black_height = height - black_y * 2
        pg.draw.rect(window, black, (black_x, black_y, black_width, black_height))
        twin = self.title_font.render(title, True, pink)
        window.blit(twin, (black_x + black_width // 2 - twin.get_width() // 2,
                            black_y + black_height // 4))
        info_1 = self.info_font.render(firstline, True, pink)
        window.blit(info_1, (black_x + black_width // 2 - info_1.get_width() // 2,
                             black_y + black_height // 2))
        if secondline is not None:
            info_2 = self.info_font.render(secondline, True, pink)
            window.blit(info_2, (black_x + black_width // 2 - info_2.get_width() // 2,
                                 black_y + black_height // 2 + info_1.get_height() + 20))

    def render(self, window : pg.surface.Surface) -> None:
        """Draw the level, the ghosts, and the pacman"""
        self.level.render(window)

        for ghost in self.ghosts:
            ghost.render(window)

        self.pacman.render(window)

        if self.state in [GameMode.PLAYING, GameMode.GAME_OVER, GameMode.GAME_WON]:
            score = self.score_font.render('Score: {}'.format(self.pacman.score), True, pink)
            window.blit(score, (20, 5))

        if self.state == GameMode.TITLE_SCREEN:
            self.render_message(window, 'PAC-MAN', 'press RETURN to start', 'or ESCAPE to quit')
        elif self.state == GameMode.PLAYING:
            # TODO: anything else to render when game is playing
            pass
        elif self.state == GameMode.GAME_OVER:
            ## superpose a "game over" screen
            self.render_message(window, 'GAME OVER', 'press RETURN to retry', 'or ESCAPE to quit')
        elif self.state == GameMode.GAME_WON:
            ## superpose a "game over" screen
            self.render_message(window, 'YOU WON!', 'press ESCAPE to quit')


#-------------------------------------------------------------------------------
# Below is the main game loop

if __name__ == '__main__':
    pg.init()

    window = pg.display.set_mode((1000, 862))
    clock = pg.time.Clock()
    game = Game(level.level_1,
                [('Pinky', pg.Color('pink')), ('Inky', pg.Color('#00CCFF')),
                 ('Blinky', pg.Color('red')), ('Clyde', pg.Color('orange'))])

    millis = 0
    while not game.is_done():
        for event in pg.event.get():
            game.process_event(event)
        game.update(millis)
        window.fill(pg.Color('black'))
        game.render(window)
        millis = clock.tick(60)
        pg.display.flip()

    pg.quit()
