#!/usr/bin/env python3
import random
import pygame as pg

### Representation of levels and ghosts
import level
import ghost

### some convenient color names
green  = pg.Color('#00FF00')
black  = pg.Color('black')
yellow = pg.Color('yellow')

from enum import Enum

class PacmanMode(Enum):
    ALIVE = 0
    DEAD = 1

class Pacman:
    def __init__(self, level_info : level.Level) -> None:
        self.level : level.Level = level_info    # the "level" is the current board
        self.score : int = 0                     # the score the Pac-Man has achieved
        self.pos : tuple[int,int] = (0, 0)       # the cell coordinates of the Pac-Man
        self.timer : float = 200
        self.direction : int = 0
        self.original_speed: float = 200
        self.power : bool = False
        self.power_dur : float = 15000
        self.power_time_left: float = 0
        ### The above are dummy values; the real values come from
        ### the following .reset() function
        self.reset()

    def reset(self) -> None:
        """Set the default values for the starting state of the Pac-Man."""
        (pr, pc, pw, ph) = self.level.pit
        self.pos  = (pr + ph, pc + pw // 2)
        self.score = 0
        self.direction = 0
        self.power = False
        self.timer = 200
        # maybe set other variables/attributes?

    def update(self, millis : int, ghosts : list[ghost.Ghost], power = 0) -> None:
        """Update the Pac-Man's state.

        millis: number of milliseconds that have elapsed since the last
                time update() was called
        ghosts: a list of all the ghost entities on the level. The Pac-Man
                should **not** modify the ghost entities, but is allowed
                to retrieve information about the ghosts"""
        self.timer -= millis
        
        if self.power : 
            self.power_time_left -= millis
            if self.power_time_left <= 0 : 
                self.power = False 
                self.timer = self.original_speed
            for g in ghosts : 
                g.blanch(self.power_time_left)
            
        if self.timer < 0 :             
            x,y = self.pos
            
            if self.direction == 'u' : 
                if self.level.can_enter((x-1,y)) : 
                    self.pos = x-1,y
            elif self.direction == 'd' : 
                if self.level.can_enter((x+1,y)) : 
                    self.pos = x+1,y
            elif self.direction == 'l' : 
                if self.level.can_enter((x,y-1)) : 
                    self.pos = x,y-1
            elif self.direction == 'r' :
                if self.level.can_enter((x,y+1)) :  
                    self.pos = x,y+1

            
            if self.level[self.pos] == level.Cell.PILL : 
                self.level[self.pos] = level.Cell.EMPTY
                self.score += 1
                
            if self.level[self.pos] == level.Cell.POWERPILL : 
                self.level[self.pos] = level.Cell.EMPTY
                self.score += 10
                self.power = True
                self.power_time_left = self.power_dur
                self.timer = self.original_speed / 2
                
            if self.power == False : 
                self.timer = self.original_speed
            else : 
                self.timer = self.original_speed / 2
                    


    def process_event(self, event : pg.event.Event) -> None:
        """Make the Pac-Man respond to the event, if relevant. It should
        only respond to the movement keys (WASD or the arrow keys)."""
        
        if event.type == pg.KEYDOWN : 
            if event.key in [pg.K_UP, pg.K_w] :
                self.direction = 'u'
            elif event.key in [pg.K_DOWN, pg.K_s] :
                self.direction = 'd'
            elif event.key in [pg.K_LEFT, pg.K_a] :
                self.direction = 'l'
            elif event.key in [pg.K_RIGHT, pg.K_d] : 
                self.direction = 'r'

        if event.type == pg.KEYUP :
            if (event.key in [pg.K_LEFT, pg.K_a] and self.direction == 'l') or \
               (event.key in [pg.K_RIGHT, pg.K_d] and self.direction == 'r') or \
               (event.key in [pg.K_UP, pg.K_w] and self.direction == 'u') or \
               (event.key in [pg.K_DOWN, pg.K_s] and self.direction == 'd'):
                self.direction = 0

    def render(self, window : pg.surface.Surface) -> None:
        """Draw the Pac-Man on the given window"""
        # scale params
        cw = window.get_width() // (self.level.width + 2)
        ch = window.get_height() // (self.level.height + 2)
        y = int((self.pos[0] + 1) * ch)
        x = int((self.pos[1] + 1) * cw)
        ## body, a yellow circle
        pg.draw.circle(window, yellow, (x + cw//2, y + ch//2), cw * 2 // 5)
        ## mouth, a black filled wedge
        pg.draw.polygon(window, black, [(x + cw//2, y + ch//2), (x + cw, y), (x + cw, y + ch)])
