#!/usr/bin/env python
import time

import rospy
import tf2_ros

from std_msgs.msg import String
from sensor_msgs.msg import Joy

from AbstractVirtualCapability import AbstractVirtualCapability, VirtualCapabilityServer, formatPrint
from KobukiTeleop import KobukiTeleop

# max_timeout has to be finetuned if Button-pressed events will not send
max_timeout = 0.005
pressed_a = 0
pressed_b = 0
pressed_x = 0
pressed_y = 0

tfBuffer = None
listener = None


def get_position():
	try:
		"""
		world_str = rospy.get_param('~world')
		position_str = rospy.get_param('~position')
		map_str = rospy.get_param('~map')
		"""

		current = tfBuffer.lookup_transform('world', 'turtlebot', rospy.Time(0), rospy.Duration(1.0))
		return [current.transform.translation.x, current.transform.translation.y, current.transform.translation.z]
	except (tf2_ros.LookupException, tf2_ros.ConnectivityException, tf2_ros.ExtrapolationException) as error:
		rospy.logwarn(error)
		return [100,100,100] #[repr(error).replace("\"", "").replace("\'", "")]


def callback(data):
	global pressed_a
	global pressed_b
	global pressed_x
	global pressed_y
	global pressed_pos

	buttons_abxy = data.buttons[:4]
	if any(buttons_abxy):
		#print(buttons_abxy)
		#pub.publish(str(buttons_abxy))
		pressed_a = time.time() if data.buttons[0] == 1 else pressed_a
		pressed_b = time.time() if data.buttons[1] == 1 else pressed_b
		pressed_x = time.time() if data.buttons[2] == 1 else pressed_x
		pressed_y = time.time() if data.buttons[3] == 1 else pressed_y

if __name__ == '__main__':
	#global pub
	pressed_a = 0
	pressed_b = 0
	pressed_x = 0
	pressed_y = 0

	pressed_pos = 0

	pub = rospy.Publisher('/joy_button_reader_input', String, queue_size=100)
	# subscribed to joystick inputs on topic "joy"
	rospy.Subscriber("joy", Joy, callback)
	# starts the node
	rospy.init_node("joy_button_reader", anonymous=True)
	rate = rospy.Rate(20)

	tfBuffer = tf2_ros.Buffer()
	listener = tf2_ros.TransformListener(tfBuffer)

	server = VirtualCapabilityServer(int(rospy.get_param('~semantix_port')))
	kobuki = KobukiTeleop(server)
	kobuki.functionality["pressedJoyA"] = lambda: (time.time() - pressed_a) < max_timeout
	kobuki.functionality["pressedJoyB"] = lambda: (time.time() - pressed_b) < max_timeout
	kobuki.functionality["pressedJoyX"] = lambda: (time.time() - pressed_x) < max_timeout
	kobuki.functionality["pressedJoyY"] = lambda: (time.time() - pressed_y) < max_timeout

	kobuki.functionality["GetKobukiPosition"] = get_position

	kobuki.start()

	while not rospy.is_shutdown() and server.running:
		rate.sleep()
