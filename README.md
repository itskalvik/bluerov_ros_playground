# BlueRov-ROS-playground
Bluerov2 Gazebo simulation.

# Setup
1. Install [freebuoyancy_gazebo](https://github.com/bluerobotics/freebuoyancy_gazebo#install)
    plugin for buoyancy simulation.
2. Install [ardupilot_gazebo/add_link](https://github.com/patrickelectric/ardupilot_gazebo/tree/add_link#usage-)
    plugin for ardupilot-gazebo communication. *add_link* is a branch that provides actuation over sdf links, after the `git clone`, it's necessary to run `git checkout add_link`.
3. Run BlueRov2 Gazebo model
    1. Download bluerov_ros_playground
        ```bash
        git clone https://github.com/kdkalvik/bluerov_ros_playground/
        cd bluerov_ros_playground/
        ```
 
    2. Run Gazebo model
        ```bash
        cd bluerov_ros_playground
        source gazebo.sh
        gazebo worlds/underwater.world -u
        # Start the simulation
        ```
 
4. Execute ArduPilot SITL
    ```bash
    sim_vehicle.py -f gazebo-bluerov2 -I 0 -j4 -D -L RATBeach --console
    ```

The console will start to display the output if the connection was successful.
