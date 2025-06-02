#!/usr/bin/env python
import rospy
from geometry_msgs.msg import PoseStamped
from mavros_msgs.msg import State
from mavros_msgs.srv import CommandBool, SetMode

current_state = State()

def state_cb(msg):
    global current_state
    current_state = msg

def main():
    rospy.init_node('takeoff_hover')

    rospy.Subscriber('mavros/state', State, state_cb)
    local_pos_pub = rospy.Publisher('mavros/setpoint_position/local', PoseStamped, queue_size=10)

    rospy.wait_for_service('mavros/cmd/arming')
    rospy.wait_for_service('mavros/set_mode')
    arm_srv = rospy.ServiceProxy('mavros/cmd/arming', CommandBool)
    mode_srv = rospy.ServiceProxy('mavros/set_mode', SetMode)

    rate = rospy.Rate(20)

    pose = PoseStamped()
    pose.pose.position.x = 0
    pose.pose.position.y = 0
    pose.pose.position.z = 1

    # send a few setpoints before starting
    for _ in range(100):
        pose.header.stamp = rospy.Time.now()
        local_pos_pub.publish(pose)
        rate.sleep()

    last_req = rospy.Time.now()
    while not rospy.is_shutdown():
        if current_state.mode != 'OFFBOARD' and (rospy.Time.now() - last_req > rospy.Duration(5.0)):
            mode_srv(0, 'OFFBOARD')
            last_req = rospy.Time.now()
        else:
            if not current_state.armed and (rospy.Time.now() - last_req > rospy.Duration(5.0)):
                arm_srv(True)
                last_req = rospy.Time.now()

        pose.header.stamp = rospy.Time.now()
        local_pos_pub.publish(pose)
        rate.sleep()

if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass
