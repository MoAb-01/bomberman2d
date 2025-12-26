
from abc import ABC ,abstractmethod 
import random 
import pygame 
from src .utils .pathfinding import astar 

class EnemyState (ABC ):
    @abstractmethod 
    def update (self ,enemy ,game_map ,players ):
        pass 

class IdleState (EnemyState ):
    def update (self ,enemy ,game_map ,players ):
        enemy .idle_timer -=1 
        if enemy .idle_timer <=0 :
            enemy .state =PatrolState ()
        if hasattr (enemy ,'can_chase')and enemy .can_chase :
            for player in players :
                dist =pygame .math .Vector2 (enemy .rect .center ).distance_to (player .rect .center )
                if dist <200 :
                    enemy .state =ChaseState ()

class PatrolState (EnemyState ):
    def __init__ (self ):
        self .direction =random .choice ([(0 ,1 ),(0 ,-1 ),(1 ,0 ),(-1 ,0 )])
        self .switch_time =60 
    def update (self ,enemy ,game_map ,players ):
        dx ,dy =self .direction 
        enemy .move (dx ,dy ,game_map .walls )
        self .switch_time -=1 
        if self .switch_time <=0 or random .random ()<0.02 :
            self .direction =random .choice ([(0 ,1 ),(0 ,-1 ),(1 ,0 ),(-1 ,0 )])
            self .switch_time =60 
        if hasattr (enemy ,'can_chase')and enemy .can_chase :
            for player in players :
                dist =pygame .math .Vector2 (enemy .rect .center ).distance_to (player .rect .center )
                if dist <200 :
                    enemy .state =ChaseState ()

class ChaseState (EnemyState ):
    def update (self ,enemy ,game_map ,players ):

        target =None 
        min_dist =1000 
        for p in players :
            d =pygame .math .Vector2 (enemy .rect .center ).distance_to (p .rect .center )
            if d <min_dist :
                min_dist =d 
                target =p 

        if target :
            start =(int (enemy .rect .centery //40 ),int (enemy .rect .centerx //40 ))
            end =(int (target .rect .centery //40 ),int (target .rect .centerx //40 ))
            grid =[[0 for _ in range (game_map .tiles_x )]for _ in range (game_map .tiles_y )]
            for w in game_map .walls :
                if not w .destructible :
                     grid [int (w .rect .y //40 )][int (w .rect .x //40 )]=1 

            path =astar (grid ,start ,end )
            if len (path )>1 :
                next_node =path [1 ]


                target_y ,target_x =next_node 


                target_pixel_x =target_x *40 +20 
                target_pixel_y =target_y *40 +20 

                dx =0 
                dy =0 
                if target_pixel_x >enemy .rect .centerx :dx =1 
                elif target_pixel_x <enemy .rect .centerx :dx =-1 

                if target_pixel_y >enemy .rect .centery :dy =1 
                elif target_pixel_y <enemy .rect .centery :dy =-1 

                enemy .move (dx ,dy ,game_map .walls )
            else :

                 pass 

        if min_dist >300 :
            enemy .state =PatrolState ()

class Enemy (pygame .sprite .Sprite ):
    def __init__ (self ,x ,y ):
        super ().__init__ ()
        self .image =pygame .Surface ((30 ,30 ))
        self .image .fill ((255 ,50 ,50 ))
        pygame .draw .circle (self .image ,(255 ,255 ,255 ),(8 ,10 ),4 )
        pygame .draw .circle (self .image ,(255 ,255 ,255 ),(22 ,10 ),4 )
        pygame .draw .circle (self .image ,(0 ,0 ,0 ),(8 ,10 ),2 )
        pygame .draw .circle (self .image ,(0 ,0 ,0 ),(22 ,10 ),2 )
        pygame .draw .polygon (self .image ,(255 ,255 ,255 ),[(10 ,20 ),(15 ,25 ),(20 ,20 )])
        self .rect =self .image .get_rect (topleft =(x ,y ))
        self .speed =2 
        self .state =IdleState ()
        self .idle_timer =60 
        self .can_chase =True 

    def update (self ,walls ,players =None ):











        class MockMap :
            def __init__ (self ,w ):self .walls =w 




        if players is None :players =[]



        pass_map =MockMap (walls )

        try :
             self .state .update (self ,pass_map ,players )
        except :

             pass 

    def move (self ,dx ,dy ,walls ):
        self .rect .x +=dx *self .speed 

        for wall in walls :
            if self .rect .colliderect (wall .rect ):
                if dx >0 :self .rect .right =wall .rect .left 
                if dx <0 :self .rect .left =wall .rect .right 

        self .rect .y +=dy *self .speed 

        for wall in walls :
            if self .rect .colliderect (wall .rect ):
                if dy >0 :self .rect .bottom =wall .rect .top 
                if dy <0 :self .rect .top =wall .rect .bottom 
