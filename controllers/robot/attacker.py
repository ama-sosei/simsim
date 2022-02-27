import math
from utils import (
	Utils,
	debug,
	log,
	get_direction
)

class Attack(Utils):
	@debug(4)
	def attack(self):
		if not self.robot_pos:
			return
		elif not self.ball_pos:
			return
		direction = get_direction(self.ball_pos)
		if self.direction == 0:
			self.motor(10, 10)
		else:
			self.motor(self.direction * 8, self.direction * -8)

