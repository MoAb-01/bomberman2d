
import pygame 
from src .models .entities import Entity 
from src .models .states import IdleState 

class Enemy (Entity ):
    def __init__ (self ,x ,y ,enemy_type ="dumb"):
        super ().__init__ (x ,y ,30 ,30 ,(255 ,0 ,0 ))
        self .state =IdleState ()
        self .idle_timer =60 
        self .speed =2 
        self .enemy_type =enemy_type 
        self .can_chase =(enemy_type =="smart")

        self .image .set_colorkey ((0 ,0 ,0 ))
        self .image .fill ((0 ,0 ,0 ))

        self .draw_enemy ()

    def draw_enemy (self ):
        self .image .fill ((0 ,0 ,0 ))
        if self .enemy_type =="dumb":
            color =(220 ,50 ,50 )
            pygame .draw .circle (self .image ,color ,(15 ,12 ),10 )
            pygame .draw .rect (self .image ,color ,(8 ,12 ,14 ,12 ))
            pygame .draw .rect (self .image ,(255 ,255 ,255 ),(10 ,8 ,4 ,8 ))
            pygame .draw .rect (self .image ,(255 ,255 ,255 ),(16 ,8 ,4 ,8 ))
            pygame .draw .rect (self .image ,(0 ,0 ,0 ),(12 ,10 ,2 ,4 ))
            pygame .draw .rect (self .image ,(0 ,0 ,0 ),(16 ,10 ,2 ,4 ))
        else :
            color =(0 ,200 ,200 )
            pygame .draw .circle (self .image ,color ,(15 ,10 ),12 )
            pygame .draw .polygon (self .image ,color ,[(3 ,20 ),(27 ,20 ),(15 ,30 )])

            pygame .draw .polygon (self .image ,(255 ,255 ,0 ),[(8 ,10 ),(12 ,14 ),(8 ,14 )])
            pygame .draw .polygon (self .image ,(255 ,255 ,0 ),[(22 ,10 ),(18 ,14 ),(22 ,14 )])

    def update (self ,game_map ,players ):
        self .draw_enemy ()
        self .state .update (self ,game_map ,players )

    def move (self ,dx ,dy ,walls ):
        if dx !=0 :
            self ._move_single_axis (dx *self .speed ,0 ,walls )
        if dy !=0 :
            self ._move_single_axis (0 ,dy *self .speed ,walls )

    def _move_single_axis (self ,dx ,dy ,walls ):
        self .rect .x +=dx 
        self .rect .y +=dy 
        for wall in walls :
            if self .rect .colliderect (wall .rect ):
                 if dx >0 :self .rect .right =wall .rect .left 
                 if dx <0 :self .rect .left =wall .rect .right 
                 if dy >0 :self .rect .bottom =wall .rect .top 
                 if dy <0 :self .rect .top =wall .rect .bottom 
