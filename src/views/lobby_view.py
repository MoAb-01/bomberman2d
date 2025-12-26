import pygame 
from src .views .menus import MenuContainer ,MenuItem 
from src .models .factories import CityFactory ,ForestFactory ,DesertFactory 

class MapPreview (MenuItem ):
    """
    Composite component to render the map thumbnail.
    """
    def __init__ (self ,x ,y ,width ,height ,factories ):
        super ().__init__ ("",x ,y ,None ,width =width ,height =height ,is_label =True )
        self .factories =factories 
        self .current_idx =0 
        self .thumbnails =[f .create_thumbnail (width ,height )for f in factories ]

    def set_theme (self ,idx ):
        self .current_idx =idx %len (self .thumbnails )

    def draw (self ,surface ):

        pygame .draw .rect (surface ,(200 ,200 ,200 ),self .rect ,4 )

        thumb =self .thumbnails [self .current_idx ]
        surface .blit (thumb ,self .rect )

        names =["Neon City","Ancient Forest","Desert Ruins"]
        font =pygame .font .Font (None ,36 )
        text =font .render (names [self .current_idx ],True ,(255 ,255 ,255 ))

        t_rect =text .get_rect (center =(self .rect .centerx ,self .rect .bottom +25 ))
        pygame .draw .rect (surface ,(0 ,0 ,0 ),t_rect .inflate (20 ,10 ))
        surface .blit (text ,t_rect )

class LobbyView :
    def __init__ (self ,width ,height ):
        self .width =width 
        self .height =height 
        self .mode ='SELECT'


        self .is_host =False 
        self .theme_idx =0 
        self .players =[]
        self .message =""


        self .factories =[CityFactory (),ForestFactory (),DesertFactory ()]
        self .font_large =pygame .font .Font (None ,60 )
        self .font_small =pygame .font .Font (None ,36 )


        self .menu_container =MenuContainer ()
        self .map_preview =None 
        self .action_queue =None 

        self ._build_select_menu ()

    def _build_select_menu (self ):
        self .menu_container .children =[]
        cx ,cy =self .width //2 ,self .height //2 


        self .menu_container .add (MenuItem ("BOMBERMAN",cx -150 ,80 ,None ,font =self .font_large ,width =300 ,height =80 ,is_label =True ))


        self .menu_container .add (MenuItem ("PLAY MULTIPLAYER",cx -150 ,cy -20 ,lambda :self .set_action ('PLAY'),width =300 ,height =60 ))


        self .menu_container .add (MenuItem ("QUIT GAME",cx -150 ,cy +60 ,lambda :self .set_action ('QUIT'),width =300 ,height =60 ))

    def _build_lobby_ui (self ):
        self .menu_container .children =[]
        cx =self .width //2 


        self .map_preview =MapPreview (cx -150 ,100 ,300 ,200 ,self .factories )
        self .menu_container .add (self .map_preview )



        pass 

    def set_mode (self ,mode ):
        self .mode =mode 
        if mode =='SELECT':
            self ._build_select_menu ()
        else :
            self ._build_lobby_ui ()

    def update_state (self ,is_host ,theme_idx ,players ):
        self .is_host =is_host 
        self .theme_idx =theme_idx 
        self .players =players 
        if self .map_preview :
            self .map_preview .set_theme (theme_idx )

    def set_action (self ,action ):
        self .action_queue =action 

    def handle_event (self ,event ):
        if self .mode =='SELECT':
            self .menu_container .handle_event (event )

        elif self .mode !='SELECT':

            if event .type ==pygame .KEYDOWN and event .key ==pygame .K_ESCAPE :
                return {'action':'CANCEL'}


            if self .is_host :
                if event .type ==pygame .KEYDOWN :
                    if event .key ==pygame .K_d or event .key ==pygame .K_RIGHT :
                        return {'action':'THEME_CHANGE','idx':(self .theme_idx +1 )%3 }
                    if event .key ==pygame .K_a or event .key ==pygame .K_LEFT :
                        return {'action':'THEME_CHANGE','idx':(self .theme_idx -1 )%3 }
                    if event .key ==pygame .K_RETURN :
                         if len (self .players )>=2 :
                             return {'action':'START_MATCH','theme_idx':self .theme_idx }

        if self .action_queue :
            a =self .action_queue 
            self .action_queue =None 
            return {'action':a }

        return None 

    def draw (self ,surface ):
        surface .fill ((20 ,20 ,30 ))
        self .menu_container .draw (surface )

        if self .mode !='SELECT':
            cx =self .width //2 


            pygame .draw .line (surface ,(100 ,100 ,100 ),(cx -200 ,380 ),(cx +200 ,380 ),2 )

            y =400 
            for i in range (2 ):
                p_text ="Waiting..."
                color =(100 ,100 ,100 )

                if i <len (self .players ):
                   p_text =f"P{i +1 }: {self .players [i ]}"
                   color =(100 ,255 ,100 )if i ==1 else (255 ,215 ,0 )




                surf =self .font_small .render (p_text ,True ,color )
                surface .blit (surf ,(cx -100 ,y ))
                y +=40 


            y_inst =self .height -60 
            if self .is_host :
                msg ="[WASD] Change Map   [ENTER] Start Game"
                if len (self .players )<2 :
                    msg ="Waiting for P2..."
                col =(200 ,200 ,255 )
            else :
                msg ="Waiting for Host to start..."
                col =(200 ,200 ,200 )

            i_surf =self .font_small .render (msg ,True ,col )
            surface .blit (i_surf ,i_surf .get_rect (center =(cx ,y_inst )))

    def reset (self ):
        self .set_mode ('SELECT')
        self .players =[]
        self .is_host =False 
