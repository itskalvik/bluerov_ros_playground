import rospy
from mavros_msgs.msg import *
from mavros_msgs.srv import *
from geometry_msgs.msg import PoseStamped
from geographic_msgs.msg import GeoPoseStamped

# https://github.com/mavlink/mavros/blob/master/mavros_msgs/msg/CommandCode.msg
NAV_WAYPOINT = 16
TAKE_OFF = 22 
NAV_LAND = 21 

'''
uint8 FRAME_GLOBAL = 0
uint8 FRAME_LOCAL_NED = 1
uint8 FRAME_MISSION = 2
uint8 FRAME_GLOBAL_REL_ALT = 3
uint8 FRAME_LOCAL_ENU = 4
# http://docs.ros.org/api/mavros_msgs/html/msg/Waypoint.html
'''
FRAME = 0

class Modes:
    def __init__(self):
        pass

    def setArm(self):
        rospy.wait_for_service('mavros/cmd/arming')
        armService = rospy.ServiceProxy('mavros/cmd/arming', mavros_msgs.srv.CommandBool)
        armService(True)

    def auto_set_mode(self, mode="STABILIZE"):
        rospy.wait_for_service('mavros/set_mode')
        setModeService = rospy.ServiceProxy('mavros/set_mode', mavros_msgs.srv.SetMode)
        setModeService(custom_mode=mode)

    def wpPush(self,index,wps):
        rospy.wait_for_service('mavros/mission/push')
        wpPushService = rospy.ServiceProxy('mavros/mission/push', WaypointPush,persistent=True)
        wpPushService(start_index=0,waypoints=wps)
        print("Waypoint Pushed")


class stateMoniter:
    def __init__(self):
        self.state = State()
        
    def stateCb(self, msg):
        self.state = msg

class wpMissionCnt:

    def __init__(self):
        self.wp =Waypoint()
        
    def setWaypoints(self, command, is_current, autocontinue , x_lat, y_long, z_alt, param1=None):
        self.wp.frame = FRAME 
        self.wp.command = command 
        self.wp.is_current= is_current
        # enable taking and following upcoming waypoints automatically 
        self.wp.autocontinue = autocontinue
        self.wp.x_lat= x_lat 
        self.wp.y_long=y_long
        self.wp.z_alt= z_alt
        if param1 != None:
            self.wp.param1= param1

        return self.wp


def main():
    rospy.init_node('waypointMission', anonymous=True)
    rate = rospy.Rate(20.0)

    stateMt = stateMoniter()
    md = Modes()
    
    wayp0 = wpMissionCnt()
    wayp1 = wpMissionCnt()
    wayp2 = wpMissionCnt()
    wayp3 = wpMissionCnt()
    
    wps = [] #List to story waypoints
    
    w = wayp0.setWaypoints(84, True, True, 0, 0, 1, param1=10)
    wps.append(w)

    w = wayp1.setWaypoints(NAV_WAYPOINT, False, True, 10, 10, 1)
    wps.append(w)

    w = wayp2.setWaypoints(NAV_LAND, False, True, 0, 0, 1)
    wps.append(w)

    md.wpPush(0,wps)
    rospy.Subscriber("/mavros/state",State, stateMt.stateCb)
    local_pos_pub = rospy.Publisher("mavros/setpoint_raw/local", 
                                    PositionTarget, 
                                    queue_size=10)

    pose = PositionTarget()
    pose.position.z = 10000

    for i in range(100):
        if(rospy.is_shutdown()):
            break

        local_pos_pub.publish(pose)
        rate.sleep()

    # Switching the state to STABILIZE mode
    while not stateMt.state.mode=="STABILIZE":
        md.auto_set_mode("STABILIZE")
        rate.sleep()
    # Arming the drone
    while not stateMt.state.armed:
        md.setArm()
        rate.sleep()
    # Switching the state to AUTO mode
    while not stateMt.state.mode=="GUIDED":
        md.auto_set_mode("GUIDED")
        rate.sleep()

    while(rospy.is_shutdown() is False and stateMt.state.armed):
        local_pos_pub.publish(pose)
        rate.sleep()


if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass