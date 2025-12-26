"""
Singleton Class to control game
"""
import pygame 
class GameManager :

    _instance =None 
    def __new__ (cls ):
        if cls ._instance is None :
            cls ._instance =super (GameManager ,cls ).__new__ (cls )
            cls ._instance ._initialized =False 

        return cls ._instance 

    def __init__ (self ):
        if self ._initialized :
            return 
        self ._initialized =True 

        self .screen_width =800 
        self .screen_height =700 
        self .caption ="Bomberman 2D - Multiplayer"
        self .fps =60 
        self .running =True 
        self .current_user =None 
        self .clock =pygame .time .Clock ()

    def set_user (self ,user_data ):
        self .current_user =user_data 

    def get_user (self ):
        return self .current_user 

    def quit_game (self ):
        self .running =False 
