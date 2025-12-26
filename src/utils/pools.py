
class ObjectPool :
    def __init__ (self ,class_type ,initial_size =10 ,max_size =50 ):
        self .class_type =class_type 
        self .pool =[]
        self .max_size =max_size 

        for _ in range (initial_size ):
            self .pool .append (self .class_type ())

    def get (self ):
        if self .pool :
            obj =self .pool .pop ()
        else :
            obj =self .class_type ()
        return obj 

    def return_obj (self ,obj ):
        if len (self .pool )<self .max_size :
            obj .reset ()
            self .pool .append (obj )
