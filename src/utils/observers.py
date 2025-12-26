
from abc import ABC ,abstractmethod 
import pygame 


class Observer (ABC ):
    @abstractmethod 
    def update (self ,subject ):
        pass 




class Subject (ABC ):
    def __init__ (self ):
        self ._observers =[]
    def attach (self ,observer :Observer ):
        self ._observers .append (observer )

    def detach (self ,observer :Observer ):
        self ._observers .remove (observer )
    def notify (self ):
        for observer in self ._observers :
            observer .update (self )


class ScoreSystem (Subject ):
    def __init__ (self ):
        super ().__init__ ()
        self .scores ={}
    def update_score (self ,player_id ,points ):
        if player_id not in self .scores :
            self .scores [player_id ]=0 
        self .scores [player_id ]+=points 
        self .notify ()
    def get_score (self ,player_id ):
        return self .scores .get (player_id ,0 )



class ScoreboardUI (Observer ):
    def __init__ (self ,x ,y ,font =None ):
        self .font =font or pygame .font .Font (None ,36 )
        self .x =x 
        self .y =y 
        self .surfaces =[]

    def update (self ,scores ,players =None ,local_player_id =None ):
        pass 
        self .scores_data =scores if isinstance (scores ,dict )else scores .scores 
        self .players_ref =players 
        self .local_id =local_player_id 

    def draw (self ,surface ):
        if not hasattr (self ,'scores_data'):return 
        p1_score =self .scores_data .get (1 ,0 )
        p1_text =self .font .render (f"P1: {p1_score }",True ,(100 ,100 ,255 ))
        self ._draw_bg_text (surface ,p1_text ,(self .x ,self .y ))
        p2_score =self .scores_data .get (2 ,0 )
        p2_text =self .font .render (f"P2: {p2_score }",True ,(100 ,255 ,100 ))
        self ._draw_bg_text (surface ,p2_text ,(self .x +150 ,self .y ))
        if self .players_ref and self .local_id :
            local_player =next ((p for p in self .players_ref if p .player_id ==self .local_id ),None )
            if local_player :
                screen_h =surface .get_height ()
                screen_w =surface .get_width ()
                hud_x =20 if self .local_id ==1 else screen_w -320 
                hud_y =screen_h -100 
                hud_w =300 
                hud_h =80 
                s =pygame .Surface ((hud_w ,hud_h ))
                s .set_alpha (180 )
                s .fill ((30 ,30 ,30 ))
                surface .blit (s ,(hud_x ,hud_y ))
                pygame .draw .rect (surface ,(100 ,100 ,100 ),(hud_x ,hud_y ,hud_w ,hud_h ),2 )
                font_small =pygame .font .Font (None ,24 )
                b_color =(255 ,200 ,100 )
                active =local_player .active_bombs 
                limit =local_player .bombs_count 
                total =local_player .bombs_remaining 
                b_str =f"Bombs: {limit } ({total })"
                t_bombs =font_small .render (b_str ,True ,b_color )
                surface .blit (t_bombs ,(hud_x +10 ,hud_y +10 ))
                r_str =f"Fire: {local_player .explosion_range }"
                t_range =font_small .render (r_str ,True ,(255 ,100 ,50 ))
                surface .blit (t_range ,(hud_x +10 ,hud_y +30 ))
                sp_str =f"Speed: {local_player .speed /3.0 :.1f}x"
                t_speed =font_small .render (sp_str ,True ,(100 ,200 ,255 ))
                surface .blit (t_speed ,(hud_x +10 ,hud_y +45 ))
                g_str ="Ghost: ON"if local_player .ghost_active else "Ghost: OFF"
                g_col =(200 ,255 ,255 )if local_player .ghost_active else (100 ,100 ,100 )
                t_ghost =font_small .render (g_str ,True ,g_col )
                surface .blit (t_ghost ,(hud_x +10 ,hud_y +60 ))
                slots =['FIRE','SPEED','GHOST']
                slot_x =hud_x +130 
                slot_y =hud_y +10 
                slot_size =50 
                gap =10 

                for i ,p_type in enumerate (slots ):
                    px =slot_x +i *(slot_size +gap )
                    py =slot_y 
                    rect =pygame .Rect (px ,py ,slot_size ,slot_size )
                    pygame .draw .rect (surface ,(50 ,50 ,60 ),rect )
                    pygame .draw .rect (surface ,(100 ,100 ,120 ),rect ,1 )

                    color =(100 ,100 ,100 )
                    if p_type =='FIRE':color =(255 ,100 ,50 )
                    elif p_type =='SPEED':color =(100 ,200 ,255 )
                    elif p_type =='GHOST':color =(200 ,200 ,200 )

                    pygame .draw .circle (surface ,color ,(px +slot_size //2 ,py +slot_size //2 -5 ),10 )
                    count =local_player .inventory .get (p_type ,0 )
                    c_text =font_small .render (f"x{count }",True ,(255 ,255 ,255 ))
                    tx =px +(slot_size -c_text .get_width ())//2 
                    ty =py +slot_size -20 
                    surface .blit (c_text ,(tx ,ty ))
                    if local_player .selected_powerup ==p_type :
                        pygame .draw .rect (surface ,(180 ,180 ,180 ),rect ,3 )
                    if p_type =='GHOST'and local_player .ghost_active :
                         pygame .draw .rect (surface ,(200 ,255 ,255 ),rect ,2 )
                         t_act =font_small .render ("ON",True ,(255 ,255 ,255 ))
                         surface .blit (t_act ,(px +15 ,py -15 ))


    def _draw_bg_text (self ,surface ,text ,pos ):
        bg_rect =text .get_rect (topleft =pos )
        bg_rect .inflate_ip (10 ,6 )
        s =pygame .Surface ((bg_rect .width ,bg_rect .height ))
        s .set_alpha (150 )
        s .fill ((0 ,0 ,0 ))
        surface .blit (s ,bg_rect .topleft )
        surface .blit (text ,pos )

    def draw_modal (self ,surface ,highscores ,game_over =False ,winner_id =None ,progress =1.0 ,current_scores =None ,player_names =None ):
        alpha =int (180 *progress )
        overlay =pygame .Surface (surface .get_size ())
        overlay .set_alpha (alpha )
        overlay .fill ((0 ,0 ,0 ))
        surface .blit (overlay ,(0 ,0 ))
        if progress <0.1 :return 
        w ,h =surface .get_size ()
        cx ,cy =w //2 ,h //2 
        offset_y =int ((1.0 -progress )*-300 )

        if game_over :
            header_font =pygame .font .Font (None ,80 )
            sub_font =pygame .font .Font (None ,50 )
            t_main =header_font .render ("GAME OVER",True ,(255 ,255 ,255 ))
            r_main =t_main .get_rect (center =(cx ,cy -180 +offset_y ))
            surface .blit (t_main ,r_main )
            win_text ="TOTAL ANNIHILATION (DRAW)"
            win_color =(150 ,150 ,150 )
            if player_names :
                p1_name =player_names .get (1 ,'Player 1')
                p2_name =player_names .get (2 ,'Player 2')
            else :
                p1_name ,p2_name ='Player 1','Player 2'

            if winner_id ==1 :
                win_text =f"{p1_name .upper ()} DOMINATES!"
                win_color =(100 ,100 ,255 )
            elif winner_id ==2 :
                win_text =f"{p2_name .upper ()} WINS!"
                win_color =(255 ,100 ,100 )

            t_sub =sub_font .render (win_text ,True ,win_color )
            r_sub =t_sub .get_rect (center =(cx ,cy -120 +offset_y ))
            surface .blit (t_sub ,r_sub )
            if current_scores :
                p_rect =pygame .Rect (0 ,0 ,400 ,150 )
                p_rect .center =(cx ,cy +offset_y )
                pygame .draw .rect (surface ,(30 ,30 ,40 ),p_rect ,border_radius =10 )
                pygame .draw .rect (surface ,win_color ,p_rect ,2 ,border_radius =10 )
                score_font =pygame .font .Font (None ,40 )
                s1 =current_scores .get (1 ,0 )
                p1_display =p1_name if player_names else 'Player 1'
                t1 =score_font .render (f"{p1_display }: {s1 } pts",True ,(150 ,200 ,255 ))
                surface .blit (t1 ,(p_rect .x +40 ,p_rect .y +40 ))
                s2 =current_scores .get (2 ,0 )
                p2_display =p2_name if player_names else 'Player 2'
                t2 =score_font .render (f"{p2_display }: {s2 } pts",True ,(255 ,150 ,150 ))
                surface .blit (t2 ,(p_rect .x +40 ,p_rect .y +90 ))
            if pygame .time .get_ticks ()%1000 <600 :
                inst =pygame .font .Font (None ,30 ).render ("PRESS [SPACE] TO RETURN TO LOBBY",True ,(255 ,255 ,0 ))
                surface .blit (inst ,inst .get_rect (center =(cx ,cy +180 +offset_y )))

        else :
            title_surf =pygame .font .Font (None ,60 ).render ("Leaderboard",True ,(255 ,215 ,0 ))
            surface .blit (title_surf ,title_surf .get_rect (center =(cx ,cy -150 )))
            y =cy -50 
            for i ,(name ,score ,_ )in enumerate (highscores [:5 ]):
                t =self .font .render (f"{i +1 }. {name }: {score }",True ,(255 ,255 ,255 ))
                surface .blit (t ,t .get_rect (center =(cx ,y )))
                y +=40 
