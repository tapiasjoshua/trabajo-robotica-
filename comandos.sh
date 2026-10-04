#!/usr/bin/env bash
# Comandos usados en la actividad (ejecutar cada bloque en una terminal distinta).
# Probado con ROS2 Humble / Jazzy y el driver oficial de Universal Robots.

# 0) Instalacion (una sola vez)
#   sudo apt install ros-$ROS_DISTRO-ur

# 1) Levantar URSim UR5e en Docker con el URCap External Control
#   ros2 run ur_client_library start_ursim.sh -m ur5e
#   PolyScope: http://192.168.56.101:6080/vnc.html

# 2) Driver del robot (Terminal 1)
#   ros2 launch ur_robot_driver ur_control.launch.py ur_type:=ur5e robot_ip:=192.168.56.101 launch_rviz:=false

# 3) (Opcional, bono no realizado) MoveIt 2 + RViz (Terminal 2)
#   ros2 launch ur_moveit_config ur_moveit.launch.py ur_type:=ur5e launch_rviz:=true

# 4) En PolyScope: Play a Programa2 -> OK en el popup -> esperar 5 s
#    El driver debe mostrar: "Robot connected to reverse interface. Ready to receive control commands."
# 5) (Opcional, bono) En RViz: Plan -> Execute

# Verificaciones utiles
#   ros2 control list_controllers
#   ros2 topic echo /joint_states --once
