
import socket 
import threading 
import pickle 
import struct 

class NetworkConfig :
    PORT =5555 

def send_msg (sock ,data ):
    """Helper to send data with length prefix."""
    serialized =pickle .dumps (data )

    msg =struct .pack ('>I',len (serialized ))+serialized 
    sock .sendall (msg )

def recv_msg (sock ,buffer ):
    """
    Helper to extract one complete message from buffer.
    Returns: (decoded_obj, remaining_buffer) or (None, buffer_if_incomplete)
    """
    if len (buffer )<4 :
        return None ,buffer 


    msg_len =struct .unpack ('>I',buffer [:4 ])[0 ]

    if len (buffer )<4 +msg_len :
        return None ,buffer 


    msg_data =buffer [4 :4 +msg_len ]
    remaining =buffer [4 +msg_len :]

    try :
        obj =pickle .loads (msg_data )
        return obj ,remaining 
    except Exception as e :
        print (f"Packet Corrupt: {e }")
        return None ,remaining 



class GameServer :
    def __init__ (self ):
        self .server_socket =socket .socket (socket .AF_INET ,socket .SOCK_STREAM )
        self .server_socket .setsockopt (socket .SOL_SOCKET ,socket .SO_REUSEADDR ,1 )
        self .server_socket .bind (('',NetworkConfig .PORT ))
        self .server_socket .listen (2 )
        self .clients =[]
        self .running =True 
        self .last_data =None 
        self .lock =threading .Lock ()
        self .lock =threading .Lock ()
        self .lock =threading .Lock ()
        self .send_lock =threading .Lock ()
        self .current_theme_idx =0 
        self .host_name ="Host"
        self .p2_name =None 

    def start (self ,host_name ):
        self .host_name =host_name 
        threading .Thread (target =self ._accept_clients ,daemon =True ).start ()

    def _accept_clients (self ):
        print ("Server waiting for connections...")
        while self .running :
            try :
                client ,addr =self .server_socket .accept ()
                print (f"Connection from {addr }")
                self .clients .append (client )



                threading .Thread (target =self ._handle_client ,args =(client ,),daemon =True ).start ()
            except Exception as e :

                break 

    def _handle_client (self ,client ):

        buffer =b''

        while self .running :
            try :

                try :
                    chunk =client .recv (16384 )
                    if not chunk :break 
                    buffer +=chunk 
                except :
                    break 


                while True :
                    obj ,buffer =recv_msg (None ,buffer )
                    if obj is None :break 



                    if obj .get ('event')=='HELLO':
                         p2 =obj .get ('name','P2')
                         print (f"[SERVER] Received HELLO from {p2 }")
                         with self .lock :
                             self .p2_name =p2 

                         self ._send_lobby_state (client )


                    with self .lock :
                        self .last_data =obj 


                    self ._echo_to_others (client ,obj )

            except Exception as e :
                print (f"Server Client Error: {e }")
                if client in self .clients :
                    self .clients .remove (client )
                break 

    def _send_lobby_state (self ,client ):
        packet ={
        'event':'LOBBY_STATE',
        'host_name':self .host_name ,
        'theme_idx':self .current_theme_idx 
        }
        try :
             send_msg (client ,packet )
        except :pass 

    def _echo_to_others (self ,sender ,data ):
        with self .send_lock :
            for c in self .clients :
                if c !=sender :
                    try :
                        send_msg (c ,data )
                    except :
                        pass 

    def send_to_all (self ,data ):
        with self .send_lock :
            for c in self .clients :
                try :
                    send_msg (c ,data )
                except :
                    pass 

    def close (self ):
        self .running =False 
        try :
            self .server_socket .close ()
        except :
            pass 

class GameClient :
    def __init__ (self ):
        self .client_socket =socket .socket (socket .AF_INET ,socket .SOCK_STREAM )
        self .connected =False 
        self .buffer =b''

    def connect (self ,ip ,local_name ):
        try :
            self .client_socket .settimeout (0.5 )
            self .client_socket .connect ((ip ,NetworkConfig .PORT ))
            self .client_socket .settimeout (None )

            self .client_socket .setblocking (True )
            self .connected =True 


            print (f"[CLIENT] Connected. Sending HELLO name={local_name }")
            send_msg (self .client_socket ,{'event':'HELLO','name':local_name })

            return True 
        except Exception as e :

            return False 
        except Exception as e :

            return False 

    def send (self ,data ):
        if self .connected :
            try :

                send_msg (self .client_socket ,data )
            except Exception as e :
                print (f"Network Error (Send): {e }")
                self .connected =False 

    def receive (self ):
        if not self .connected :
            return None 

        try :

            import select 
            readable ,_ ,_ =select .select ([self .client_socket ],[],[],0 )

            if readable :

                while True :
                    try :


                        chunk =self .client_socket .recv (16384 )
                        if not chunk :

                            print ("Server closed connection.")
                            self .connected =False 
                            break 
                        self .buffer +=chunk 


                        r ,_ ,_ =select .select ([self .client_socket ],[],[],0 )
                        if not r :break 

                    except Exception as e :
                        print (f"Socket Error during read: {e }")
                        self .connected =False 
                        break 


            latest_data =None 
            while True :
                obj ,self .buffer =recv_msg (None ,self .buffer )
                if obj is None :break 
                latest_data =obj 

            return latest_data 

        except Exception as e :
            print (f"Network Error (Recv): {e }")
            self .connected =False 
            pass 

        return None 
