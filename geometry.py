
class point():
	
	def __init__(self, x, y):
		self.x = x
		self.y = y

class line():
	
	def __init__(self, point1, point2):
		
		self.a = point2.y - point1.y
		self.b =  point1.x - point2.x
		self.c = -point1.x*(point2.y - point1.y) + point2.y*(point2.x - point1.x)

class geometry():

	def intersect_lines(line1, line2):
		if (line1.a*line2.b - line2.a*line1.b):
			x = -((line1.c*line2.b - line2.c*line1.b)/(line1.a*line2.b - line2.a*line1.b))//1
		else:
			x = 999999
		if (line1.a*line2.b - line2.a*line1.b):
			y = -((line1.a*line2.c - line2.a*line1.c)/(line1.a*line2.b - line2.a*line1.b))//1
		else:
			y = 999999
		return(point(x, y))
		
	def point_on_line_segment(point1, point2, point3):
		if ((point1.x <= point2.x) and (point1.x >= point3.x)) or ((point1.x >= point2.x) and (point1.x <= point3.x)):
			t = 1
		else:
			if ((point1.y <= point2.y) and (point1.y >= point3.y)) or ((point1.y >= point2.y) and (point1.y <= point3.y)):
				t = 1
			else:
				return(False)
		if (t == 1):
			if	abs(point2.x - point1.x) + abs(point3.x - point1.x) - abs(point3.x - point2.x) <= 5:
				if abs(point2.y - point1.y) + abs(point3.y - point1.y) - abs(point3.y - point2.y) <= 5:
					return(True)