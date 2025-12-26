
import heapq 

class Node :
    def __init__ (self ,parent =None ,position =None ):
        self .parent =parent 
        self .position =position 
        self .g =0 
        self .h =0 
        self .f =0 

    def __eq__ (self ,other ):
        return self .position ==other .position 

def astar (maze ,start ,end ):
    """
    Returns a list of tuples as a path from the given start to the given end in the given maze.
    Maze is a grid where 0 is walkable and 1 is a wall.
    """
    start_node =Node (None ,start )
    end_node =Node (None ,end )

    open_list =[]
    closed_list =[]

    heapq .heappush (open_list ,(start_node .f ,id (start_node ),start_node ))


    outer_iterations =0 
    max_iterations =len (maze )*len (maze [0 ])*2 

    while len (open_list )>0 :
        outer_iterations +=1 
        if outer_iterations >max_iterations :
            return []

        current_node =heapq .heappop (open_list )[2 ]
        closed_list .append (current_node )

        if current_node ==end_node :
            path =[]
            current =current_node 
            while current is not None :
                path .append (current .position )
                current =current .parent 
            return path [::-1 ]

        children =[]
        for new_position in [(0 ,-1 ),(0 ,1 ),(-1 ,0 ),(1 ,0 )]:
            node_position =(current_node .position [0 ]+new_position [0 ],current_node .position [1 ]+new_position [1 ])

            if node_position [0 ]>(len (maze )-1 )or node_position [0 ]<0 or node_position [1 ]>(len (maze [0 ])-1 )or node_position [1 ]<0 :
                continue 

            if maze [node_position [0 ]][node_position [1 ]]!=0 :
                continue 

            children .append (Node (current_node ,node_position ))

        for child in children :
            if child in closed_list :
                continue 

            child .g =current_node .g +1 
            child .h =((child .position [0 ]-end_node .position [0 ])**2 )+((child .position [1 ]-end_node .position [1 ])**2 )
            child .f =child .g +child .h 



            heapq .heappush (open_list ,(child .f ,id (child ),child ))

    return []
