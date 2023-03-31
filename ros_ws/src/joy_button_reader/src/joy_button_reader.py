#!/usr/bin/env python
import time

import rospy

from std_msgs.msg import String
from sensor_msgs.msg import Joy

from AbstractVirtualCapability import VirtualCapabilityServer
from KobukiTeleop import KobukiTeleop

max_timeout = 5

pressed_a = 0
pressed_b = 0
pressed_x = 0
pressed_y = 0


def callback(data):
	buttons_abxy = data.buttons[:4]
	if any(buttons_abxy):
		#print(buttons_abxy)
		pub.publish(str(buttons_abxy))
	pressed_a = time.time() if data.buttons[0] == 1 else pressed_a
	pressed_b = time.time() if data.buttons[1] == 1 else pressed_b
	pressed_x = time.time() if data.buttons[2] == 1 else pressed_x
	pressed_y = time.time() if data.buttons[3] == 1 else pressed_y


if __name__ == '__main__':
	global pub
	pub = rospy.Publisher('/joy_button_reader_input', String, queue_size=100)
	# subscribed to joystick inputs on topic "joy"
	rospy.Subscriber("joy", Joy, callback)
	# starts the node
	rospy.init_node("joy_button_reader", anonymous=True)
	rate = rospy.Rate(20)

	server = VirtualCapabilityServer(int(rospy.get_param('~semantix_port')))
	kobuki = KobukiTeleop(server)
	kobuki.functionality["pressedJoyA"] = lambda: (time.time() - pressed_a) < max_timeout
	kobuki.functionality["pressedJoyB"] = lambda: (time.time() - pressed_b) < max_timeout
	kobuki.functionality["pressedJoyX"] = lambda: (time.time() - pressed_x) < max_timeout
	kobuki.functionality["pressedJoyY"] = lambda: (time.time() - pressed_y) < max_timeout
	kobuki.start()

	while not rospy.is_shutdown() and server.running:
		rate.sleep()
