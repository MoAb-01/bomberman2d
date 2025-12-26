
import pygame 
from src .controllers .inputs import InputStrategy 

class Entity (pygame .sprite .Sprite ):
    def __init__ (self ,x ,y ,width ,height ,color ):
        super ().__init__ ()
        self .image =pygame .Surface ((width ,height ))
        self .image .fill (color )
        self .rect =self .image .get_rect (topleft =(x ,y ))
        self .speed =3 

class Powerup (pygame .sprite .Sprite ):
    def __init__ (self ,x ,y ,p_type ):
        super ().__init__ ()
        self .type =p_type 
        self .image =pygame .Surface ((30 ,30 ))


        if p_type =='BOMB_UP':self .image .fill ((50 ,50 ,50 ))
        elif p_type =='FIRE_UP':self .image .fill ((255 ,100 ,50 ))
        elif p_type =='SPEED_UP':self .image .fill ((100 ,200 ,255 ))
        elif p_type =='GHOST':self .image .fill ((200 ,200 ,200 ))


        pygame .draw .rect (self .image ,(255 ,255 ,255 ),(0 ,0 ,30 ,30 ),2 )

        font =pygame .font .Font (None ,24 )
        text =font .render (p_type [0 ],True ,(255 ,255 ,255 ))
        self .image .blit (text ,(8 ,8 ))

        self .rect =self .image .get_rect (topleft =(x +5 ,y +5 ))

class Player (Entity ):
    def __init__ (self ,x ,y ,color ,input_strategy :InputStrategy ,player_id ):
        super ().__init__ (x ,y ,30 ,30 ,color )
        self .input_strategy =input_strategy 
        self .player_id =player_id 


        self .bombs_count =1 
        self .active_bombs =0 
        self .bombs_remaining =5 

        self .explosion_range =2 
        self .base_speed =3 
        self .speed =3 
        self .inventory ={
        'BOMB':0 ,
        'FIRE':0 ,
        'SPEED':0 ,
        'GHOST':0 
        }
        self .available_types =['BOMB','FIRE','SPEED','GHOST']
        self .selected_index =0 
        self .selected_powerup =self .available_types [self .selected_index ]
        self .ghost_active =False 
        self .ghost_timer =0 
        self .active_effects =[]
        self .rect .x +=5 
        self .rect .y +=5 
        self .score =0 
        self .color =color 
        self .walk_frame =0 
        self .is_alive =True 
        self .image .set_colorkey ((0 ,0 ,0 ))
        self .image .fill ((0 ,0 ,0 ))

    def collect_powerup (self ,p_type ):
        if p_type =='BOMB_UP':
            from src .models .powerups import IncreaseBombCount 
            command =IncreaseBombCount ()
            command .execute (self )
            print (f"[POWERUP] Player {self .player_id } collected BOMB_UP: bombs_count={self .bombs_count }, bombs_remaining={self .bombs_remaining }")
        elif p_type =='FIRE_UP':
            self .inventory ['FIRE']=self .inventory .get ('FIRE',0 )+1 
        elif p_type =='SPEED_UP':
            self .inventory ['SPEED']=self .inventory .get ('SPEED',0 )+1 
        elif p_type =='GHOST':
            self .inventory ['GHOST']=self .inventory .get ('GHOST',0 )+1 

        if p_type !='BOMB_UP':
            print (f"[POWERUP] Player {self .player_id } collected {p_type }, inventory: {self .inventory }")

    def cycle_selection (self ):
        self .selected_index =(self .selected_index +1 )%5 
        if self .selected_index <4 :
            self .selected_powerup =self .available_types [self .selected_index ]
        else :
            self .selected_powerup =None 

    def activate_selection (self ):
        if not self .selected_powerup :return 

        count =self .inventory .get (self .selected_powerup ,0 )
        if count >0 :
            self .inventory [self .selected_powerup ]-=1 
            if self .selected_powerup =='BOMB':
                from src .models .powerups import IncreaseBombCount 
                command =IncreaseBombCount ()
                command .execute (self )
                self .active_effects .append ((command ,600 ))
            elif self .selected_powerup =='FIRE':
                from src .models .powerups import IncreaseRange 
                command =IncreaseRange ()
                command .execute (self )
                self .active_effects .append ((command ,600 ))
            elif self .selected_powerup =='SPEED':
                from src .models .powerups import SpeedUp 
                command =SpeedUp ()
                command .execute (self )
                self .active_effects .append ((command ,600 ))
            elif self .selected_powerup =='GHOST':
                self .ghost_active =True 
                self .ghost_timer =600 
                print (f"[GHOST] Player {self .player_id } activated ghost mode for 10 seconds")

    def reset (self ):
        self .is_alive =True 
        self .active_bombs =0 
        self .bombs_remaining =5 
        self .bombs_count =1 
        self .speed =3 
        self .explosion_range =2 
        self .inventory ={'BOMB':0 ,'FIRE':0 ,'SPEED':0 ,'GHOST':0 }
        self .selected_index =0 
        self .selected_powerup =self .available_types [self .selected_index ]
        self .index =0 
        self .ghost_active =False 
        self .ghost_timer =0 
        self .active_effects =[]
        if self .player_id ==1 :
            self .rect .topleft =(40 ,40 )
        else :
            self .rect .topleft =(720 ,520 )

    def can_plant_bomb (self ):
        if self .active_bombs >=self .bombs_count :
            return False 
        if self .bombs_remaining <=0 :
            return False 
        return True 

    def try_plant_bomb (self ):
        if self .input_strategy .planted_bomb ():
            return self .can_plant_bomb ()
        return False 

    def draw (self ,surface ):
        self .image .fill ((0 ,0 ,0 ))

        if not self .is_alive :
            center_x =15 
            pygame .draw .circle (self .image ,(100 ,100 ,100 ),(center_x ,15 ),12 )
            pygame .draw .line (self .image ,(255 ,255 ,255 ),(center_x -5 ,12 ),(center_x -2 ,18 ),2 )
            pygame .draw .line (self .image ,(255 ,255 ,255 ),(center_x -2 ,12 ),(center_x -5 ,18 ),2 )
            pygame .draw .line (self .image ,(255 ,255 ,255 ),(center_x +2 ,12 ),(center_x +5 ,18 ),2 )
            pygame .draw .line (self .image ,(255 ,255 ,255 ),(center_x +5 ,12 ),(center_x +2 ,18 ),2 )
            return 
        import math 
        leg_offset =int (math .sin (self .walk_frame *0.5 )*3 )
        hand_offset =int (math .cos (self .walk_frame *0.5 )*3 )
        center_x =15 

        body_color =(40 ,60 ,180 )
        pygame .draw .rect (self .image ,body_color ,(center_x -6 ,18 ,12 ,10 ),border_radius =4 )

        foot_color =(200 ,50 ,50 )
        pygame .draw .circle (self .image ,foot_color ,(center_x -5 ,28 +leg_offset ),4 )
        pygame .draw .circle (self .image ,foot_color ,(center_x +5 ,28 -leg_offset ),4 )

        hand_color =(255 ,255 ,255 )
        pygame .draw .circle (self .image ,hand_color ,(center_x -9 ,21 +hand_offset ),4 )
        pygame .draw .circle (self .image ,hand_color ,(center_x +9 ,21 -hand_offset ),4 )

        head_color =(255 ,220 ,200 )
        helmet_color =(240 ,240 ,240 )
        pygame .draw .circle (self .image ,helmet_color ,(center_x ,11 ),11 )

        pygame .draw .rect (self .image ,head_color ,(center_x -6 ,8 ,12 ,10 ),border_radius =5 )

        eye_color =(0 ,0 ,0 )
        pygame .draw .ellipse (self .image ,eye_color ,(center_x -4 ,10 ,3 ,6 ))
        pygame .draw .ellipse (self .image ,eye_color ,(center_x +1 ,10 ,3 ,6 ))

        pygame .draw .line (self .image ,(255 ,50 ,50 ),(center_x ,0 ),(center_x ,4 ),2 )
        pygame .draw .circle (self .image ,(255 ,0 ,0 ),(center_x ,0 ),2 )
        pygame .draw .polygon (self .image ,(255 ,100 ,100 ),[(center_x ,4 ),(center_x -3 ,7 ),(center_x +3 ,7 )])

    def update (self ,walls ):
        if not self .is_alive :return 

        if self .ghost_active :
            self .ghost_timer -=1 
            if self .ghost_timer %60 ==0 :
                print (f"[GHOST] Player {self .player_id } ghost timer: {self .ghost_timer //60 } seconds remaining")
            if self .ghost_timer <=0 :
                print (f"[GHOST] Player {self .player_id } ghost mode EXPIRED")
                self .ghost_active =False 

        for effect in self .active_effects [:]:
            command ,timer =effect 
            timer -=1 
            if timer <=0 :
                print (f"[POWERUP] Player {self .player_id } effect {type (command ).__name__ } EXPIRED")
                command .undo (self )
                self .active_effects .remove (effect )
            else :
                idx =self .active_effects .index (effect )
                self .active_effects [idx ]=(command ,timer )
                if timer %120 ==0 :
                    print (f"[POWERUP] Player {self .player_id } effect {type (command ).__name__ }: {timer //60 } seconds remaining")

        dx ,dy =self .input_strategy .get_movement ()
        if dx !=0 or dy !=0 :
            self .walk_frame +=1 
        else :
            self .walk_frame =0 

        self .draw (None )

        if self .ghost_active :
            self .image .set_alpha (150 )
        else :
            self .image .set_alpha (255 )

        CORNER_TOLERANCE =10 

        if dx !=0 :
            self ._move_single_axis (dx *self .speed ,0 ,walls )

        if dy !=0 :
            self ._move_single_axis (0 ,dy *self .speed ,walls )

    def _move_single_axis (self ,dx ,dy ,walls ):
        self .rect .x +=dx 
        self .rect .y +=dy 

        collision_occurred =False 
        hit_wall =None 

        for wall in walls :
            if self .rect .colliderect (wall .rect ):
                if getattr (wall ,'health',0 )==2 :
                     pass 

                is_passable =False 
                if self .ghost_active :
                     if getattr (wall ,'destructible',False ):
                          is_passable =True 
                          import pygame 
                          if pygame .time .get_ticks ()%500 <50 :
                              print (f"[GHOST] Player {self .player_id } passing through wall at ({wall .rect .x }, {wall .rect .y })")

                if not is_passable :
                    collision_occurred =True 
                    hit_wall =wall 
                    if dx >0 :self .rect .right =wall .rect .left 
                    if dx <0 :self .rect .left =wall .rect .right 
                    if dy >0 :self .rect .bottom =wall .rect .top 
                    if dy <0 :self .rect .top =wall .rect .bottom 


        if collision_occurred and hit_wall :
            SLIDE_SPEED =2 
            TOLERANCE =18 


            if dx !=0 :
                py =self .rect .centery 
                wy =hit_wall .rect .centery 
                diff =py -wy 
                if abs (diff )>10 and abs (diff )<TOLERANCE +15 :
                    if diff >0 :
                         self .rect .y +=SLIDE_SPEED 
                    else :
                         self .rect .y -=SLIDE_SPEED 

            if dy !=0 :
                px =self .rect .centerx 
                wx =hit_wall .rect .centerx 
                diff =px -wx 

                if abs (diff )>10 and abs (diff )<TOLERANCE +15 :
                    if diff >0 :
                         self .rect .x +=SLIDE_SPEED 
                    else :
                         self .rect .x -=SLIDE_SPEED 

    def try_plant_bomb (self ):
        if self .input_strategy .planted_bomb ()and self .active_bombs <self .bombs_count and self .bombs_remaining >0 :
            return True 
        return False 
