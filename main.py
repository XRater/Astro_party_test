import six
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cocos.director import director
from cocos.layer import *
from cocos.scene import Scene
from cocos.scenes.transitions import *
from cocos.actions import *
from cocos.sprite import *
from cocos.menu import *
from cocos.text import *

from const import sc
import socket
import status
import threading

import pyglet
from pyglet import gl, font
from pyglet.window import key

class OptionsMenu( Menu ):
	def __init__(self):
		super( OptionsMenu, self).__init__('TETRICO') 
		
		self.font_title['font_name'] = 'Edit Undo Line BRK'
		self.font_title['font_size'] = 72//screen_scale
		self.font_title['color'] = (245,184,16,255)

		self.font_item['font_name'] = 'Courier New',
		self.font_item['color'] = (32,16,32,255)
		self.font_item['font_size'] = 40//screen_scale
		self.font_item_selected['font_name'] = 'Courier New'
		self.font_item_selected['color'] = (255, 0, 255,255)
		self.font_item_selected['font_size'] = 54//screen_scale

		self.menu_anchor_y = CENTER
		self.menu_anchor_x = CENTER

		items = []

		items.append( ToggleMenuItem('Show FPS:', self.on_show_fps, director.show_FPS) )
		items.append( MenuItem('Back', self.on_quit) )
		self.create_menu( items, shake(), shake_back() )


	def on_quit( self ):
		self.parent.switch_to( 0 )

	def on_show_fps( self, value ):
		director.show_FPS = value


class MainMenu(Menu):
	
	def __init__(self):
		super(MainMenu, self).__init__('Shooter')

		self.font_title['font_name'] = 'Edit Undo Line BRK'
		self.font_title['font_size'] = 72//screen_scale
		self.font_title['color'] = (245,184,16,255)

		self.font_item['font_name'] = 'Courier New',
		self.font_item['color'] = (32,16,32,255)
		self.font_item['font_size'] = 40//screen_scale
		self.font_item_selected['font_name'] = 'Courier New'
		self.font_item_selected['color'] = (255, 0, 255,255)
		self.font_item_selected['font_size'] = 54//screen_scale

		self.menu_anchor_y = CENTER
		self.menu_anchor_x = CENTER
		
		items = []
		items.append( MenuItem('Start as server', self.on_newgame_server) )
		items.append( MenuItem('Start as client', self.on_newgame_client) )
		items.append( MenuItem('Options', self.on_options) )
		items.append( MenuItem('Quit', self.on_quit) )
		
		self.create_menu( items, shake(), shake_back() )
		
	def on_quit(self):
		pyglet.app.exit()
	
	def on_newgame_server(self):
		#import game
		status.host = 'server'
		self.parent.switch_to(2)
		#director.push( FadeTransition(game.get_newgame('server'), 1.5 ) )
	
	def on_options( self ):
		self.parent.switch_to(1)
	
	def on_newgame_client(self):
		#import game
		status.host = 'client'
		self.parent.switch_to(2)
		
		#director.push( FadeTransition(game.get_newgame('client'), 1.5 ) )
		
class Waiting_layer(Layer):
	
	def __init__(self):
		super(Waiting_layer, self).__init__()
		self.unconnected = True
		
	def on_enter(self):
		self.ready_to_start = False
		if self.unconnected:
			self.find_partner()
		#t1 = threading.Thread(self.find_partner(), daemon=True)
		#t1.start()
	
	def find_partner(self):
		
		self.sock = socket.socket()
		if status.host == 'server':
			self.sock.bind(('0.0.0.0', 9050))
			self.sock.listen(1)
			self.conn, addr = self.sock.accept()
			self.unconnected = False
			import game
			director.push( FadeTransition(game.get_newgame(self.sock, self.conn), 1.5 ) )
		if status.host == 'client':
			self.sock.connect(('localhost', 9050))
			self.unconnected = False
			import game
			director.push( FadeTransition(game.get_newgame(self.sock, False), 1.5 ) )
		
		
if __name__ == "__main__":	
	
	screen_scale = sc
	director.init(width=1920//sc, height=1080//sc, caption="Shooter", fullscreen=(sc == 1))
	main_scene = Scene()
	main_scene.add( MultiplexLayer(MainMenu(), OptionsMenu(), Waiting_layer()),z=1 ) 
	director.run(main_scene)