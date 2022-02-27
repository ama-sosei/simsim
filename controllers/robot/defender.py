import math
from utils import (
	Utils,
	get_direction
)



class Defense(Utils):
	def _chk_ball_pos(self):
		if self.team == "B" and self.ball_pos[0] >= 0.3:
			return True
		elif self.team == "Y" and self.ball_pos[0] <= -0.3:
			return True
		else:
			return False

	def defense(self):
		return
		if not self.robot_pos:
			return

		if self._chk_ball_pos(): # Defense
			pass
		else:
			self.go_position(0, 0)



