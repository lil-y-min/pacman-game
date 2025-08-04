import math
import random
from copy import copy

import pygame as pg

import level

black = pg.Color('black')
white = pg.Color('white')
gray  = pg.Color('gray')

from enum import Enum

class GhostMode(Enum):
    NORMAL   = 0
    BLANCHED = 1
    SPOOKED  = 2
    PITTED   = 3

class Ghost:
    # number of milliseconds to go 1 cell
    speed = 200

    def __init__(self, level_info : level.Level, name : str, color : pg.Color) -> None:
        """Create ag ghost named `name` with color `color`"""
        self.level = level_info
        self.name = name
        self.color = color
        self.reset()

    def reset(self, pos : (tuple[int,int] | None) = None) -> None:
        """Reset the ghost: it goes back in the pit"""
        if pos is None: pos = self.random_pit_pos()

        ## mode
        self.mode : GhostMode = GhostMode.PITTED
        ## logical position
        self.pos : tuple[int,int] = pos
        ## intermediate display position
        self.dpos : tuple[float,float] = (self.pos[0], self.pos[1])
        ## direction of motion (in the pit)
        self.direction : tuple[int,int] = (0, 0)
        while self.direction == (0, 0):
            self.direction = (random.randint(-1, 1), random.randint(-1, 1))
        ## time left in the pit (if any)
        self.timer : int = random.randrange(2000, 5000)

    def random_pit_pos(self) -> tuple[int,int]:
        (pr, pc, pw, ph) = self.level.pit
        return (random.randint(pr + 1, pr + ph - 2),
                random.randint(pc + 1, pc + pw - 2))

    def blanch(self, duration : int) -> None:
        """Go into blanched mode because pacman swallowed a powerpill.
        The blanched effect will last for the given `duration`."""
        if self.mode in [GhostMode.PITTED, GhostMode.SPOOKED]: return
        self.mode = GhostMode.BLANCHED
        self.timer = duration

    def collide(self) -> int:
        """Handle a possible collision with the pacman."""
        if self.mode == GhostMode.BLANCHED:
            self.mode = GhostMode.SPOOKED
            self.timer = 0
            self.return_pos = self.random_pit_pos()
            return 50
        elif self.mode == GhostMode.NORMAL:
            return -1
        elif self.mode == GhostMode.SPOOKED:
            return 0
        else:
            print('BUG: {} collided with the pacman in mode {}!'.format(self.name, self.mode))
            raise Exception('Ghost.collide()')

    def update(self, millis : int) -> None:
        """Move the ghost"""
        if self.mode == GhostMode.PITTED:
            self.update_pitted(millis)
        elif self.mode == GhostMode.NORMAL:
            self.update_normal(millis)
        elif self.mode == GhostMode.BLANCHED:
            self.update_blanched(millis)
        elif self.mode == GhostMode.SPOOKED:
            self.update_spooked(millis)
        else:
            print('BUG: {} in unknown mode {}', self.name, self.mode)
            raise Exception('Ghost.update()')

    def update_spooked(self, millis : int) -> None:
        """Update in spooked mode"""
        (row, col) = self.dpos
        (r0, c0) = self.return_pos
        dist = math.sqrt((row - r0) ** 2 + (col - c0) ** 2)
        trav = 5 * millis / Ghost.speed
        if dist > trav:
            dr = (row - r0) / dist
            dc = (col - c0) / dist
            row -= dr * trav
            col -= dc * trav
            self.dpos = (row, col)
        else:
            self.reset((r0, c0))

    def update_blanched(self, millis : int) -> None:
        """Update in blanched mode"""
        self.timer -= millis
        if self.timer < 0: self.mode = GhostMode.NORMAL
        self.update_normal(millis, 2)

    def update_pitted(self, millis : int) -> None:
        """Move the ghost in the pit"""
        (pr, pc, pw, ph) = self.level.pit
        self.timer = max(self.timer - millis, 0)
        if self.timer == 0:
            self.mode = GhostMode.NORMAL
            self.pos = (pr - 1, pc + pw // 2)
            self.dpos = copy(self.pos)
            self.direction = random.choice([(0, 1), (0, -1)])
        else:
            row, col = self.dpos
            dr, dc = self.direction
            fac = millis / Ghost.speed / 3
            row += dr * fac
            col += dc * fac
            if row < pr: dr, row = 1, row + 2 * fac
            if row >= pr + ph - 1: dr, row = -1, row - 2 * fac
            if col < pc: dc, col = 1, col + 2 * fac
            if col >= pc + pw - 1: dc, col = -1, col - 2 * fac
            self.direction = (dr, dc)
            self.dpos = (row, col)

    def update_normal(self, millis : int, slowdown : int = 1) -> None:
        # try to go in the current direction
        (dr, dc) = self.direction
        nr = (self.pos[0] + dr) % self.level.height
        nc = (self.pos[1] + dc) % self.level.width
        if self.level.can_enter((nr, nc)):
            self.dpos = (self.dpos[0] + dr * millis / Ghost.speed / slowdown,
                         self.dpos[1] + dc * millis / Ghost.speed / slowdown)

            if abs(self.dpos[0] - self.pos[0]) >= 1 or \
               abs(self.dpos[1] - self.pos[1]) >= 1:
                old_pos = copy(self.pos)
                self.pos = ((self.pos[0] + self.direction[0]) % self.level.height,
                            (self.pos[1] + self.direction[1]) % self.level.width)
                self.dpos = copy(self.pos)
                forks = self.level.neighbors(self.pos, exclude=old_pos)
                if len(forks) > 0:
                    fork = random.choice(forks)
                    self.direction = (fork[0] - self.pos[0], fork[1] - self.pos[1])
        else:
            print('BUG: {} got stuck at {}'.format(self.name, self.pos))
            self.direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])

    def render(self, window : pg.surface.Surface) -> None:
        """Draw the ghost"""
        cw = window.get_width() // (self.level.width + 2)
        ch = window.get_height() // (self.level.height + 2)
        y = int((self.dpos[0] + 1) * ch) + ch // 2
        x = int((self.dpos[1] + 1) * cw) + cw // 2
        gw = cw * 4 // 5
        color = self.color
        body = True
        if self.mode == GhostMode.BLANCHED:
            color = gray
            if self.timer < 3000 and (self.timer // 300) % 2 == 0:
                color = self.color
        if self.mode == GhostMode.SPOOKED: body = False

        ## The ghost body
        if body:
            pg.draw.circle(window, color, (x, y), gw // 2)
            pg.draw.rect(window, color, (x - gw // 2, y, gw, ch//2))

        ## the ghost eyes
        pg.draw.circle(window, white, (x - gw//6, y - gw//6), gw//6)
        pg.draw.circle(window, white, (x + gw//6, y - gw//6), gw//6)
        pg.draw.circle(window, black, (x - gw//6, y - gw//7), gw//8)
        pg.draw.circle(window, black, (x + gw//6, y - gw//7), gw//8)
