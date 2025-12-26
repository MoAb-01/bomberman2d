
from abc import ABC ,abstractmethod 
import pygame 

""" Abstrac Factory Dp to select maps"""

class Wall (ABC ):
    def __init__ (self ,x ,y ):
        self .rect =pygame .Rect (x ,y ,40 ,40 )
        self .color =(255 ,255 ,255 )
        self .destructible =False 
        self .health =1 

    @abstractmethod 
    def draw (self ,surface ):
        pass 

class Background (ABC ):
    @abstractmethod 
    def get_color (self ):
        pass 



class CityWall (Wall ):
    def draw (self ,surface ):

        pygame .draw .rect (surface ,(40 ,40 ,50 ),self .rect )
        pygame .draw .rect (surface ,(0 ,255 ,255 ),self .rect ,2 )

        pygame .draw .line (surface ,(0 ,200 ,200 ),(self .rect .left +10 ,self .rect .top +10 ),(self .rect .right -10 ,self .rect .bottom -10 ),2 )
        pygame .draw .line (surface ,(0 ,200 ,200 ),(self .rect .right -10 ,self .rect .top +10 ),(self .rect .left +10 ,self .rect .bottom -10 ),2 )

class CityBreakableWall (Wall ):
    def __init__ (self ,x ,y ):
        super ().__init__ (x ,y )
        self .destructible =True 
        self .color =(100 ,100 ,120 )

    def draw (self ,surface ):
        pygame .draw .rect (surface ,self .color ,self .rect )
        pygame .draw .rect (surface ,(50 ,50 ,60 ),self .rect ,4 )
        pygame .draw .line (surface ,(60 ,60 ,80 ),self .rect .topleft ,self .rect .bottomright ,3 )
        pygame .draw .line (surface ,(60 ,60 ,80 ),self .rect .topright ,self .rect .bottomleft ,3 )

class CityHardWall (Wall ):
    def __init__ (self ,x ,y ):
        super ().__init__ (x ,y )
        self .destructible =True 
        self .health =2 
        self .color =(70 ,70 ,70 )

    def draw (self ,surface ):
        pygame .draw .rect (surface ,self .color ,self .rect )
        for i in range (0 ,40 ,10 ):
            pygame .draw .line (surface ,(30 ,30 ,30 ),(self .rect .left ,self .rect .top +i ),(self .rect .right ,self .rect .top +i ))
        if self .health <2 :
             pygame .draw .circle (surface ,(255 ,50 ,50 ),self .rect .center ,8 )

class CityBackground (Background ):
    def get_color (self ):
        return (20 ,24 ,35 )


class ForestWall (Wall ):
    def draw (self ,surface ):
        pygame .draw .rect (surface ,(120 ,120 ,130 ),self .rect )
        pygame .draw .rect (surface ,(100 ,100 ,110 ),self .rect ,3 )
        pygame .draw .arc (surface ,(50 ,200 ,50 ),self .rect ,0 ,3.14 ,2 )
        pygame .draw .line (surface ,(50 ,200 ,50 ),(self .rect .left +5 ,self .rect .top ),(self .rect .left +15 ,self .rect .bottom ),3 )
        pygame .draw .circle (surface ,(50 ,200 ,50 ),(self .rect .right -10 ,self .rect .top +10 ),6 )

class ForestBreakableWall (Wall ):
    def __init__ (self ,x ,y ):
        super ().__init__ (x ,y )
        self .destructible =True 
        self .color =(34 ,139 ,34 )

    def draw (self ,surface ):
        pygame .draw .rect (surface ,(20 ,100 ,20 ),(self .rect .x +5 ,self .rect .y +5 ,30 ,30 ))
        offsets =[(10 ,10 ),(30 ,10 ),(10 ,30 ),(30 ,30 ),(20 ,20 )]
        for ox ,oy in offsets :
            pygame .draw .circle (surface ,(60 ,180 ,60 ),(self .rect .x +ox ,self .rect .y +oy ),12 )
            pygame .draw .circle (surface ,(80 ,220 ,80 ),(self .rect .x +ox ,self .rect .y +oy ),8 )
        pygame .draw .circle (surface ,(255 ,255 ,255 ),(self .rect .x +15 ,self .rect .y +12 ),3 )
        pygame .draw .circle (surface ,(255 ,200 ,255 ),(self .rect .x +28 ,self .rect .y +25 ),3 )

class ForestHardWall (Wall ):
    def __init__ (self ,x ,y ):
        super ().__init__ (x ,y )
        self .destructible =True 
        self .health =2 
        self .color =(100 ,60 ,20 )

    def draw (self ,surface ):
        pygame .draw .rect (surface ,self .color ,self .rect )
        for i in range (5 ,40 ,8 ):
            pygame .draw .line (surface ,(70 ,40 ,10 ),(self .rect .x +i ,self .rect .y ),(self .rect .x +i ,self .rect .y +40 ),2 )
        pygame .draw .circle (surface ,(40 ,20 ,0 ),(self .rect .centerx ,self .rect .centery -5 ),6 )

class ForestBackground (Background ):
    def get_color (self ):
        return (34 ,100 ,34 )


class DesertWall (Wall ):
    def draw (self ,surface ):
        color =(230 ,180 ,100 )
        pygame .draw .rect (surface ,color ,self .rect )
        pygame .draw .rect (surface ,(200 ,150 ,80 ),self .rect ,3 )
        pygame .draw .ellipse (surface ,(180 ,130 ,60 ),(self .rect .left +10 ,self .rect .top +15 ,20 ,10 ),1 )
        pygame .draw .circle (surface ,(180 ,130 ,60 ),(self .rect .centerx ,self .rect .centery ),2 )

class DesertBreakableWall (Wall ):
    def __init__ (self ,x ,y ):
        super ().__init__ (x ,y )
        self .destructible =True 
        self .color =(210 ,160 ,120 )

    def draw (self ,surface ):
        pygame .draw .rect (surface ,self .color ,self .rect )
        pygame .draw .polygon (surface ,(150 ,100 ,80 ),[(self .rect .left ,self .rect .top ),(self .rect .centerx ,self .rect .centery ),(self .rect .left ,self .rect .bottom )],1 )
        pygame .draw .line (surface ,(150 ,100 ,80 ),(self .rect .right ,self .rect .top ),(self .rect .centerx ,self .rect .centery ),1 )

class DesertHardWall (Wall ):
    def __init__ (self ,x ,y ):
        super ().__init__ (x ,y )
        self .destructible =True 
        self .health =2 
        self .color =(160 ,160 ,160 )

    def draw (self ,surface ):
        pygame .draw .rect (surface ,self .color ,self .rect )
        if self .health >=2 :
            pygame .draw .rect (surface ,(130 ,130 ,130 ),(self .rect .left +5 ,self .rect .top +5 ,30 ,30 ))
        else :
            pygame .draw .rect (surface ,(140 ,100 ,100 ),(self .rect .left +5 ,self .rect .top +5 ,30 ,30 ))

class DesertBackground (Background ):
    def get_color (self ):
        return (245 ,222 ,179 )


class KeyAbstractFactory (ABC ):
    @abstractmethod 
    def create_wall (self ,x ,y ):
        pass 

    @abstractmethod 
    def create_breakable_wall (self ,x ,y ):
        pass 

    @abstractmethod 
    def create_hard_wall (self ,x ,y ):
        pass 

    @abstractmethod 
    def create_background (self ):
        pass 

    @abstractmethod 
    def create_thumbnail (self ,width ,height ):
        pass 


class CityFactory (KeyAbstractFactory ):
    def create_wall (self ,x ,y ):return CityWall (x ,y )
    def create_breakable_wall (self ,x ,y ):return CityBreakableWall (x ,y )
    def create_hard_wall (self ,x ,y ):return CityHardWall (x ,y )
    def create_background (self ):return CityBackground ()

    def create_thumbnail (self ,width ,height ):
        surf =pygame .Surface ((width ,height ))
        surf .fill ((20 ,24 ,35 ))
        for i in range (0 ,width ,20 ):
            pygame .draw .line (surf ,(0 ,100 ,100 ),(i ,0 ),(i ,height ),1 )
        for i in range (0 ,height ,20 ):
            pygame .draw .line (surf ,(0 ,100 ,100 ),(0 ,i ),(width ,i ),1 )
        pygame .draw .rect (surf ,(40 ,40 ,60 ),(10 ,height -40 ,20 ,40 ))
        pygame .draw .rect (surf ,(50 ,50 ,70 ),(40 ,height -60 ,30 ,60 ))
        pygame .draw .circle (surf ,(255 ,0 ,255 ),(width -30 ,30 ),10 )
        return surf 

class ForestFactory (KeyAbstractFactory ):
    def create_wall (self ,x ,y ):return ForestWall (x ,y )
    def create_breakable_wall (self ,x ,y ):return ForestBreakableWall (x ,y )
    def create_hard_wall (self ,x ,y ):return ForestHardWall (x ,y )
    def create_background (self ):return ForestBackground ()

    def create_thumbnail (self ,width ,height ):
        surf =pygame .Surface ((width ,height ))
        surf .fill ((34 ,100 ,34 ))
        import random 
        r =random .Random (42 )
        for _ in range (20 ):
            x ,y =r .randint (0 ,width ),r .randint (0 ,height )
            pygame .draw .circle (surf ,(20 ,80 ,20 ),(x ,y ),r .randint (5 ,15 ))
        return surf 

class DesertFactory (KeyAbstractFactory ):
    def create_wall (self ,x ,y ):return DesertWall (x ,y )
    def create_breakable_wall (self ,x ,y ):return DesertBreakableWall (x ,y )
    def create_hard_wall (self ,x ,y ):return DesertHardWall (x ,y )
    def create_background (self ):return DesertBackground ()

    def create_thumbnail (self ,width ,height ):
        surf =pygame .Surface ((width ,height ))
        surf .fill ((245 ,222 ,179 ))
        pygame .draw .polygon (surf ,(210 ,180 ,140 ),[(width //2 ,20 ),(width -20 ,height -20 ),(20 ,height -20 )])
        pygame .draw .circle (surf ,(255 ,215 ,0 ),(30 ,30 ),15 )
        return surf 
