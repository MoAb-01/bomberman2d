from abc import ABC ,abstractmethod 
from enum import Enum ,auto 
import pygame 
import os 

class IntroState (Enum ):
    FADING_IN =auto ()
    HOLDING =auto ()
    FADING_OUT =auto ()
    FINISHED =auto ()

class BaseIntroView (ABC ):
    def __init__ (self ,width ,height ):
        self .width =width 
        self .height =height 
        self .alpha =0.0 
        self .state =IntroState .FADING_IN 
        self .timer =0.0 
        self .FADE_SPEED =200.0 
        self .HOLD_DURATION =2.0 

    def update (self ,dt ):
        if self .state ==IntroState .FADING_IN :
            self .alpha +=self .FADE_SPEED *dt 
            if self .alpha >=255.0 :
                self .alpha =255.0 
                self .state =IntroState .HOLDING 
                self .timer =0.0 

        elif self .state ==IntroState .HOLDING :
            self .timer +=dt 
            if self .timer >=self .HOLD_DURATION :
                self .state =IntroState .FADING_OUT 

        elif self .state ==IntroState .FADING_OUT :
            self .alpha -=self .FADE_SPEED *dt 
            if self .alpha <=0.0 :
                self .alpha =0.0 
                self .state =IntroState .FINISHED 

    def is_finished (self ):
        return self .state ==IntroState .FINISHED 

    def draw (self ,screen ):

        content_surf =pygame .Surface ((self .width ,self .height ),flags =pygame .SRCALPHA )
        self .draw_content (content_surf )

        display_surf =pygame .Surface ((self .width ,self .height ))
        display_surf .fill ((0 ,0 ,0 ))
        display_surf .blit (content_surf ,(0 ,0 ))
        display_surf .set_alpha (int (self .alpha ))

        screen .blit (display_surf ,(0 ,0 ))

    @abstractmethod 
    def draw_content (self ,surface ):
        pass 


class AbdouIntroView (BaseIntroView ):
    def __init__ (self ,width ,height ):
        super ().__init__ (width ,height )
        self .assets_loaded =False 
        self ._load_assets ()

    def _load_assets (self ):

        self .bg_img =None 
        self .bomb_icon =None 
        try :

            self .title_font =pygame .font .SysFont ('consolas',70 ,bold =True )
            self .subtitle_font =pygame .font .SysFont ('consolas',50 ,bold =True )
            self .small_font =pygame .font .SysFont ('arial',20 )
        except :
             self .title_font =pygame .font .SysFont ('arial',60 )

    def draw_content (self ,surface ):
        cx ,cy =self .width //2 ,self .height //2 


        surface .fill ((5 ,5 ,8 ))

        grid_color =(0 ,51 ,0 )
        grid_spacing =40 

        for x in range (0 ,self .width ,grid_spacing ):
            pygame .draw .line (surface ,grid_color ,(x ,0 ),(x ,self .height ),1 )

        for y in range (0 ,self .height ,grid_spacing ):
            pygame .draw .line (surface ,grid_color ,(0 ,y ),(self .width ,y ),1 )
        text_gold =(255 ,215 ,0 )
        shadow_color =(0 ,0 ,0 )
        shadow_offset =3 

        t1_str ="ABDOU GAMES"
        t2_str ="PRODUCTIONS"

        t1 =self .title_font .render (t1_str ,True ,text_gold )
        t2 =self .title_font .render (t2_str ,True ,text_gold )

        t1_shadow =self .title_font .render (t1_str ,True ,shadow_color )
        t2_shadow =self .title_font .render (t2_str ,True ,shadow_color )

        y1 =cy -140 
        y2 =cy -70 

        surface .blit (t1_shadow ,(cx -t1 .get_width ()//2 +shadow_offset ,y1 +shadow_offset ))
        surface .blit (t2_shadow ,(cx -t2 .get_width ()//2 +shadow_offset ,y2 +shadow_offset ))

        surface .blit (t1 ,(cx -t1 .get_width ()//2 ,y1 ))
        surface .blit (t2 ,(cx -t2 .get_width ()//2 ,y2 ))

        bomb_cy =cy +40 

        fuse_color =(200 ,100 ,0 )
        start_pos =(cx ,bomb_cy -35 )
        mid_pos =(cx +10 ,bomb_cy -60 )
        end_pos =(cx +30 ,bomb_cy -70 )

        pygame .draw .line (surface ,fuse_color ,start_pos ,mid_pos ,4 )
        pygame .draw .line (surface ,fuse_color ,mid_pos ,end_pos ,4 )


        spark_color_center =(255 ,255 ,0 )
        spark_color_outer =(255 ,50 ,0 )
        sl =8 
        pygame .draw .line (surface ,spark_color_outer ,(end_pos [0 ]-sl ,end_pos [1 ]),(end_pos [0 ]+sl ,end_pos [1 ]),2 )
        pygame .draw .line (surface ,spark_color_outer ,(end_pos [0 ],end_pos [1 ]-sl ),(end_pos [0 ],end_pos [1 ]+sl ),2 )
        pygame .draw .circle (surface ,spark_color_center ,end_pos ,3 )

        radius =40 
        pygame .draw .circle (surface ,(0 ,0 ,0 ),(cx ,bomb_cy ),radius )
        pygame .draw .circle (surface ,(255 ,255 ,255 ),(cx ,bomb_cy ),radius ,3 )

        shine_rect =(cx -25 ,bomb_cy -25 ,15 ,10 )
        pygame .draw .ellipse (surface ,(255 ,255 ,255 ),shine_rect )
        text_cyan =(0 ,255 ,255 )
        t3 =self .subtitle_font .render ("BOMBERMAN 2D",True ,text_cyan )
        surface .blit (t3 ,(cx -t3 .get_width ()//2 ,cy +110 ))


        t4 =self .small_font .render ("© 2026",True ,(150 ,150 ,150 ))
        surface .blit (t4 ,(cx -t4 .get_width ()//2 ,self .height -30 ))
