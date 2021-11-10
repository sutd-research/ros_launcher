#!/usr/bin/env python
# license removed for brevity
import rospy
from std_srvs.srv._SetBool import SetBool, SetBoolRequest, SetBoolResponse
import subprocess, shlex
import os, signal
import sys

launcher = {}

class Launcher():
    def __init__(self, node_name, launcher_name, args):
        self.running = False
        self.process = None
        self.launcher_name = launcher_name
        
        self.args = []
        if type(args)==str:
            # Convert arguments to list in case of string input
            self.args = args.split(" ")
        elif type(args)==dict:
            # Create ros launch command in case of dictionary input
            self.args = []
            try:
                pkg_name = args['pkg']
                launch_file_name = args['launch_file']
                self.args.append('roslaunch')
                self.args.append(pkg_name)
                self.args.append(launch_file_name)

                del args['pkg']
                del args['launch_file']

                # Append any other misc arguments
                for key in args:
                    self.args.append(args[key])
            except Exception:
                rospy.loginfo(node_name + ":" + launcher_name + ": ROS Launch file not provided")
                
        print (self.args)

        rospy.Service(node_name + '/' + launcher_name, SetBool, self.callback) 
        rospy.loginfo(node_name + '/' + launcher_name + " launcher registered")

    def __del__(self):
        if not(self.process is None):
            self.process.terminate()
            self.process = None
    
    def callback(self, req):
        if (req.data == True):
            try:
                self.process = subprocess.Popen(self.args, stdout=sys.stdout, stderr=sys.stderr)
            except Exception as ex:
                rospy.logerr(str(ex))
            msg = "Started Process"
        else:
            if not(self.process is None):
                try:
                    self.process.terminate()
                except Exception as ex:
                    rospy.logwarn(str(ex))
            msg = "Stopped Process"
        rospy.loginfo(self.launcher_name + " : " + msg)
        return SetBoolResponse(True, msg)

def ros_launcher():
    rospy.init_node('ros_launcher')
    node_name = rospy.get_name()

    # Get Parameters
    global launcher
    launcher_names = rospy.get_param(node_name + '/launchers')
    launcher_names = launcher_names.replace(" ","").split(",")
    
    for launcher_name in launcher_names:
        args = rospy.get_param(node_name + '/' + launcher_name)
        launcher[launcher_name] = Launcher(node_name, launcher_name, args)

    print (node_name + " : ROS Launcher Ready!")
    rospy.spin()

if __name__ == '__main__':
    try:
        ros_launcher()
    except rospy.ROSInterruptException:
        pass


