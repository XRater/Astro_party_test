from __future__ import division, print_function, unicode_literals
import six

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pyglet
from pyglet.gl import *
from pyglet import image
from pyglet.window import key
from pyglet.window import mouse

from cocos.director import *
from cocos.menu import *
from cocos.scene import *
from cocos.layer import *
from cocos.actions import *
from cocos.sprite import Sprite
from cocos.text import Label
import cocos.collision_model as cm

from const import *
from Images import *
from geometry import *
import status

import random
import math
import socket
import threading

class GameView(Layer):
	
	def __init__(self, model):
		super(GameView, self).__init__()
		
		self.model = model
		self.add(self.model)
		
	
class GameModel(Layer):
		
	def __init__(self):
		super(GameModel, self).__init__()
		if status.host == 'server':
			self.ship = Ship(self, 1)
			self.ship_enemy = Ship(self, 2)
		if status.host == 'client':
			self.ship = Ship(self, 2)
			self.ship_enemy = Ship(self, 1)
		self.ship.player = True
		self.ship.ctrl.resume_controller()
		self.ship.ctrl.allow_move()
		self.ship_enemy.ctrl.resume_controller()
		self.add(self.ship)
		self.add(self.ship_enemy)
		self.ship.targets = [self.ship_enemy]
		self.ship_enemy.targets = [self.ship]

	
	def set_connection(self, connection):
		self.conn = connection
		
class Ship(Sprite):
	
	def __init__(self, model, number):
	
		super(Ship, self).__init__(Images.ship)
		self.model = model
		self.scale = 1/sc
		self.number = number
		self.player = False
		
		if number == 1:
			self.position = (w - 100//sc, h - 100//sc)
			self.rotation = 180
		if number == 2:
			self.position = (100//sc, 100//sc)
			self.rotation = 0
			
			
		self.speed = 6
		
		self.pressed_keys = []
		self.ctrl = Player_controler(self)
		self.add(self.ctrl)
		self.elapsed = 0
		
		self.bullets = 3
		self.recharging = False
		self.bull_label = Bullet_Label(self)
		self.add(self.bull_label)
		self.fired_bullets = []
	
	def recharge_bullets(self):
		self.recharging = True
		self.schedule_interval(self.step, recharge_time)
	
	def stop_recharge_bullets(self):
		self.recharging = False
		self.unschedule(self.step)
		
	def step(self, dt):
		self.bullets += 1
		self.bull_label.bullets = self.bullets
		self.bull_label.restore_bullet()
		if (self.bullets == 3):
			self.recharging = False
			self.stop_recharge_bullets()
	
	def move_ship(self,):
		x, y = self.position
		q = self.rotation
		dx = 0
		dy = 0
		dq = 0
		if (self.pressed_keys.count('q')):
			dq = -ship_rotspeed
		dx = round(math.cos(math.radians(-q))*self.speed/sc, 0)//1
		dy = round(math.sin(math.radians(-q))*self.speed/sc, 0)//1
		
		
		if ((x + dx) >= 28//sc) and ((x + dx) <= w - 28//sc):
			x = x + dx
		if ((y + dy) >= 28//sc) and ((y + dy) <= h - 28//sc):
			y = y + dy
		self.position = (x, y)
		self.rotation += dq
		
		for bullet in self.fired_bullets:
			bullet.move_bullet()
		
		self.bull_label.rotate(self.pressed_keys.count('q'))
	
	def shoot(self):
		if self.bullets:
			if (self.recharging == False):
				self.recharge_bullets()
			self.bullets -= 1
			self.bull_label.bullets = self.bullets
			self.bull_label.fire_bullet()
			bullet = Bullet(self.model, self)
			self.model.add(bullet)
			self.fired_bullets.append(bullet)
			
	def add_key(self, key):
		if key == 'q':
			if (self.pressed_keys.count('q') == 0):
				self.pressed_keys.append('q')
		if key == 'e':
			self.shoot()
	
	def remove_key(self, key):
		
		if key == 'q':
			if (self.pressed_keys.count('q')):
				self.pressed_keys.remove('q')
				
	def destroy(self):
		if self.player:
			self.model.ship_enemy.targets.remove(self)
			print('You lost')
		if self.player == False:
			self.model.ship.targets.remove(self)
			print('You won')
		self.kill()
				
				
class Player_controler(Layer):
	
	is_event_handler = True
	
	def __init__(self, ship):
		super(Player_controler, self).__init__()
		self.ship = ship
		self.elapsed = 0
		self.paused = True
		self.listen_keyboard = False
		
	def on_key_press(self, k, m ):
		
		if self.paused or (self.listen_keyboard == False):
			return False

		if k in (key.E, key.Q):
			if k == key.Q:
				if (self.ship.pressed_keys.count('q') == 0):
					self.ship.model.conn.send_msg('0+q')
					self.ship.elapsed = 0
					self.ship.pressed_keys.append('q')
			elif k == key.E:
				self.ship.shoot()
				self.ship.model.conn.send_msg('2+e')
		return False
		
	def on_key_release(self, k, m):
		
		if self.paused or (self.listen_keyboard == False):
			return False

		if k in (key.E, key.Q):
			if k == key.Q:
				if (self.ship.pressed_keys.count('q')):
					self.ship.pressed_keys.remove('q')
	
					self.ship.model.conn.send_msg('0-q')
		return False
	
	def allow_move(self):
		self.listen_keyboard = True
	
	def forbid_move(self):
		self.listen_keyboard = False
		
	def pause_controller( self ):
		self.paused = True
		self.unschedule( self.step )
		
	def resume_controller( self ):
		self.paused = False
		self.schedule_interval( self.step, 0.008)

	def step( self, dt ):
		self.elapsed += dt
		if self.elapsed > 0.015:
			self.elapsed = 0
			self.ship.move_ship()
			
class Bullet(Sprite):
	
	def __init__(self, model, ship):
	
		super(Bullet, self).__init__(Images.bullet)
		self.model = model
		self.ship = ship
		self.scale = 1/sc
		self.position = self.ship.position
		self.rotation = self.ship.rotation
		self.speed = 15

		
	def move_bullet(self):
	
		x, y = self.position
		q = self.rotation
		
		dx = 0
		dy = 0
		dx = math.cos(math.radians(-q))*self.speed//sc
		dy = math.sin(math.radians(-q))*self.speed//sc
		x = x + dx
		y = y + dy
		if ((x + dx) <= -15//sc) or ((x + dx) >= w + 15//sc):
			self.destroy()
		if ((y + dy) <= -15//sc) or ((y + dy) >= h +15//sc):
			self.destroy()
			
		self.position = (x, y)
		if ((x + dx) >= 0) and ((x + dx) <= w) and ((y + dy) <= h) and ((y + dy) >= 0):
			self.aim_check()
	
	def aim_check(self):
		
		x, y = self.position
		for enemy in self.ship.targets:
			ax, ay = enemy.position
			if (collide_check(self.position, self.rotation, enemy.position, enemy.rotation)):
				enemy.destroy()
				self.model.conn.send_msg('1')
				self.destroy()
		
	def destroy(self):
		
		self.ship.fired_bullets.remove(self)
		self.kill()
		
			
class Bullet_Label(Layer):

	is_event_handler = True
	
	def __init__(self, ship):
		self.ship = ship
		super(Bullet_Label, self).__init__()
		self.bullets = 3
		self.phase = 0
		self.unfired_bullets = {}
		c1 = unfired_bullet(1, 0)
		c2 = unfired_bullet(2, 0)
		c3 = unfired_bullet(3, 0)
		self.unfired_bullets[1] = c1
		self.unfired_bullets[2] = c2
		self.unfired_bullets[3] = c3
		self.add(c1)
		self.add(c2)
		self.add(c3)
	
	def restore_bullet(self):
		new_bullet = unfired_bullet(self.bullets, self.phase)
		self.unfired_bullets[self.bullets] = new_bullet
		self.add(new_bullet)
	
	def fire_bullet(self):
		fired_bullet = self.unfired_bullets[self.bullets + 1]
		self.unfired_bullets[self.bullets + 1] = None
		fired_bullet.kill()
		
	def rotate(self, ship_rot):
		if (ship_rot == 0):
			self.phase += bullets_rot_speed
			for number in range (3):
				number += 1
				if (self.unfired_bullets[number] != None):
					bullet = self.unfired_bullets[number]
					bullet.rotate(ship_rot)
		else:
			self.phase = self.phase + bullets_rot_speed + ship_rotspeed
			for number in range (3):
				number += 1
				if (self.unfired_bullets[number] != None):
					bullet = self.unfired_bullets[number]
					bullet.rotate(ship_rot)
	
		
class unfired_bullet(Sprite):
			
	def __init__(self, number, phase):
		super(unfired_bullet, self).__init__(Images.unfired_bullet)
		self.scale = 1/sc
		self.number = number
		self.rotation = self.number*120 + phase
		q = self.rotation
		x = math.cos(math.radians(-q))*60//1
		y = math.sin(math.radians(-q))*60//1
		self.position = (x, y)
	
	def rotate(self, ship_rot):
		if (ship_rot == 0):
			self.rotation += bullets_rot_speed
		else:
			self.rotation = self.rotation + bullets_rot_speed + ship_rotspeed
		q = self.rotation
		x = round(math.cos(math.radians(-q))*60/sc, 0)//1
		y = round(math.sin(math.radians(-q))*60/sc, 0)//1
		self.position = (x, y)


def collide_check(bull_pos, bull_rot, target_pos, target_rot):
	
	dx = round(math.cos(math.radians(target_rot))*37/sc, 0)//1
	dy = round(math.sin(math.radians(target_rot))*37/sc, 0)//1
	x, y = target_pos
	x = x + dx
	y = y + dy
	target = point(x, y)
	x = x - dx*2
	y = y - dy*2
	dx = round(math.cos(math.radians(target_rot + 90))*25/sc, 0)//1
	dy = round(math.sin(math.radians(target_rot + 90))*25/sc, 0)//1
	target_tail1 = point(x + dx, y + dy)
	target_tail2 = point(x - dx, y - dy)
	x, y = bull_pos
	bullet = point(x, y)
	intersection_point = geometry.intersect_lines(line(target, bullet), line(target_tail1, target_tail2))
	if geometry.point_on_line_segment(intersection_point, target_tail1, target_tail2):
		if geometry.point_on_line_segment(bullet, intersection_point, target):
			return(True)
		else:
			return(False)
	else:
		return(False)
		
class Connection_listener(Layer):
	
	def __init__(self, model, sock, conn):
		super(Connection_listener, self).__init__()
		self.model = model
		self.model.set_connection(self)
		#self.sock = socket.socket()
		self.sock = sock
		if status.host == 'server':
			self.conn = conn
		#if status.host == 'server':
		#	self.sock.bind(('0.0.0.0', 9050))
		#	self.sock.listen(1)
		#if status.host == 'client':
		#	self.sock.connect(('localhost', 9050))
		t1 = threading.Thread(target=self.listen_for_msg, daemon=True)
		t1.start()
	
	def listen_for_msg(self):
		#if status.host == 'server':
		#	self.conn, addr = self.sock.accept()
		while True:
			if status.host == 'server':
				data = self.conn.recv(1024)
			if status.host == 'client':
				data = self.sock.recv(1024) 
			if data:
				data = str(data, 'utf-8')
				if data[0] == '0':
					if data[1] == '+':
						self.model.ship_enemy.add_key(data[2])
					if data[1] == '-':
						self.model.ship_enemy.remove_key(data[2])
				if data[0] == '1':
					self.model.ship.destroy()
				if data[0] == '2':
					self.model.ship_enemy.add_key('e')
					
				
	def send_msg(self, msg):
		msg = bytes(msg, 'utf-8')
		if status.host == 'server':
			self.conn.send(msg)
		if status.host == 'client':
			self.sock.send(msg)
			
def get_newgame(sock, conn = False):

	global w
	global h
	w, h = director.get_window_size()
	#status.host = host
	
	gamescene = Scene()	
	model = GameModel()
	
	view = GameView(model)
	bg = Sprite(Images.space, (960//sc, 540//sc))
	view.add(bg, z=-1, name="view")	
	gamescene.add(view, z=1, name="view")
	
	connecttion = Connection_listener(model, sock, conn)
	
	return gamescene