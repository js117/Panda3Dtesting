from panda3d.core import *
from panda3d.bullet import *
from direct.actor.Actor import Actor

#note: some functions use CamelCase because some older version of the
#Actor class (panda3d 1.9.0?) didn't have snake_case names

class Robot():
    def __init__(self, model):
        self.actor=Actor(model)
        self.actor.reparent_to(render)

        self.joints={}
        for joint in self.actor.getJoints():
            self.joints[joint.getName()]=self.actor.controlJoint(None, 'modelRoot', joint.get_name())

    def get_joint_names(self):
        return [joint.getName() for joint in self.actor.getJoints()]

    def rotate_joint(self, joint_name, hpr):
        joint=self.joints[joint_name]
        joint.set_hpr(joint,hpr)

    def slide_joint(self, joint_name, xyz):
        joint=self.joints[joint_name]
        joint.set_pos(joint,xyz)



