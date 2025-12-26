import pygame 

class AuthView :
    def __init__ (self ,screen_width ,screen_height ,repo ):
        self .width =screen_width 
        self .height =screen_height 
        self .repo =repo 
        self .font =pygame .font .Font (None ,40 )
        self .small_font =pygame .font .Font (None ,30 )


        self .mode ='LOGIN'
        self .username =''
        self .password =''
        self .active_field ='username'
        self .message =''
        self .message_color =(255 ,255 ,255 )


        center_x =self .width //2 
        self .rect_user =pygame .Rect (center_x -150 ,200 ,300 ,50 )
        self .rect_pass =pygame .Rect (center_x -150 ,280 ,300 ,50 )
        self .rect_btn_main =pygame .Rect (center_x -100 ,360 ,200 ,50 )
        self .rect_btn_switch =pygame .Rect (center_x -100 ,430 ,200 ,40 )


        self .char_pos =(100 ,450 )
        self .char_rect =pygame .Rect (80 ,410 ,40 ,60 )
        self .wave_frame =0 
        self .is_waving =False 

    def handle_event (self ,event ):

        if event .type ==pygame .MOUSEMOTION :
            if self .char_rect .collidepoint (event .pos ):
                self .is_waving =True 
            else :
                self .is_waving =False 

        if event .type ==pygame .MOUSEBUTTONDOWN :
            if self .rect_user .collidepoint (event .pos ):
                self .active_field ='username'
            elif self .rect_pass .collidepoint (event .pos ):
                self .active_field ='password'
            elif self .rect_btn_main .collidepoint (event .pos ):
                return self ._submit ()
            elif self .rect_btn_switch .collidepoint (event .pos ):
                self ._switch_mode ()

        if event .type ==pygame .KEYDOWN :
            if event .key ==pygame .K_TAB :
                self .active_field ='password'if self .active_field =='username'else 'username'
            elif event .key ==pygame .K_RETURN :
                return self ._submit ()
            elif event .key ==pygame .K_BACKSPACE :
                if self .active_field =='username':
                    self .username =self .username [:-1 ]
                else :
                    self .password =self .password [:-1 ]
            else :

                if self .active_field =='username':
                    self .username +=event .unicode 
                else :
                    self .password +=event .unicode 
        return None 

    def _switch_mode (self ):
        self .mode ='REGISTER'if self .mode =='LOGIN'else 'LOGIN'
        self .message =''

    def _submit (self ):
        username =self .username .strip ()
        password =self .password .strip ()

        if not username or not password :
            self .message ="Fields cannot be empty"
            self .message_color =(255 ,50 ,50 )
            return None 

        if self .mode =='LOGIN':
            user =self .repo .login_user (username ,password )
            if user :
                return {'action':'AUTH_SUCCESS','user':user }
            else :
                self .message ="Invalid Credentials"
                self .message_color =(255 ,50 ,50 )
        else :
            user_id =self .repo .register_user (username ,password )
            if user_id :
                self .message ="Registration Success! Please Login."
                self .message_color =(50 ,255 ,50 )
                self .mode ='LOGIN'
                self .password =''
            else :
                self .message ="Username already exists"
                self .message_color =(255 ,50 ,50 )
        return None 

    def draw (self ,surface ):
        surface .fill ((30 ,30 ,40 ))


        pygame .draw .rect (surface ,(50 ,50 ,50 ),(0 ,500 ,self .width ,100 ))


        self ._draw_character (surface )


        title_text ="Login"if self .mode =='LOGIN'else "Register"
        t_surf =self .font .render (title_text ,True ,(255 ,255 ,255 ))
        surface .blit (t_surf ,(self .width //2 -t_surf .get_width ()//2 ,100 ))



        color_u =(100 ,100 ,255 )if self .active_field =='username'else (200 ,200 ,200 )
        pygame .draw .rect (surface ,(50 ,50 ,60 ),self .rect_user )
        pygame .draw .rect (surface ,color_u ,self .rect_user ,2 )
        u_surf =self .small_font .render (self .username ,True ,(255 ,255 ,255 ))
        surface .blit (u_surf ,(self .rect_user .x +10 ,self .rect_user .y +15 ))


        color_p =(100 ,100 ,255 )if self .active_field =='password'else (200 ,200 ,200 )
        pygame .draw .rect (surface ,(50 ,50 ,60 ),self .rect_pass )
        pygame .draw .rect (surface ,color_p ,self .rect_pass ,2 )
        p_mask ="*"*len (self .password )
        p_surf =self .small_font .render (p_mask ,True ,(255 ,255 ,255 ))
        surface .blit (p_surf ,(self .rect_pass .x +10 ,self .rect_pass .y +15 ))


        surface .blit (self .small_font .render ("Username:",True ,(200 ,200 ,200 )),(self .rect_user .x ,self .rect_user .y -25 ))
        surface .blit (self .small_font .render ("Password:",True ,(200 ,200 ,200 )),(self .rect_pass .x ,self .rect_pass .y -25 ))



        btn_text ="Login"if self .mode =='LOGIN'else "Register"
        pygame .draw .rect (surface ,(50 ,200 ,50 ),self .rect_btn_main ,border_radius =5 )
        b_surf =self .font .render (btn_text ,True ,(255 ,255 ,255 ))
        surface .blit (b_surf ,b_surf .get_rect (center =self .rect_btn_main .center ))


        switch_text ="Need Account? Register"if self .mode =='LOGIN'else "Have Account? Login"
        s_surf =self .small_font .render (switch_text ,True ,(150 ,150 ,255 ))
        surface .blit (s_surf ,s_surf .get_rect (center =self .rect_btn_switch .center ))


        if self .message :
            m_surf =self .small_font .render (self .message ,True ,self .message_color )
            surface .blit (m_surf ,(self .width //2 -m_surf .get_width ()//2 ,500 ))

    def _draw_character (self ,surface ):
        x ,y =self .char_pos 
        import math 


        if self .is_waving :
            self .wave_frame +=0.2 
        else :
            self .wave_frame =0 





        suit_color =(255 ,255 ,255 )
        skin_color =(255 ,200 ,200 )
        helmet_color =(200 ,50 ,50 )
        hand_color =(255 ,200 ,200 )


        pygame .draw .rect (surface ,suit_color ,(x -15 ,y -30 ,30 ,30 ))


        pygame .draw .circle (surface ,skin_color ,(x ,y -45 ),15 )


        pygame .draw .rect (surface ,helmet_color ,(x -15 ,y -60 ,30 ,15 ))

        pygame .draw .circle (surface ,(255 ,100 ,100 ),(x ,y -60 ),5 )




        wave_angle =math .sin (self .wave_frame )*0.5 
        if not self .is_waving :wave_angle =2.0 
        else :wave_angle -=1.0 

        arm_len =25 
        hand_x =x +15 +math .cos (wave_angle )*arm_len 
        hand_y =y -40 +math .sin (wave_angle )*arm_len 


        pygame .draw .line (surface ,suit_color ,(x +15 ,y -40 ),(hand_x ,hand_y ),6 )

        pygame .draw .circle (surface ,hand_color ,(int (hand_x ),int (hand_y )),7 )


        pygame .draw .line (surface ,suit_color ,(x -15 ,y -40 ),(x -30 ,y -20 ),6 )
        pygame .draw .circle (surface ,hand_color ,(x -30 ,y -20 ),7 )


        pygame .draw .rect (surface ,(50 ,50 ,100 ),(x -15 ,y ,12 ,10 ))
        pygame .draw .rect (surface ,(50 ,50 ,100 ),(x +3 ,y ,12 ,10 ))
