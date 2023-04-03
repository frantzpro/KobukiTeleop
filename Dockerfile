FROM ros:noetic
SHELL ["/bin/bash", "-c"]

ENV semantix_port=7500

# ROS-Noetic Setup
RUN sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list'
RUN apt-get update && apt-get install -y curl
RUN curl -s https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc | sudo apt-key add -
#RUN sudo apt-key adv --keyserver 'hkp://keyserver.ubuntu.com:80' --recv-key C1CF6E31E6BADE8868B172B4F42ED6FBAB17C654
RUN sudo apt-get update
RUN apt-get update && apt-get install -y python3-rosinstall python3-rosinstall-generator python3-wstool build-essential python3-rosdep python3-catkin-tools ros-noetic-vrpn-client-ros
#Install required kobuki packages, no included in standard install
RUN apt-get update && apt-get install -y  ros-noetic-control-toolbox ros-noetic-joy ros-noetic-urdf ros-noetic-ecl-exceptions ros-noetic-ecl-threads ros-noetic-tf ros-noetic-cv-bridge ros-noetic-swri-yaml-util ros-noetic-geometry-msgs
RUN apt-get update && apt-get install -y python-is-python3 python3-pip git iputils-ping liborocos-kdl-dev

#RUN sudo /ros_ws/src/mavros/mavros/scripts/install_geographiclib_datasets.sh
RUN rosdep update
RUN echo "source /opt/ros/noetic/setup.bash" >> ~/.bashrc
RUN source ~/.bashrc

# Add Files
ADD ros_ws /ros_ws
COPY protocols /etc

RUN cd ros_ws && source /opt/ros/noetic/setup.bash && rosdep install --from-paths . --ignore-src -r -y
# Build Ros-Pkg and build
#RUN cd /ros_ws && source /opt/ros/noetic/setup.bash && catkin build turtlebot ycos_cmd_vel_mux ycos_controllers ycos_velocity_smoother

COPY KobukiTeleop.py ros_ws/src/joy_button_reader/src
COPY AbstractVirtualCapability.py ros_ws/src/joy_button_reader/src
COPY requirements /var

RUN cd /ros_ws && source /opt/ros/noetic/setup.bash && catkin_make #turtlebot_teleop
RUN source /ros_ws/devel/setup.bash

# docker build -t joy_docker
# docker run -it --device=/dev/input/js0 --net=host joy_docker
# to open another terminal
#   docker container list --> <name>
#   docker exec -it <name> bash


#Setup Env
ENTRYPOINT ["/ros_entrypoint.sh"]

RUN echo "export ROS_MASTER_URI=http://172.20.37.158:11311" >> $HOME/.bashrc

#Start Joy Controler
#CMD source /ros_ws/devel/setup.bash && roslaunch joy_button_reader joy_button_reader.launch semantix_port:=${semantix_port}
#&& rosrun joy_button_reader joy_button_reader.py
#${semantix_port}
CMD bash
