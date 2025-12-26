"""
Strategy Pattern for Player Input.
Allows swapping between Keyboard, Joystick, or AI.
"""

from abc import ABC ,abstractmethod 
import pygame 
class InputStrategy (ABC ):
    @abstractmethod 
    def get_movement (self ):
        pass 
    @abstractmethod 
    def cycle_powerup (self ):
        pass 

class KeyboardInput (InputStrategy ):
    def __init__ (self ,key_map ):
        self .key_map =key_map 
        self .last_bomb_state =False 
        self .last_cycle_state =False 

    def get_movement (self ):
        keys =pygame .key .get_pressed ()
        dx ,dy =0 ,0 
        if keys [self .key_map ['up']]:
            dy =-1 
        if keys [self .key_map ['down']]:
            dy =1 
        if keys [self .key_map ['left']]:
            dx =-1 
        if keys [self .key_map ['right']]:
            dx =1 
        return dx ,dy 

    def planted_bomb (self ):
        keys =pygame .key .get_pressed ()
        current_state =keys [self .key_map ['bomb']]
        just_pressed =current_state and not self .last_bomb_state 
        self .last_bomb_state =current_state 

        return just_pressed 

    def cycle_powerup (self ):
        keys =pygame .key .get_pressed ()
        if 'cycle'not in self .key_map :return False 
        current_state =keys [self .key_map ['cycle']]
        just_pressed =current_state and not self .last_cycle_state 
        self .last_cycle_state =current_state 
        return just_pressed 

class Player2Keys (KeyboardInput ):
    def __init__ (self ):
        super ().__init__ ({
        'up':pygame .K_UP ,
        'down':pygame .K_DOWN ,
        'left':pygame .K_LEFT ,
        'right':pygame .K_RIGHT ,
        'bomb':pygame .K_RETURN ,
        'cycle':pygame .K_RSHIFT 
        })

class Player1Keys (KeyboardInput ):
    def __init__ (self ):
        super ().__init__ ({
        'up':pygame .K_w ,
        'down':pygame .K_s ,
        'left':pygame .K_a ,
        'right':pygame .K_d ,
        'bomb':pygame .K_SPACE ,
        'cycle':pygame .K_q 
        })
