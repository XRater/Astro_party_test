from __future__ import division, print_function, unicode_literals

import pyglet

from const import *

class Images(object):
	
	ship = pyglet.resource.image('Image/ship.png')
	bullet = pyglet.resource.image('Image/bullet.png')
	space = pyglet.resource.image('Image/space.png')
	unfired_bullet = pyglet.resource.image('Image/unfired_bullet.png')
	