from panda3d.core import *
from panda3d.bullet import *
#loadPrcFileData("", "threading-model Cull/Draw")
loadPrcFileData("", "show-frame-rate-meter  1")
#loadPrcFileData("", "sync-video 0")
from direct.showbase import ShowBase
from direct.showbase.DirectObject import DirectObject

from camera import CameraControler
from robot import Robot

class Demo(DirectObject):
    def __init__(self):
        #basic stuff
        self.base = ShowBase.ShowBase()
        self.base.disableMouse()

        #use a better camera controller
        self.cam_driver=CameraControler(pos=(0,0,0), offset=(0, 2, 2),)

        #setup bullet
        self.world_np = render.attach_new_node('World')
        #debug stuff
        self.debug_np = self.world_np.attach_new_node(BulletDebugNode('Debug'))
        self.debug_np.show()
        self.debug_np.node().show_wireframe(True)
        self.debug_np.node().show_constraints(True)
        self.debug_np.node().show_bounding_boxes(False)
        self.debug_np.node().show_normals(False)
        #the bullet world
        self.world = BulletWorld()
        self.world.set_gravity(Vec3(0, 0, -9.81))
        self.world.set_debug_node(self.debug_np.node())

        # Plane (static)
        plane_shape = BulletPlaneShape(Vec3(0, 0, 1), 0)
        plane_np = self.world_np.attach_new_node(BulletRigidBodyNode('Ground'))
        plane_np.node().add_shape(plane_shape)
        plane_np.set_pos(0, 0, 0)
        self.world.attach_rigid_body(plane_np.node())

        # Box (dynamic)
        self.make_box((0.25, 0.25, 0.5), (0, 0, 1))
        self.make_box((0.25, 0.25, 0.25), (-1, 1, 1))
        self.make_box((0.1, 0.1, 0.1), (0, 1, 1))

        #the robot
        self.robot=Robot('models/arm7.egg')
        self.joints=self.robot.get_joint_names()
        self.current_joint=self.joints[0]

        #some lights
        ambient = AmbientLight("ambientLight")
        ambient.set_color((0.3, 0.3, 0.35, 1))
        dir_light = DirectionalLight("directionalLight")
        dir_light.set_direction((-5, -5, -5))
        dir_light.set_color((1, 1, 0.8, 1))
        render.set_light(render.attach_new_node(ambient))
        render.set_light(render.attach_new_node(dir_light))

        #keys for controlling the joints
        #wsad is for camera so ... [q] and [e]?
        #tab to switch joints or 1-9 keys
        self.key_map = {'left':False, 'right':False}
        self.accept('q', self.key_map.__setitem__, ['left', True])
        self.accept('q-up', self.key_map.__setitem__, ['left', False])
        self.accept('e', self.key_map.__setitem__, ['right', True])
        self.accept('e-up', self.key_map.__setitem__, ['right', False])
        self.accept('tab',self.get_next_robot_joint)
        self.accept('1',self.get_next_robot_joint,[1])
        self.accept('2',self.get_next_robot_joint,[2])
        self.accept('3',self.get_next_robot_joint,[3])
        self.accept('4',self.get_next_robot_joint,[4])
        self.accept('5',self.get_next_robot_joint,[5])
        self.accept('6',self.get_next_robot_joint,[6])
        self.accept('7',self.get_next_robot_joint,[7])
        self.accept('8',self.get_next_robot_joint,[8])
        self.accept('9',self.get_next_robot_joint,[9])
        self.roatation_speed=20.0
        self.slide_speed=0.1

        #each joint has it's own orientation, so we need some mask
        # to rotate it in the right plane or at all
        #looks like in this case it's all the R component (as in HPR)
        self.rot_mask={'Bone':Vec3(0,0,0),
                       'Bone.001':Vec3(0,0,1),
                       'Bone.002':Vec3(0,0,1),
                       'Bone.003':Vec3(0,0,0),
                       'Bone.004':Vec3(0,0,1),
                       'Bone.005':Vec3(0,0,0),
                       'Bone.006':Vec3(0,0,0),
                       'Bone.007':Vec3(0,0,1),
                       'Bone.008':Vec3(0,0,1),
                       'Bone.009':Vec3(0,0,1),
                      }
        #if the joint shouldn't rotate, maybe it should move?
        #if so in what direction?
        self.slide_mask={'Bone':Vec3(0,0,0),
                       'Bone.001':Vec3(0,0,0),
                       'Bone.002':Vec3(0,0,0),
                       'Bone.003':Vec3(0,1,0),
                       'Bone.004':Vec3(0,0,0),
                       'Bone.005':Vec3(0,0,1),
                       'Bone.006':Vec3(1,0,0),
                       'Bone.007':Vec3(0,0,0),
                       'Bone.008':Vec3(0,0,0),
                       'Bone.009':Vec3(0,0,0),
                      }
        #adding colliders to the robot arm,
        #boxes work best/fast with bullet so we make a lot of boxes
        #{'Name_of_the_bone':[(size_of_the_box), (pos_of_the_box), (hpr_of_the_box)]}
        boxes={'Bone':[
                      ((0.11, 0.11, 0.11), (0,0,-0.1),(0,0,0),)
                      ],
               'Bone.001':[
                      ((0.11, 0.11, 0.10), (0,0,0.18),(-12,0,0),)
                      ],
               'Bone.002':[
                      ((0.05, 0.05, 0.25), (-0.2,0.48,0.52),(-12,-45,0),)
                      ],
                'Bone.004':[
                      ((0.1, 0.1, 0.1), (-0.3,0.45,0.62),(-12,-20,0),)
                      ],
                'Bone.007':[
                      ((0.05, 0.05, 0.25), (-0.27,1.1,0.45),(-12,-110,0),)
                      ],
               }
        self.bodies={}
        for joint, box_list in boxes.items():
            np = self.world_np.attach_new_node(BulletRigidBodyNode('shapes'))
            joint_pos=self.robot.joints[joint].get_pos(render)
            joint_hpr=self.robot.joints[joint].get_pos(render)
            for size, pos, hpr in box_list:
                shape=BulletBoxShape(Vec3(*size))
                pos=Point3(*pos)+joint_pos
                hpr=Point3(*hpr)+joint_hpr
                np.node().add_shape(shape, TransformState.make_pos_hpr(pos, hpr))
            self.world.attach_rigid_body(np.node())
            np.node().set_kinematic(True)
            self.bodies[joint]=np
        # Task
        taskMgr.add(self.update, 'updateWorld')

    def make_box(self, size, pos):
        shape = BulletBoxShape(Vec3(*size))
        np = self.world_np.attach_new_node(BulletRigidBodyNode('Box'))
        np.node().set_mass(1.0)
        np.node().add_shape(shape)
        np.set_pos(*pos)
        self.world.attachRigidBody(np.node())

    def get_next_robot_joint(self, index=None):
        if index is None:
            index=1+self.joints.index(self.current_joint)
            if index>=len(self.joints):
                index=0
        self.current_joint=self.joints[index]
        print('Current joint:',self.joints[index] )

    def update(self, task):
        dt = globalClock.getDt()
        if self.key_map['left']:
            direction=1
        elif self.key_map['right']:
            direction=-1
        else:
            direction=0
        speed=self.rot_mask[self.current_joint]*self.roatation_speed*dt*direction
        if speed==Vec3(0,0,0):
            speed=self.slide_mask[self.current_joint]*self.slide_speed*dt*direction
            self.robot.slide_joint(self.current_joint, speed)
        else:
            self.robot.rotate_joint(self.current_joint, speed)

        #move the colliders to where the joints are
        #there should/could be a simpler way to do this
        #but so far that's the only reliable way I know of
        for joint in self.robot.actor.getJoints():
            name=joint.getName()
            if name in self.bodies:
                body=self.bodies[name]
                vt = JointVertexTransform(joint)
                mat = Mat4()
                vt.get_matrix(mat)
                body.set_mat(mat)

        self.world.do_physics(dt, 10, 1.0/320.0)
        return task.cont

d=Demo()
d.base.run()
