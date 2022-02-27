import math, struct, time
from controller import Robot
from attacker import Attack
from defender import Defense
from utils import (
	TIME_STEP,
	ROBOT_NAMES,
	N_ROBOTS,
	STRUCT_FMT,
	debug,
	get_direction
)

class RCJSoccerRobot(Attack, Defense):
	def __init__(self):
		self.robot = Robot()
		self.name = self.robot.getName()
		self.team = self.name[0]
		self.player_id = int(self.name[1])

		self.receiver = self.robot.getDevice("supervisor receiver")
		self.receiver.enable(TIME_STEP)

		self.team_emitter = self.robot.getDevice("team emitter")
		self.team_receiver = self.robot.getDevice("team receiver")
		self.team_receiver.enable(TIME_STEP)

		self.ball_receiver = self.robot.getDevice("ball receiver")
		self.ball_receiver.enable(TIME_STEP)

		self.gps = self.robot.getDevice("gps")
		self.gps.enable(TIME_STEP)

		self.compass = self.robot.getDevice("compass")
		self.compass.enable(TIME_STEP)

		self.sonar_left = self.robot.getDevice("distancesensor left")
		self.sonar_left.enable(TIME_STEP)
		self.sonar_right = self.robot.getDevice("distancesensor right")
		self.sonar_right.enable(TIME_STEP)
		self.sonar_front = self.robot.getDevice("distancesensor front")
		self.sonar_front.enable(TIME_STEP)
		self.sonar_back = self.robot.getDevice("distancesensor back")
		self.sonar_back.enable(TIME_STEP)

		self.left_motor = self.robot.getDevice("left wheel motor")
		self.right_motor = self.robot.getDevice("right wheel motor")

		self.left_motor.setPosition(float("+inf"))
		self.right_motor.setPosition(float("+inf"))

		self.left_motor.setVelocity(0.0)
		self.right_motor.setVelocity(0.0)

	@debug(16)
	def parse_supervisor_msg(self, packet: str) -> dict:
		unpacked = struct.unpack("?", packet)
		return {"waiting_for_kickoff": unpacked[0]}

	@debug(8)
	def get_new_data(self) -> dict:
		packet = self.receiver.getData()
		self.receiver.nextPacket()
		return self.parse_supervisor_msg(packet)

	@debug(8)
	def is_new_data(self) -> bool:
		return bool(self.receiver.getQueueLength() > 0)

	# team
	@debug(16)
	def parse_team_msg(self, packet: str) -> dict:
		unpacked = struct.unpack(STRUCT_FMT, packet)
		return {
			"player_id": unpacked[0],
			"robot_pos": unpacked[1:3],
		}

	@debug(8)
	def get_new_team_data(self) -> dict:
		packet = self.team_receiver.getData()
		self.team_receiver.nextPacket()
		return (self.parse_team_msg(packet))

	@debug(8)
	def is_new_team_data(self) -> bool:
		return bool(self.team_receiver.getQueueLength() > 0)

	@debug(8)
	def send_data_to_team(self) -> None:
		if self.ball_pos:
			data = [
				self.player_id,
				*self.robot_pos
			]
		else:
			data = [
				self.player_id,
				*self.robot_pos
			]
		packet = struct.pack(STRUCT_FMT, *data)
		self.team_emitter.send(packet)

	# ball
	@debug(8)
	def get_new_ball_data(self) -> dict:
		"""Read new data from IR sensor

		Returns:
			dict: Direction and strength of the ball signal
			Direction is normalized vector indicating the direction of the
			emitter with respect to the receiver's coordinate system.
			Example:
				{
					'direction': [0.23, -0.10, 0.96],
					'strength': 0.1
				}
		"""
		_ = self.ball_receiver.getData()
		data = {
			"direction": self.ball_receiver.getEmitterDirection(),
			"strength": self.ball_receiver.getSignalStrength(),
		}
		self.ball_receiver.nextPacket()
		return data

	@debug(8)
	def is_new_ball_data(self) -> bool:
		return bool(self.ball_receiver.getQueueLength() > 0)

	# GPS
	@debug(8)
	def get_gps_coordinates(self) -> list:
		"""Get new GPS coordinates

		Returns:
			List containing x and y values
		"""
		gps_values = self.gps.getValues()
		return [gps_values[0], gps_values[1]]

	@debug(8)
	def get_compass_heading(self) -> float:
		"""Get compass heading in radians

		Returns:
			float: Compass value in radians
		"""
		compass_values = self.compass.getValues()
		# Add math.pi/2 (90) so that the heading 0 is facing opponent's goal
		rad = math.atan2(compass_values[0], compass_values[1]) + (math.pi / 2)
		if rad < -math.pi:
			rad = rad + (2 * math.pi)
		return rad

	@debug(8)
	def get_sonar_values(self) -> dict:
		"""Get new values from sonars.

		Returns:
			dict: Value for each sonar.
		"""
		return {
			"left": self.sonar_left.getValue(),
			"right": self.sonar_right.getValue(),
			"front": self.sonar_front.getValue(),
			"back": self.sonar_back.getValue(),
		}

	def run(self):
		#if self.player_id in [2,3]:
		#	return
		while self.robot.step(TIME_STEP) != -1:
			data, team_data = self.fetch_data()

			if data:
		#		self.go_position(0, 0)
		#		continue
				if team_data:
					if self.team == "B":
						if max([i["robot_pos"][1] for i in team_data]) < self.robot_pos[1]:
							self.attack()
							#self.defense()
						else:
							self.attack()
					else:
						if min([i["robot_pos"][1] for i in team_data]) > self.robot_pos[1]:
							#self.defense()
							self.attack()
						else:
							self.attack()
				else:
					if self.player_id in [1, 2]:
						self.attack()
					elif self.player_id == 3:
						self.attack()
						#self.defense()

RCJSoccerRobot().run()
