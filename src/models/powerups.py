
from abc import ABC ,abstractmethod 
import pygame 


class PowerUpCommand (ABC ):
    @abstractmethod 
    def execute (self ,player ):
        pass 

    @abstractmethod 
    def undo (self ,player ):
        pass 

class IncreaseBombCount (PowerUpCommand ):
    def execute (self ,player ):
        if player .bombs_count <5 :
            player .bombs_count +=1 
        player .bombs_remaining +=5 

    def undo (self ,player ):
        if player .bombs_count >1 :
            player .bombs_count -=1 
        player .bombs_remaining =max (0 ,player .bombs_remaining -5 )

class IncreaseRange (PowerUpCommand ):
    def execute (self ,player ):
        player .explosion_range +=1 
    def undo (self ,player ):
        player .explosion_range =max (2 ,player .explosion_range -1 )

class SpeedUp (PowerUpCommand ):
    def execute (self ,player ):
        player .speed =min (player .speed +0.5 ,6.0 )
    def undo (self ,player ):
        player .speed =max (3.0 ,player .speed -0.5 )
class PowerUp (pygame .sprite .Sprite ):
    def __init__ (self ,x ,y ,command :PowerUpCommand ,color ):
        super ().__init__ ()
        self .image =pygame .Surface ((30 ,30 ))
        self .image .fill (color )
        self .rect =self .image .get_rect (topleft =(x +5 ,y +5 ))
        self .command =command 

    def apply (self ,player ):
        self .command .execute (player )
