
import sys 
import pygame 
import random 

TILE_SIZE =40 

from src .core .game_manager import GameManager 
from src .database .repository import SqliteRepository 
from src .utils .pools import ObjectPool 
from src .models .factories import CityFactory ,ForestFactory ,DesertFactory 
from src .models .map import GameMap 
from src .models .entities import Player ,Powerup 
from src .models .bombs import Bomb ,Explosion 
from src .models .enemies import Enemy 
from src .controllers .inputs import Player1Keys 
from src .views .menus import MenuContainer ,MenuItem 
from src .views .auth_view import AuthView 
from src .views .lobby_view import LobbyView 
from src .views .intro_view import AbdouIntroView 
from src .utils .observers import ScoreSystem ,ScoreboardUI 
from src .controllers .network import GameServer ,GameClient 

class GameFacade :

    def __init__ (self ):
        pygame .init ()
        self .manager =GameManager ()
        self .screen =pygame .display .set_mode ((self .manager .screen_width ,self .manager .screen_height ))
        pygame .display .set_caption (self .manager .caption )
        self .repo =SqliteRepository ()
        self .clock =pygame .time .Clock ()

        self .score_system =ScoreSystem ()
        self .scoreboard =ScoreboardUI (10 ,10 )
        self .score_system .attach (self .scoreboard )
        self .score_system .update_score (1 ,0 )
        self .score_system .update_score (2 ,0 )
        self .game_over_time =0 
        self .winner_id =None 

        self .current_user =None 

        self .auth_view =AuthView (self .manager .screen_width ,self .manager .screen_height ,self .repo )
        self .lobby_view =LobbyView (self .manager .screen_width ,self .manager .screen_height )
        self .main_menu =None 
        self .server =None 
        self .client =None 
        self ._local_player_name =None 
        self .remote_player_name =None 
        self .map =None 
        self .players =pygame .sprite .Group ()
        self .enemies =pygame .sprite .Group ()
        self .bombs =pygame .sprite .Group ()
        self .explosions =pygame .sprite .Group ()
        self .powerups =pygame .sprite .Group ()
        self .bomb_pool =ObjectPool (Bomb )
        self .explosion_pool =ObjectPool (Explosion )

        self .anim_state ={
        'bomber_pos':(100 ,450 ),
        'bomb_pos':[100 ,450 ],
        'bomb_vel':[0 ,0 ],
        'is_throwing':False ,
        'particles':[]
        }
        self .anim_timer =0 
        self .frame_count =0 

        self .scroll_offset =[0 ,0 ]
        self .floor_tile =self ._create_floor_tile ()

        self .map_updates =[]
        self .intro =AbdouIntroView (self .manager .screen_width ,self .manager .screen_height )
        self .state ='INTRO'
        self .is_host =False 
        self .game_over =False 
        self .showing_scoreboard =False 

        self .lobby_view .reset ()

    @property 
    def local_player_name (self ):
        return self ._local_player_name 

    @local_player_name .setter 
    def local_player_name (self ,value ):
        self ._local_player_name =value 

    def _update_menu_animation (self ):

        if not self .anim_state ['is_throwing']:
            self .anim_timer +=1 
            if self .anim_timer >60 :
                self .anim_state ['is_throwing']=True 
                self .anim_state ['bomb_pos']=[100 ,430 ]
                self .anim_state ['bomb_vel']=[10 ,-15 ]
                self .anim_state ['particles']=[(x ,y ,vx ,vy ,life )for (x ,y ,vx ,vy ,life )in self .anim_state ['particles']if life >0 ]
                self .anim_timer =0 
        else :
            self .anim_state ['bomb_pos'][0 ]+=self .anim_state ['bomb_vel'][0 ]
            self .anim_state ['bomb_pos'][1 ]+=self .anim_state ['bomb_vel'][1 ]
            self .anim_state ['bomb_vel'][1 ]+=0.8 

            if self .anim_state ['bomb_pos'][1 ]>500 :
                self .anim_state ['is_throwing']=False 
                self ._spawn_menu_explosion (self .anim_state ['bomb_pos'][0 ],500 )
        for p in self .anim_state ['particles'][:]:
            p [0 ]+=p [2 ]
            p [1 ]+=p [3 ]
            p [4 ]-=1 
            if p [4 ]<=0 :
                self .anim_state ['particles'].remove (p )

    def _spawn_menu_explosion (self ,x ,y ):
        for _ in range (20 ):
            vx =random .uniform (-5 ,5 )
            vy =random .uniform (-10 ,-2 )
            self .anim_state ['particles'].append ([x ,y ,vx ,vy ,random .randint (30 ,60 )])

    def _draw_menu_animation (self ):
        self .screen .fill ((30 ,30 ,40 ))
        pygame .draw .rect (self .screen ,(50 ,50 ,50 ),(0 ,500 ,self .manager .screen_width ,100 ))
        bpm =self .anim_state ['bomber_pos']
        pygame .draw .rect (self .screen ,(255 ,255 ,255 ),(bpm [0 ]-15 ,bpm [1 ]-30 ,30 ,30 ))
        pygame .draw .circle (self .screen ,(255 ,200 ,200 ),(bpm [0 ],bpm [1 ]-45 ),15 )
        pygame .draw .rect (self .screen ,(200 ,50 ,50 ),(bpm [0 ]-15 ,bpm [1 ]-60 ,30 ,15 ))
        if self .anim_state ['is_throwing']:
            bx ,by =self .anim_state ['bomb_pos']
            pygame .draw .circle (self .screen ,(0 ,0 ,0 ),(int (bx ),int (by )),12 )
            pygame .draw .circle (self .screen ,(200 ,50 ,50 ),(int (bx )+2 ,int (by )-2 ),4 )
        for p in self .anim_state ['particles']:
            color =(255 ,random .randint (100 ,200 ),0 )
            pygame .draw .circle (self .screen ,color ,(int (p [0 ]),int (p [1 ])),random .randint (2 ,6 ))
    def _create_floor_tile (self ):
        tile =pygame .Surface ((50 ,50 ))
        base_color =(30 ,90 ,30 )
        tile .fill (base_color )
        top_color =(50 ,120 ,50 )
        pygame .draw .polygon (tile ,top_color ,[(5 ,5 ),(45 ,5 ),(45 ,45 ),(5 ,45 )])
        right_color =(20 ,70 ,20 )
        pygame .draw .polygon (tile ,right_color ,[(45 ,5 ),(49 ,1 ),(49 ,41 ),(45 ,45 )])
        bottom_color =(15 ,60 ,15 )
        pygame .draw .polygon (tile ,bottom_color ,[(5 ,45 ),(45 ,45 ),(49 ,49 ),(1 ,49 )])
        pygame .draw .rect (tile ,(10 ,50 ,10 ),(0 ,0 ,50 ,50 ),1 )
        grid_color =(40 ,100 ,40 )
        pygame .draw .line (tile ,grid_color ,(25 ,5 ),(25 ,45 ),1 )
        pygame .draw .line (tile ,grid_color ,(5 ,25 ),(45 ,25 ),1 )
        return tile 

    def _draw_scrolling_background (self ,surface ):
        self .scroll_offset [0 ]+=0.1 
        self .scroll_offset [1 ]+=0.1 
        tile_size =50 
        if self .scroll_offset [0 ]>=tile_size :
            self .scroll_offset [0 ]-=tile_size 
        if self .scroll_offset [1 ]>=tile_size :
            self .scroll_offset [1 ]-=tile_size 
        screen_w =self .manager .screen_width 
        screen_h =self .manager .screen_height 
        tiles_x =(screen_w //tile_size )+2 
        tiles_y =(screen_h //tile_size )+2 
        for ty in range (tiles_y ):
            for tx in range (tiles_x ):
                x =tx *tile_size -self .scroll_offset [0 ]
                y =ty *tile_size -self .scroll_offset [1 ]
                surface .blit (self .floor_tile ,(int (x ),int (y )))
        overlay =pygame .Surface ((screen_w ,screen_h ))
        overlay .set_alpha (160 )
        overlay .fill ((0 ,0 ,0 ))
        surface .blit (overlay ,(0 ,0 ))

    def _build_menu (self ):
        menu =MenuContainer ()
        screen_w =self .manager .screen_width 
        center_x =screen_w //2 -150 
        title_font =pygame .font .Font (None ,80 )
        subtitle_font =pygame .font .Font (None ,30 )
        btn_font =pygame .font .Font (None ,40 )
        menu .add (MenuItem ("Bomberman 2D",screen_w //2 -200 ,80 ,None ,font =title_font ,width =400 ,height =80 ,is_label =True ))
        menu .add (MenuItem ("by Mohamed Abdou @2026",screen_w //2 -200 ,140 ,None ,font =subtitle_font ,width =400 ,height =30 ,is_label =True ))
        start_y =250 
        gap =20 
        buttons_config =[
        ("Multiplayer",self .on_enter_lobby ),
        ("Scoreboard",self .toggle_scoreboard ),
        ("Quit",self .manager .quit_game )
        ]

        current_y =start_y 
        for text ,callback in buttons_config :
            btn =MenuItem (text ,center_x ,current_y ,callback ,font =btn_font )
            menu .add (btn )
            current_y +=btn .rect .height +gap 

        return menu 

    def toggle_scoreboard (self ):
        self .showing_scoreboard =not getattr (self ,'showing_scoreboard',False )

    def on_enter_lobby (self ):
        self .state ='LOBBY'
        self .lobby_view .reset ()

        print ("[LOBBY] Play clicked. 1. Attempting to Connect as Client...")
        self .client =GameClient ()
        local_name =self .current_user .get ('username')if self .current_user else 'Player 2'
        self .local_player_name =local_name 

        if self .client .connect ('127.0.0.1',local_name ):
             print ("[LOBBY] Connection SUCCESS. We are CLIENT.")
             self .is_host =False 
             self .lobby_view .set_mode ('JOINING')
             self .lobby_view .update_state (False ,0 ,[])
             return 
        print ("[LOBBY] Connection Failed. 2. Attempting to Start Server...")
        self .client =None 

        try :
            self .server =GameServer ()
            local_name =self .current_user .get ('username')if self .current_user else 'Player 1'
            self .local_player_name =local_name 
            self .server .start (local_name )
            self .is_host =True 
            print ("[LOBBY] Server Started. We are HOST.")
            self .lobby_view .set_mode ('HOSTING')
            self .lobby_view .update_state (True ,0 ,[local_name ])

        except OSError as e :
            print (f"[LOBBY] Failed to Host (Port Busy?): {e }")
            self .server =None 
            self .is_host =False 
            self .lobby_view .set_mode ('SELECT')

    def draw_high_scores (self ,surface ):
        overlay =pygame .Surface ((self .manager .screen_width ,self .manager .screen_height ))
        overlay .set_alpha (200 )
        overlay .fill ((0 ,0 ,0 ))
        surface .blit (overlay ,(0 ,0 ))
        panel_w =int (self .manager .screen_width *0.8 )
        panel_h =int (self .manager .screen_height *0.8 )
        panel_x =self .manager .screen_width //2 -panel_w //2 
        panel_y =self .manager .screen_height //2 -panel_h //2 
        pygame .draw .rect (surface ,(30 ,30 ,40 ),(panel_x ,panel_y ,panel_w ,panel_h ),border_radius =15 )
        pygame .draw .rect (surface ,(255 ,215 ,0 ),(panel_x ,panel_y ,panel_w ,panel_h ),4 ,border_radius =15 )
        font_title =pygame .font .Font (None ,72 )
        font_header =pygame .font .Font (None ,40 )
        font_row =pygame .font .Font (None ,36 )
        title =font_title .render ("Leaderboard",True ,(255 ,215 ,0 ))
        surface .blit (title ,title .get_rect (center =(self .manager .screen_width //2 ,panel_y +50 )))
        pygame .draw .line (surface ,(100 ,100 ,100 ),(panel_x +40 ,panel_y +90 ),(panel_x +panel_w -40 ,panel_y +90 ),3 )
        headers_y =panel_y +110 
        col1 =panel_x +int (panel_w *0.1 )
        col2 =panel_x +int (panel_w *0.25 )
        col3 =panel_x +int (panel_w *0.6 )
        col4 =panel_x +int (panel_w *0.8 )

        surface .blit (font_header .render ("Rank",True ,(150 ,150 ,150 )),(col1 ,headers_y ))
        surface .blit (font_header .render ("Player",True ,(150 ,150 ,150 )),(col2 ,headers_y ))
        surface .blit (font_header .render ("Score",True ,(150 ,150 ,150 )),(col3 ,headers_y ))
        surface .blit (font_header .render ("Wins",True ,(150 ,150 ,150 )),(col4 ,headers_y ))
        scores_count =int ((panel_h -200 )/45 )
        scores =self .repo .fetch_top_scores (scores_count )
        row_y =headers_y +50 

        for i ,(name ,score ,wins )in enumerate (scores ):
            if i %2 ==0 :
                pygame .draw .rect (surface ,(40 ,40 ,50 ),(panel_x +40 ,row_y -5 ,panel_w -80 ,40 ),border_radius =5 )
            rank_color =(255 ,255 ,255 )
            if i ==0 :rank_color =(255 ,215 ,0 )
            elif i ==1 :rank_color =(192 ,192 ,192 )
            elif i ==2 :rank_color =(205 ,127 ,50 )
            surface .blit (font_row .render (f"#{i +1 }",True ,rank_color ),(col1 ,row_y ))
            surface .blit (font_row .render (str (name ),True ,(255 ,255 ,255 )),(col2 ,row_y ))
            surface .blit (font_row .render (str (score ),True ,(100 ,255 ,100 )),(col3 ,row_y ))
            surface .blit (font_row .render (str (wins ),True ,(100 ,200 ,255 )),(col4 ,row_y ))
            row_y +=45 
        foot_text =font_header .render ("Press SPACE to return",True ,(200 ,200 ,200 ))
        f_rect =foot_text .get_rect (center =(self .manager .screen_width //2 ,panel_y +panel_h -40 ))
        surface .blit (foot_text ,f_rect )

    def _handle_lobby_packet (self ,data ):
        if data .get ('event')=='GAME_START':
            host_name =data .get ('host_name','Player 1')
            self .remote_player_name =host_name 
            print (f"[CLIENT] Handling GAME_START. Current User: {self .current_user }")
            if self .current_user and self .current_user .get ('username'):
                self .local_player_name =self .current_user ['username']
            else :
                print (f"[CLIENT] WARNING: No current_user found! Defaulting to 'Player 2'")
                self .local_player_name ='Player 2'


            received_seed =data .get ('map_seed')
            print (f"[CLIENT] Received map_seed from host: {received_seed }, Host Name: {host_name }, My Name: {self .local_player_name }")
            self .start_game (data .get ('theme_idx'),received_seed )

    def start_game (self ,theme_idx =None ,map_seed =None ):
        self .state ='GAME'
        self .game_over =False 
        self .winner_id =None 
        self .game_over_time =0 
        self .score_system .scores ={1 :0 ,2 :0 }
        self .score_system .notify ()
        factories =[CityFactory (),ForestFactory (),DesertFactory ()]

        if self .is_host :
            if theme_idx is None :
                theme_idx =random .randint (0 ,2 )
            if map_seed is None :
                map_seed =random .randint (0 ,999999 )
                print (f"[HOST] Generated map_seed: {map_seed }")
            if self .server :
                local_name =self .current_user .get ('username','Player 1')if self .current_user else 'Player 1'
                self .server .send_to_all ({
                'event':'GAME_START',
                'theme_idx':theme_idx ,
                'map_seed':map_seed ,
                'host_name':local_name 
                })
                self .local_player_name =local_name 
                self .remote_player_name ='Player 2'

        else :
            if theme_idx is None :theme_idx =0 
        print (f"[{'HOST'if self .is_host else 'CLIENT'}] Creating map with seed: {map_seed }")
        self .map =GameMap (self .manager .screen_width ,self .manager .screen_height ,factories [theme_idx ],seed =map_seed )
        class RemoteStrategy :
            def __init__ (self ):
                self .x =0 
                self .y =0 
                self .frame =0 
                self .planting =False 
                self .last_planting =False 

            def get_movement (self ):
                return 0 ,0 

            def planted_bomb (self ):
                just_pressed =self .planting and not self .last_planting 
                self .last_planting =self .planting 
                return just_pressed 

            def update_state (self ,x ,y ,frame ,planting ):
                self .x =x 
                self .y =y 
                self .frame =frame 
                self .planting =planting 

        self .players .empty ()

        if self .is_host :
            p1_input =Player1Keys ()
        else :
            p1_input =RemoteStrategy ()

        p1 =Player (40 ,40 ,(0 ,0 ,255 ),p1_input ,1 )

        if not self .is_host :
            p2_input =Player1Keys ()
        else :
            p2_input =RemoteStrategy ()

        p2 =Player (720 ,520 ,(0 ,255 ,0 ),p2_input ,2 )

        self .players .add (p1 )
        self .players .add (p2 )

        self .local_player =p1 if self .is_host else p2 
        self .remote_player =p2 if self .is_host else p1 


        self .enemies .empty ()
        random .seed (42 )
        if True :
            e_smart =Enemy (300 ,300 ,enemy_type ="smart")
            self .enemies .add (e_smart )
            for _ in range (2 ):
                e_dumb =Enemy (random .randint (200 ,600 ),random .randint (100 ,400 ),enemy_type ="dumb")
                self .enemies .add (e_dumb )
        random .seed ()

    def on_host_game (self ):
        self .state ='LOBBY'
        self .lobby_view .set_mode ('HOSTING')
        self .is_host =True 

        self .server =GameServer ()
        self .server .start ()

    def on_join_game (self ):
        self .state ='LOBBY'
        self .lobby_view .set_mode ('JOINING')
        self .is_host =False 
        self .client =GameClient ()

    def _spawn_bomb (self ,player ):
        grid_x =(player .rect .centerx //TILE_SIZE )*TILE_SIZE 
        grid_y =(player .rect .centery //TILE_SIZE )*TILE_SIZE 

        if not self .is_host and player .player_id ==self .local_player .player_id :
            self .pending_bomb_placement ={
            'x':grid_x ,
            'y':grid_y ,
            'range':player .explosion_range 
            }
            self .bomb_placement_frames =60 
            print (f"[CLIENT] Requesting bomb placement at ({grid_x }, {grid_y })")
            return 
        bomb =self .bomb_pool .get ()
        if bomb :
            bomb .spawn (grid_x ,grid_y ,player )
            self .bombs .add (bomb )
            player .active_bombs +=1 
            player .bombs_remaining -=1 
            print (f"[HOST] Spawned bomb at ({grid_x }, {grid_y }) for Player {player .player_id }, active={bomb .active }",flush =True )

    def _draw_hud (self ,surface ):
        pygame .draw .rect (surface ,(20 ,20 ,20 ),(0 ,600 ,800 ,100 ))
        pygame .draw .line (surface ,(100 ,100 ,100 ),(0 ,600 ),(800 ,600 ),2 )
        p1_score =self .score_system .get_score (1 )
        p1_text =self .font .render (f"P1 (Host): {p1_score }",True ,(100 ,100 ,255 ))
        surface .blit (p1_text ,(20 ,630 ))
        p2_score =self .score_system .get_score (2 )
        p2_text =self .font .render (f"P2 (Client): {p2_score }",True ,(100 ,255 ,100 ))
        surface .blit (p2_text ,(self .manager .screen_width -p2_text .get_width ()-20 ,630 ))
        if self .local_player :

            bombs_text =self .font .render (f"Bombs: {self .local_player .bombs_remaining }",True ,(255 ,200 ,100 ))

            surface .blit (bombs_text ,(self .manager .screen_width //2 -bombs_text .get_width ()//2 ,630 ))

    def run (self ):
        while self .manager .running :
            dt =self .clock .tick (60 )/1000.0 
            self .frame_count +=1 
            events =pygame .event .get ()
            for event in events :
                if event .type ==pygame .QUIT :
                    self .manager .quit_game ()

            if self .state =='INTRO':
                self .intro .update (dt )


                if self .intro .is_finished ():
                    self .state ='AUTH'

                for event in events :
                     if event .type ==pygame .KEYDOWN :
                         if event .key in (pygame .K_ESCAPE ,pygame .K_RETURN ,pygame .K_SPACE ):
                             self .state ='AUTH'

            elif self .state =='AUTH':
                for event in events :
                    result =self .auth_view .handle_event (event )
                    if result and result ['action']=='AUTH_SUCCESS':
                        self .current_user =result ['user']
                        self .state ='MENU'
                        self .main_menu =self ._build_menu ()

            elif self .state =='MENU':
                if getattr (self ,'showing_scoreboard',False ):
                    for event in events :
                        if event .type ==pygame .KEYDOWN and event .key ==pygame .K_SPACE :
                            self .showing_scoreboard =False 
                else :
                    for event in events :
                        self .main_menu .handle_event (event )
                    self ._update_menu_animation ()

            elif self .state =='LOBBY':
                self ._handle_lobby_input (events )
                if self .is_host and self .server :
                    players =[self .local_player_name ]
                    if self .server .p2_name :
                        self .remote_player_name =self .server .p2_name 
                        players .append (self .server .p2_name )
                    self .lobby_view .update_state (True ,self .server .current_theme_idx ,players )

                elif not self .is_host and self .client :
                    data =self .client .receive ()
                    if data :
                        if data .get ('event')=='LOBBY_STATE':

                            h_name =data .get ('host_name','Host')
                            t_idx =data .get ('theme_idx',0 )
                            self .remote_player_name =h_name 
                            players =[h_name ,self .local_player_name ]
                            self .lobby_view .update_state (False ,t_idx ,players )

                        elif data .get ('event')=='MAP_UPDATE':
                            t_idx =data .get ('theme_idx',0 )
                            players =self .lobby_view .players 
                            self .lobby_view .update_state (False ,t_idx ,players )

                        elif data .get ('event')=='GAME_START':
                            self ._handle_lobby_packet (data )
                if self .lobby_view .mode =='WAITING_ROOM':

                    if self .is_host and self .server :

                        if self .server .last_data :
                            data =self .server .last_data 
                            if data .get ('event')=='LOBBY_JOIN':
                                self .client_username =data .get ('name','Client')

                        players =[self .local_player_name or 'Host']
                        if len (self .server .clients )>0 :
                            players .append (self .client_username or 'Client')
                        self .lobby_view .update_state (True ,self .lobby_view .theme_idx ,players )

                        update_packet ={
                        'event':'LOBBY_UPDATE',
                        'theme_idx':self .lobby_view .theme_idx ,
                        'players':players 
                        }

                        if self .frame_count %30 ==0 :
                            self .server .send_to_all (update_packet )

                    elif not self .is_host and self .client :
                        if self .client .connected :
                            data =self .client .receive ()
                            if data :
                                if data .get ('event')=='LOBBY_UPDATE':
                                    self .lobby_view .update_state (False ,data .get ('theme_idx',0 ),data .get ('players',[]))
                                    if self .frame_count %60 ==0 :
                                        self .client .send ({'event':'LOBBY_JOIN','name':self .local_player_name or 'Client'})

                                elif data .get ('event')=='GAME_START':
                                    self ._handle_lobby_packet (data )
                        else :
                             pass 

            elif self .state =='GAME':
                self ._update_game (events )

            self ._draw ()

        self ._shutdown ()

    def _handle_lobby_input (self ,events ):
        for event in events :
             action =self .lobby_view .handle_event (event )
             if action and action .get ('action'):
                 act =action ['action']

                 if act =='QUIT':
                     self .manager .quit_game ()

                 elif act =='CANCEL':
                      if self .server :self .server .close ()
                      if self .client :
                          try :self .client .client_socket .close ()
                          except :pass 
                      self .server =None 
                      self .client =None 
                      self .state ='MENU'
                      self .lobby_view .reset ()

                 elif act =='THEME_CHANGE':
                      if self .server :
                          new_idx =action ['idx']
                          self .server .current_theme_idx =new_idx 
                          print (f"[HOST] Changed theme to {new_idx }")
                          self .server .send_to_all ({'event':'MAP_UPDATE','theme_idx':new_idx })
                          self .lobby_view .theme_idx =new_idx 
                          if self .lobby_view .map_preview :
                               self .lobby_view .map_preview .set_theme (new_idx )

                 elif act =='START_MATCH':
                      if self .server and self .server .p2_name :
                           self .start_game (self .server .current_theme_idx )

    def _update_game (self ,events ):
        if getattr (self ,'local_player',None ):
            planting =False 
            if hasattr (self .local_player .input_strategy ,'key_map'):
                keys =pygame .key .get_pressed ()
                planting =keys [self .local_player .input_strategy .key_map ['bomb']]
            else :
                 planting =self .local_player .input_strategy .planted_bomb ()

            data ={
            'x':self .local_player .rect .x ,
            'y':self .local_player .rect .y ,
            'frame':self .local_player .walk_frame ,
            'plant':planting ,
            'plant':planting ,
            'alive':self .local_player .is_alive ,
            'score':self .score_system .get_score (self .local_player .player_id ),
            'bombs_remaining':self .local_player .bombs_remaining ,
            'bomb_count':self .local_player .bombs_count ,
            'range':self .local_player .explosion_range ,
            'speed':self .local_player .speed ,
            'ghost':self .local_player .ghost_active 
            }

            if not self .is_host :
                c_user_name =self .current_user .get ('username')if self .current_user else None 
                client_name =getattr (self ,'local_player_name',None )or c_user_name or 'Client'
                import time 
                current_time =time .time ()
                if client_name in ['Player 2','Client']and (getattr (self ,'last_client_debug',0 )+10 <current_time ):
                     self .last_client_debug =current_time 
                     print (f"[DEBUG CLIENT] Sending generic name '{client_name }'. Current User: {self .current_user }, LocalName: {getattr (self ,'local_player_name','unset')}")

                data ['client_name']=client_name 
                if hasattr (self ,'pending_powerup_activation')and self .pending_powerup_activation :
                    data ['powerup_activation']=self .pending_powerup_activation 
                    print (f"[CLIENT] Sending powerup activation: {self .pending_powerup_activation }")
                    self .pending_powerup_activation =None 
            if self .is_host :
                data ['scores']=self .score_system .scores 
                data ['game_over']=self .game_over 
                data ['winner']=self .winner_id 

                data ['player_names']={
                1 :self .local_player_name or 'Host',
                2 :self .remote_player_name or 'Client'
                }

                bomb_list =[]
                for b in self .bombs :
                    bomb_list .append ({'x':b .rect .x ,'y':b .rect .y })
                data ['active_bombs']=bomb_list 
                pup_list =[]
                for p in self .powerups :
                    pup_list .append ({'x':p .rect .x ,'y':p .rect .y ,'type':p .type })
                data ['active_powerups']=pup_list 

                if self .map_updates :
                    data ['map_updates']=self .map_updates 
                    self .map_updates =[]
                enemy_list =[]
                for e in self .enemies :
                    enemy_list .append ({
                    'x':e .rect .x ,
                    'y':e .rect .y ,
                    'type':getattr (e ,'enemy_type','dumb')
                    })
                data ['active_enemies']=enemy_list 
                explosion_list =[]
                for exp in self .explosions :
                    explosion_list .append ({
                    'x':exp .rect .x ,
                    'y':exp .rect .y 
                    })
                data ['active_explosions']=explosion_list 
                if len (self .players )>1 :
                    p2 =self .players .sprites ()[1 ]
                    data ['client_stats']={
                    'bombs_remaining':p2 .bombs_remaining ,
                    'bombs_count':p2 .bombs_count ,
                    'range':p2 .explosion_range ,
                    'speed':p2 .speed ,
                    'ghost':p2 .ghost_active ,
                    'ghost_timer':p2 .ghost_timer ,
                    'inventory':p2 .inventory .copy (),
                    'active_effects':[(type (cmd ).__name__ ,timer )for cmd ,timer in p2 .active_effects ]
                    }

            if self .is_host and self .server :
                self .server .send_to_all (data )
            elif not self .is_host and self .client :
                if hasattr (self ,'pending_bomb_placement')and self .pending_bomb_placement :
                    data ['bomb_placement']=self .pending_bomb_placement 
                    if self .bomb_placement_frames %20 ==0 :
                        print (f"[CLIENT] Including bomb_placement in packet: {self .pending_bomb_placement }")
                    if not hasattr (self ,'bomb_placement_frames'):
                        self .bomb_placement_frames =60 
                    self .bomb_placement_frames -=1 
                    if self .bomb_placement_frames <=0 :
                        self .pending_bomb_placement =None 
                        print (f"[CLIENT] Cleared pending bomb placement after multiple sends")
                self .client .send (data )

        remote_data =None 
        if self .is_host and self .server :
            remote_data =self .server .last_data 
            if remote_data :
                if 'bomb_placement'in remote_data :
                    bomb_data =remote_data ['bomb_placement']
                    grid_x =bomb_data .get ('x')
                    grid_y =bomb_data .get ('y')
                    duplicate =False 
                    for b in self .bombs :
                        if abs (b .rect .x -(grid_x +5 ))<5 and abs (b .rect .y -(grid_y +5 ))<5 :
                            duplicate =True 
                            break 

                    if not duplicate :
                        print (f"[HOST] Received NEW bomb_placement: x={grid_x }, y={grid_y }")
                        bomb =self .bomb_pool .get ()
                        if bomb :
                            bomb .spawn (grid_x ,grid_y ,self .remote_player )
                            self .bombs .add (bomb )
                            self .remote_player .active_bombs +=1 
                            self .remote_player .bombs_remaining -=1 
                            print (f"[HOST] Client placed bomb at ({grid_x }, {grid_y }), total bombs: {len (self .bombs )}")
                        else :
                            print (f"[HOST] ERROR: No bomb available from pool!")
                if 'name'in remote_data :
                    self .client_username =remote_data .get ('name','Player 2')
                if 'client_name'in remote_data :
                    self .client_username =remote_data .get ('client_name','Player 2')
                if 'powerup_activation'in remote_data :
                    powerup_type =remote_data ['powerup_activation']
                    print (f"[HOST] Received powerup activation request: {powerup_type }")
                    if self .remote_player .inventory .get (powerup_type ,0 )>0 :
                        old_selection =self .remote_player .selected_powerup 
                        self .remote_player .selected_powerup =powerup_type 
                        self .remote_player .activate_selection ()
                        self .remote_player .selected_powerup =old_selection 
                        print (f"[HOST] Applied powerup {powerup_type } for client")
                    else :
                        print (f"[HOST] Client doesn't have {powerup_type } in inventory!")
        elif not self .is_host and self .client :
            remote_data =self .client .receive ()


        if remote_data and getattr (self ,'remote_player',None ):
            if isinstance (remote_data ,dict )and 'x'in remote_data :
                self .remote_player .rect .x =remote_data .get ('x',self .remote_player .rect .x )
                self .remote_player .rect .y =remote_data .get ('y',self .remote_player .rect .y )
                self .remote_player .rect .y =remote_data .get ('y',self .remote_player .rect .y )
                self .remote_player .walk_frame =remote_data .get ('frame',0 )
                if not self .is_host :
                    self .remote_player .bombs_count =remote_data .get ('bomb_count',1 )
                    self .remote_player .explosion_range =remote_data .get ('range',2 )
                    self .remote_player .speed =remote_data .get ('speed',3 )
                    self .remote_player .ghost_active =remote_data .get ('ghost',False )

                was_alive =self .remote_player .is_alive 
                is_alive_now =remote_data .get ('alive',True )

                if self .is_host and 'client_name'in remote_data :
                    new_name =remote_data ['client_name']
                    if new_name and new_name !=self .remote_player_name :
                        self .remote_player_name =new_name 

                if self .is_host and was_alive and not is_alive_now :
                    print ("Remote Player Died. Host Wins.")

                    self .game_over =True 
                    self .showing_scoreboard =True 
                    self .game_over_time =pygame .time .get_ticks ()
                    self .winner_id =self .local_player .player_id 

                self .remote_player .is_alive =is_alive_now 

                if not self .is_host :
                    if 'player_names'in remote_data :
                        self .synced_player_names =remote_data ['player_names']
                        self .host_username =self .synced_player_names .get (1 ,'Player 1')
                        if not hasattr (self ,'username'):
                            self .username =self .synced_player_names .get (2 ,'Player 2')
                        self .local_player_name =self .synced_player_names .get (2 ,'Player 2')

                    if 'scores'in remote_data :
                        new_scores =remote_data ['scores']
                        for pid ,val in new_scores .items ():
                            self .score_system .scores [pid ]=val 
                        self .score_system .notify ()

                    if 'client_stats'in remote_data :
                         stats =remote_data ['client_stats']
                         if not (hasattr (self ,'pending_bomb_placement')and self .pending_bomb_placement ):
                             self .local_player .bombs_remaining =stats .get ('bombs_remaining',1 )

                         self .local_player .bombs_count =stats .get ('bombs_count',1 )
                         self .local_player .explosion_range =stats .get ('range',2 )
                         self .local_player .speed =stats .get ('speed',3 )
                         self .local_player .ghost_active =stats .get ('ghost',False )
                         self .local_player .ghost_timer =stats .get ('ghost_timer',0 )
                         if 'inventory'in stats :
                             self .local_player .inventory =stats ['inventory'].copy ()


                    if 'active_bombs'in remote_data :
                        host_bombs =remote_data ['active_bombs']
                        self .bombs .empty ()

                        for b_data in host_bombs :
                            bomb =self .bomb_pool .get ()
                            if bomb :
                                bomb .rect .x =b_data ['x']
                                bomb .rect .y =b_data ['y']
                                bomb .active =True 
                                bomb .frame_timer =180 
                                bomb .owner =None 
                                bomb .range =2 
                                self .bombs .add (bomb )

                    if 'active_enemies'in remote_data :
                        self .enemies .empty ()
                        enemy_count =len (remote_data ['active_enemies'])
                        if enemy_count >0 and pygame .time .get_ticks ()%120 ==0 :
                            print (f"[CLIENT] Syncing {enemy_count } enemies from Host")
                        for e_data in remote_data ['active_enemies']:
                            e =Enemy (e_data ['x'],e_data ['y'],e_data ['type'])
                            self .enemies .add (e )

                    if 'active_powerups'in remote_data :
                        self .powerups .empty ()
                        for p_data in remote_data ['active_powerups']:
                            self .powerups .add (Powerup (p_data ['x']-5 ,p_data ['y']-5 ,p_data ['type']))

                    if 'active_explosions'in remote_data :
                        self .explosions .empty ()
                        for exp_data in remote_data ['active_explosions']:
                            exp =self .explosion_pool .get ()
                            if exp :
                                exp .rect .x =exp_data ['x']
                                exp .rect .y =exp_data ['y']
                                exp .active =True 
                                import time 
                                exp .creation_time =time .time ()
                                self .explosions .add (exp )

                    if 'map_updates'in remote_data :
                        updates_count =len (remote_data ['map_updates'])
                        if updates_count >0 :
                            print (f"[CLIENT] Received {updates_count } map updates from host")
                        for wall_pos in remote_data ['map_updates']:
                            wx ,wy =wall_pos ['x'],wall_pos ['y']
                            removed =False 
                            for wall in self .map .walls [:]:
                                if wall .rect .x ==wx and wall .rect .y ==wy :
                                    self .map .walls .remove (wall )
                                    removed =True 
                                    print (f"[CLIENT] Removed wall at ({wx }, {wy })")
                                    break 
                            if not removed :
                                print (f"[CLIENT] WARNING: Could not find wall at ({wx }, {wy }) to remove!")

                    if 'game_over'in remote_data and remote_data ['game_over']:
                         if not self .game_over :
                             print (f"[CLIENT] Received GAME OVER! Winner: {remote_data .get ('winner')}")
                             self .game_over =True 
                             self .showing_scoreboard =True 
                             self .game_over_time =pygame .time .get_ticks ()
                             self .winner_id =remote_data .get ('winner')

                if hasattr (self .remote_player .input_strategy ,'update_state'):
                    self .remote_player .input_strategy .update_state (
                    remote_data .get ('x'),
                    remote_data .get ('y'),
                    remote_data .get ('frame'),
                    remote_data .get ('plant',False )
                    )

        if self .game_over :
            for event in events :
                if event .type ==pygame .KEYDOWN and event .key ==pygame .K_SPACE :
                    print ("Returning to Main Menu...")
                    self .reset_game ()
            return 

        for player in self .players :
            player .update (self .map .walls )

            if player ==self .local_player :
                if player .input_strategy .cycle_powerup ():
                    player .cycle_selection ()

                if player .input_strategy .planted_bomb ():
                    print (f"[DEBUG] Space pressed! Player {player .player_id }, is_host={self .is_host }")
                    used_item =False 
                    if player .selected_powerup :
                        if player .inventory .get (player .selected_powerup ,0 )>0 :
                            if not self .is_host and player ==self .local_player :
                                self .pending_powerup_activation =player .selected_powerup 
                                print (f"[CLIENT] Requesting powerup activation: {player .selected_powerup }")
                            else :
                                player .activate_selection ()
                            used_item =True 

                    if not used_item :
                         if player .can_plant_bomb ():
                             print (f"[DEBUG] Planting bomb for Player {player .player_id }")
                             self ._spawn_bomb (player )
                         else :
                             print (f"[DEBUG] Cannot plant: Active={player .active_bombs }/{player .bombs_count }, Ammo={player .bombs_remaining }")

            hit_pow =pygame .sprite .spritecollide (player ,self .powerups ,True )
            for p in hit_pow :
                player .collect_powerup (p .type )

        if self .is_host :
            for player in self .players :
                if player .is_alive :
                    enemy_hit =pygame .sprite .spritecollide (player ,self .enemies ,False )
                    if enemy_hit :
                        print (f"Player {player .player_id } touched by enemy!")
                        player .is_alive =False 
                        if player .player_id ==self .local_player .player_id :
                            self .game_over =True 
                            self .showing_scoreboard =True 
                            self .game_over_time =pygame .time .get_ticks ()
                            self .winner_id =self .remote_player .player_id 
                        else :
                            self .game_over =True 
                            self .showing_scoreboard =True 
                            self .game_over_time =pygame .time .get_ticks ()
                            self .winner_id =self .local_player .player_id 

        if self .is_host :
            for enemy in self .enemies :
                enemy .update (self .map ,self .players )
        if self .is_host :
            for bomb in self .bombs :
                if bomb .update ():
                    print (f"[HOST] Bomb exploded! Owner: Player {bomb .owner .player_id if bomb .owner else 'None'}")
                    self ._trigger_explosion (bomb )
                    bomb .reset ()
                    self .bombs .remove (bomb )
                    self .bomb_pool .return_obj (bomb )
        for exp in self .explosions :
            if exp .update ():
                exp .reset ()
                self .explosions .remove (exp )
                self .explosion_pool .return_obj (exp )
        local_died =False 
        hit_self =pygame .sprite .spritecollide (self .local_player ,self .explosions ,False )
        if hit_self and self .local_player .is_alive :
             print (f"I (Player {self .local_player .player_id }) died!")
             self .local_player .is_alive =False 
             local_died =True 
        remote_died =False 
        if self .is_host and self .remote_player .is_alive :
             hit_remote =pygame .sprite .spritecollide (self .remote_player ,self .explosions ,False )
             if hit_remote :
                  print (f"Remote Player (Player {self .remote_player .player_id }) died!")
                  self .remote_player .is_alive =False 
                  remote_died =True 
        if self .is_host and (local_died or remote_died ):
            if local_died and remote_died :
                print ("TIE! Both players eliminated!")
                self .game_over =True 
                self .showing_scoreboard =True 
                self .game_over_time =pygame .time .get_ticks ()
                self .winner_id =None 
            elif local_died :
                self .game_over =True 
                self .showing_scoreboard =True 
                self .game_over_time =pygame .time .get_ticks ()
                self .winner_id =self .remote_player .player_id 
            elif remote_died :
                self .game_over =True 
                self .showing_scoreboard =True 
                self .game_over_time =pygame .time .get_ticks ()
                self .winner_id =self .local_player .player_id 

        if self .is_host :
             hit_enemies =pygame .sprite .groupcollide (self .enemies ,self .explosions ,True ,False )
             for enemy ,exps in hit_enemies .items ():
                 if exps :
                     killer_exp =exps [0 ]
                     k_id =getattr (killer_exp ,'owner_id',None )
                     if k_id :
                         self .score_system .update_score (k_id ,50 )
        else :
             pygame .sprite .groupcollide (self .enemies ,self .explosions ,True ,False )

    def _trigger_explosion (self ,bomb ):
        positions =[(bomb .rect .x ,bomb .rect .y )]
        directions =[(0 ,40 ),(0 ,-40 ),(40 ,0 ),(-40 ,0 )]

        for dx ,dy in directions :
            for i in range (1 ,3 ):
                nx =bomb .rect .x +dx *i 
                ny =bomb .rect .y +dy *i 
                if not (0 <=nx <self .manager .screen_width and 0 <=ny <self .manager .screen_height ):
                    break 
                wall_hit =False 
                test_rect =pygame .Rect (nx ,ny ,30 ,30 )

                for wall in self .map .walls [:]:
                    if wall .rect .colliderect (test_rect ):
                        wall_hit =True 

                        if wall .destructible :
                            wall .health -=1 
                            if wall .health <=0 :
                                if self .is_host :
                                    self .map .walls .remove (wall )

                                    self .map_updates .append ({'x':wall .rect .x ,'y':wall .rect .y })

                                if self .is_host and bomb .owner :
                                    pts =0 

                                    from src .models .factories import CityHardWall ,ForestHardWall ,DesertHardWall 
                                    cname =wall .__class__ .__name__ 
                                    if 'Hard'in cname :pts =20 
                                    else :pts =10 

                                    self .score_system .update_score (bomb .owner .player_id ,pts )

                                    if random .random ()<0.5 :

                                        roll =random .random ()
                                        p_type ='BOMB_UP'
                                        if roll <0.4 :p_type ='BOMB_UP'
                                        elif roll <0.6 :p_type ='FIRE_UP'
                                        elif roll <0.8 :p_type ='SPEED_UP'
                                        else :p_type ='GHOST'

                                        p =Powerup (wall .rect .x ,wall .rect .y ,p_type )
                                        self .powerups .add (p )

                        break 
                if wall_hit :
                    break 

                positions .append ((nx ,ny ))

        for px ,py in positions :
            exp =self .explosion_pool .get ()
            owner_id =bomb .owner .player_id if bomb .owner else None 
            exp .spawn (px ,py ,owner_id )
            self .explosions .add (exp )

        if bomb .owner :
            before =bomb .owner .active_bombs 
            bomb .owner .active_bombs -=0 if bomb .owner .active_bombs <=0 else 1 
            after =bomb .owner .active_bombs 
            print (f"[DEBUG] Decremented active_bombs for Player {bomb .owner .player_id }: {before } -> {after }")

    def reset_game (self ):
        try :
            if hasattr (self ,'current_user')and self .current_user :
                user_id =self .current_user .get ('id')
                if user_id and hasattr (self ,'score_system'):

                    if hasattr (self ,'local_player'):
                        final_score =self .score_system .get_score (self .local_player .player_id )
                        if final_score >0 :
                            self .repo .save_score (user_id ,final_score )
        except Exception as e :
            print (f"Error saving score: {e }")

        if self .server :
            self .server .close ()
            self .server =None 

        if self .client :
            try :
                self .client .client_socket .close ()
            except :
                pass 
            self .client =None 

        self .map_updates =[]
        if hasattr (self ,'pending_bomb_placement'):
             self .pending_bomb_placement =None 

        self .is_host =False 
        self .game_over =False 
        self .showing_scoreboard =False 

        self .lobby_view .reset ()

        if hasattr (self ,'bombs'):
            self .bombs .empty ()
        if hasattr (self ,'explosions'):
            self .explosions .empty ()
        if hasattr (self ,'enemies'):
            self .enemies .empty ()
        if hasattr (self ,'powerups'):
            self .powerups .empty ()

        self .state ='MENU'

    def _draw (self ):
        if self .state =='INTRO':
            self .intro .draw (self .screen )

        elif self .state =='AUTH':
            self .auth_view .draw (self .screen )

        elif self .state =='MENU':
            if getattr (self ,'showing_scoreboard',False ):
                self .draw_high_scores (self .screen )
            else :
                self ._draw_scrolling_background (self .screen )
                self .main_menu .draw (self .screen )

        elif self .state =='LOBBY':
            self .lobby_view .draw (self .screen )

        elif self .state =='GAME':
            if self .map :
                self .map .draw (self .screen )

            if len (self .bombs )>0 :
                 pass 
            self .bombs .draw (self .screen )
            self .explosions .draw (self .screen )
            self .powerups .draw (self .screen )
            self .players .draw (self .screen )
            self .enemies .draw (self .screen )

            local_id =self .local_player .player_id if hasattr (self ,'local_player')else None 

            self .scoreboard .update (self .score_system .scores ,list (self .players ),local_id )
            self .scoreboard .draw (self .screen )

        try :
            if getattr (self ,'showing_scoreboard',False )and self .state =='GAME':
                 if self .game_over :
                     now =pygame .time .get_ticks ()
                     duration =300 
                     progress =min (1.0 ,(now -self .game_over_time )/duration )
                 else :
                     progress =1.0 

                     progress =1.0 


                 scores =self .repo .fetch_top_scores ()

                 if self .is_host :
                     player_names ={
                     1 :self .local_player_name or "Host",
                     2 :getattr (self ,'remote_player_name',"Player 2")
                     }
                 else :
                     player_names ={
                     1 :getattr (self ,'remote_player_name',"Host"),
                     2 :self .local_player_name or "Player 2"
                     }

                 print (f"[GAME OVER] Winner ID: {self .winner_id }, Player Names: {player_names }")

                 self .scoreboard .draw_modal (self .screen ,scores ,
                 game_over =self .game_over ,
                 winner_id =self .winner_id ,
                 progress =progress ,
                 current_scores =self .score_system .scores ,
                 player_names =player_names )
        except Exception as e :
            print (f"Render Error: {e }")
        pygame .display .flip ()

    def _shutdown (self ):
        self .repo .close ()
        pygame .quit ()
        sys .exit ()

if __name__ =="__main__":
    game =GameFacade ()
    try :
        game .run ()
    except Exception as e :
        import traceback 
        with open ("crash_log.txt","w")as f :
            traceback .print_exc (file =f )
        traceback .print_exc ()
        pygame .quit ()
        input ("Press Enter to Exit...")
