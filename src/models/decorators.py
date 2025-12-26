
class PlayerDecorator :
    """
    Base Decorator. Forward calls to the wrapped player.
    """
    def __init__ (self ,player ):
        self .player =player 
        self .rect =player .rect 

    def __getattr__ (self ,name ):
         return getattr (self .player ,name )

    def update (self ,walls ):
        self .player .update (walls )

class GhostWalkDecorator (PlayerDecorator ):
    def __init__ (self ,player ,duration =5.0 ):
        super ().__init__ (player )
        self .duration =duration 
        self .timer =duration 
        self .active =True 

    def update (self ,walls ):
        if self .active :
            self .timer -=1 /60.0 
            if self .timer <=0 :
                self .active =False 
                return 
            solid_walls =[w for w in walls if not w .destructible ]
            self .player .update (solid_walls )
        else :
            self .player .update (walls )
