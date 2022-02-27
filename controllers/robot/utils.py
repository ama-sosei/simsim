import math
from datetime import (
	datetime,
	date
)

TIME_STEP = 64
ROBOT_NAMES = ["B1", "B2", "B3", "Y1", "Y2", "Y3"]
N_ROBOTS = len(ROBOT_NAMES)
STRUCT_FMT = "iff"
#player_id, robo_x, robo_y, ball_x, ball_y, ball_z
DEBUG_LEVEL = 0

def log(log_message, lv=16):
	if DEBUG_LEVEL < lv:
		return
	print(f"{date.today()}: {log_message}")
	try:
		with open(f"{date.today()}.log", "a") as f:
			f.write(f"{datetime.today()}: {log_message}\n")
	except Exception as e:
		print(e)

def debug(lv, ignore_arg_len=1):
	"""
		0 -> No output
		1 -> Error
		2 -> WARNING
		4 -> EVENT
		8 -> INFO
		16 -> DEBUG
	"""
	def _debug(func):
		def wrapper(*args, **kwargs):
			_args = ', '.join(map(str,args[ignore_arg_len:]))
			_kwargs = ', '.join([f'{key}={val}' for key,val in kwargs.items()])
			try:
				result = func(*args, **kwargs)
				log(f"{func.__name__}({_args}{', ' if _args and _kwargs else ''}{_kwargs}) -> {result}", lv)
				return result
			except Exception as e:
				log(f"[ERROR]: {e}", 1)
				raise e from e
		return wrapper
	return _debug


@debug(8)
def get_direction(ball_vector: list, base:int=0.13) -> int:
	"""Get direction to navigate robot to face the ball
	Args:
		ball_vector (list of floats): Current vector of the ball with respect
			to the robot.

	Returns:
		int: 0 = forward, -1 = right, 1 = left
	"""
	if -base <= ball_vector[1] < base:
		return 0
	return -1 if ball_vector[1] < 0 else 1


class Utils:
	@debug(4)
	def motor(self,left:int, right:int) -> None:
		self.left_motor.setVelocity(-left)
		self.right_motor.setVelocity(-right)

	@debug(4)
	def fetch_data(self):
		if self.is_new_data():
			data = self.get_new_data()

			team_data = []
			while self.is_new_team_data():
				team_data.append(self.get_new_team_data())
				# Do something with team data

			if self.is_new_ball_data():
				ball_data = self.get_new_ball_data()
				self.ball_pos = ball_data["direction"]
				self.ball_strength = ball_data["strength"]
			else:
				self.ball_pos = []
				self.ball_strength = 0
			
			# Get data from compass
			self.heading = self.get_compass_heading()
			# Get GPS coordinates of the robot
			self.robot_pos = self.get_gps_coordinates()
			# Get data from sonars
			self.sonar_values = self.get_sonar_values()
			# Compute the speed for motors
			if self.ball_pos:
				self.direction = get_direction(self.ball_pos)
			else:
				self.direction = 0
			return (data, team_data)
		else:
			return (None, None)

	@debug(4)
	def go_position(self, x, y):
		angle = math.degrees(
			math.atan2(
				abs(y - self.robot_pos[1]),
				abs(x - self.robot_pos[0])
			)
		)
		if angle < 0:
			angle += 360
		
		heading = math.degrees(self.heading)
		if heading < 0:
			heading += 360
		target_angle = angle + heading

		if target_angle > 360:
			target_angle -= 360
		
		print(target_angle)

		if target_angle >= 345 or target_angle <= 15:
			self.motor(-10, -10)
		elif target_angle < 180:
			self.motor(5, -5)
		else:
			self.motor(-5, 5)

