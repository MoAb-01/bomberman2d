
import pygame 
import time 

class Bomb (pygame .sprite .Sprite ):
    def __init__ (self ):
        super ().__init__ ()
        self .image =pygame .Surface ((30 ,30 ))
        self .image .fill ((0 ,0 ,0 ))
        pygame .draw .circle (self .image ,(255 ,0 ,0 ),(15 ,15 ),5 )
        self .rect =self .image .get_rect ()
        self .frame_timer =0 
        self .owner =None 
        self .range =0 
        self .active =False 

    def spawn (self ,x ,y ,owner ):
        self .rect .topleft =(x +5 ,y +5 )
        self .owner =owner 
        self .range =owner .explosion_range 
        self .active =True 
        self .frame_timer =180 
        print (f"[BOMB] Spawned at ({x }, {y }) for Player {owner .player_id }, active={self .active }, frames={self .frame_timer }")

    def update (self ):
        if not self .active :
            return False 

        self .frame_timer -=1 


        if self .frame_timer %60 ==0 :
            print (f"[BOMB UPDATE] frames_left={self .frame_timer }, will_explode={self .frame_timer <=0 }")

        if self .frame_timer <=0 :
            self .active =False 
            print (f"[BOMB] EXPLODING!")
            return True 
        return False 

    def reset (self ):
        self .active =False 
        self .owner =None 

class Explosion (pygame .sprite .Sprite ):
    def __init__ (self ):
        super ().__init__ ()
        self .image =pygame .Surface ((40 ,40 ))
        self .image .fill ((255 ,165 ,0 ))
        self .rect =self .image .get_rect ()
        self .creation_time =0 
        self .duration =0.5 
        self .active =False 

    def spawn (self ,x ,y ,owner_id =None ):
        self .rect .topleft =(x ,y )
        self .creation_time =time .time ()
        self .active =True 
        self .owner_id =owner_id 

    def update (self ):
        if self .active and time .time ()-self .creation_time >=self .duration :
            self .active =False 
            return True 
        return False 

    def reset (self ):
        self .active =False 
        self .owner_id =None 
