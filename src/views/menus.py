
from abc import ABC ,abstractmethod 
import pygame 

class MenuComponent (ABC ):
    def __init__ (self ,parent =None ):
        self .parent =parent 

    @abstractmethod 
    def draw (self ,surface ):
        pass 

    @abstractmethod 
    def handle_event (self ,event ):
        pass 

class MenuContainer (MenuComponent ):
    def __init__ (self ):
        super ().__init__ ()
        self .children =[]

    def add (self ,component ):
        self .children .append (component )
        component .parent =self 
    def draw (self ,surface ):
        for child in self .children :
            child .draw (surface )
    def handle_event (self ,event ):
        for child in self .children :
            child .handle_event (event )

class MenuItem (MenuComponent ):
    def __init__ (self ,text ,x ,y ,action ,font =None ,width =300 ,height =60 ,is_label =False ):
        super ().__init__ ()
        self .text =text 
        self .rect =pygame .Rect (x ,y ,width ,height )
        self .action =action 
        self .font =font or pygame .font .Font (None ,40 )
        self .is_label =is_label 
        self .color_normal =(50 ,50 ,50 )
        self .color_hover =(100 ,100 ,100 )
        self .color_text =(255 ,255 ,255 )
        self .color_border =(200 ,200 ,200 )

    def draw (self ,surface ):
        mouse_pos =pygame .mouse .get_pos ()
        hovered =self .rect .collidepoint (mouse_pos )and not self .is_label 
        if not self .is_label :
            color =self .color_hover if hovered else self .color_normal 
            pygame .draw .rect (surface ,color ,self .rect ,border_radius =10 )
            pygame .draw .rect (surface ,self .color_border ,self .rect ,2 ,border_radius =10 )
        text_surf =self .font .render (self .text ,True ,self .color_text )
        text_rect =text_surf .get_rect (center =self .rect .center )
        surface .blit (text_surf ,text_rect )

    def handle_event (self ,event ):
        if self .is_label :return 
        if event .type ==pygame .MOUSEBUTTONDOWN :
            if self .rect .collidepoint (event .pos ):
                if self .action :
                    self .action ()
