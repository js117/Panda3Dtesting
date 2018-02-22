from math import pi, sin, cos
 
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence
from panda3d.core import Point3
import sys
 
class MyApp(ShowBase):
	def __init__(self):
		ShowBase.__init__(self)
		
		base.enableParticles()
		# TODO: 
		# Follow the rest of the physics tutorial: https://www.panda3d.org/manual/index.php/Enabling_physics_on_a_node 

 
		# Disable the camera trackball controls.
		#self.disableMouse()
 
		# Load the environment model.
		self.scene = self.loader.loadModel("models/environment")
		# Reparent the model to render.
		self.scene.reparentTo(self.render)
		# Apply scale and position transforms on the model.
		self.scene.setScale(0.25, 0.25, 0.25)
		self.scene.setPos(-8, 42, 0)
 
		# Add the spinCameraTask procedure to the task manager.
		#self.taskMgr.add(self.spinCameraTask, "SpinCameraTask")
		
		
		self.m = Actor("models/arm6.egg")
		self.m.setScale(5, 5, 5)
		self.m.reparentTo(self.render)
		
		
		
		print("------- Joints: ---------")
		print(self.m.listJoints())
		'''
		J1_y = ob.pose.bones['Bone.001']	  # base rotation / shoulder yaw
		J2_y = ob.pose.bones['Bone.002']	  # shoulder pitch
		J3_y = ob.pose.bones['Bone.004']	  # elbow pitch
		J4_y = ob.pose.bones['Bone.007']	  # elbow roll
		J5_y = ob.pose.bones['Bone.008']	  # wrist pitch
		J6_y = ob.pose.bones['Bone.009']	  # wrist roll
		'''
		self.J = [0,0,0,0,0,0,0]
		self.J[1] = self.m.exposeJoint(None, 'modelRoot', 'Bone.001')
		self.J[2] = self.m.exposeJoint(None, 'modelRoot', 'Bone.002')
		self.J[3] = self.m.exposeJoint(None, 'modelRoot', 'Bone.004')
		self.J[4] = self.m.exposeJoint(None, 'modelRoot', 'Bone.007')
		self.J[5] = self.m.exposeJoint(None, 'modelRoot', 'Bone.008')
		self.J[6] = self.m.exposeJoint(None, 'modelRoot', 'Bone.009')
		
		self.Jpos = [0,0,0,0,0,0,0]
		self.Jpos[1] = 0 # ID == 1
		self.Jpos[2] = 0 # ID == 2
		self.Jpos[3] = 0 # ID == 3
		self.Jpos[4] = 0 # ID == 4
		self.Jpos[5] = 0 # ID == 5
		self.Jpos[6] = 0 # ID == 6
		
		self.currentJoint = 1 # default to joint ID == 1
		
		# Set up key input
		self.accept('escape', sys.exit)
		self.accept('1', self.switchJoint, [1])
		self.accept('2', self.switchJoint, [2])
		self.accept('3', self.switchJoint, [3])
		self.accept('4', self.switchJoint, [4])
		self.accept('5', self.switchJoint, [5])
		self.accept('6', self.switchJoint, [6])
		
		self.accept('q', self.moveJoint, [6])
		self.accept('w', self.moveJoint, [6])
		
		
		

		
		'''
		self.pandaActor = Actor("models/panda-model",
								{"walk": "models/panda-walk4"})
		self.pandaActor.setScale(0.005, 0.005, 0.005)
		self.pandaActor.reparentTo(self.render)
		# Loop its animation.
		self.pandaActor.loop("walk")
 
		# Create the four lerp intervals needed for the panda to
		# walk back and forth.
		pandaPosInterval1 = self.pandaActor.posInterval(13,
														Point3(0, -10, 0),
														startPos=Point3(0, 10, 0))
		pandaPosInterval2 = self.pandaActor.posInterval(13,
														Point3(0, 10, 0),
														startPos=Point3(0, -10, 0))
		pandaHprInterval1 = self.pandaActor.hprInterval(3,
														Point3(180, 0, 0),
														startHpr=Point3(0, 0, 0))
		pandaHprInterval2 = self.pandaActor.hprInterval(3,
														Point3(0, 0, 0),
														startHpr=Point3(180, 0, 0))
 
		# Create and play the sequence that coordinates the intervals.
		self.pandaPace = Sequence(pandaPosInterval1,
								  pandaHprInterval1,
								  pandaPosInterval2,
								  pandaHprInterval2,
								  name="pandaPace")
		self.pandaPace.loop()
		'''
 
	def switchJoint(self, i):
		self.currentJoint = i
		print("Current joint switched to :: "+str(i))
		
	def moveJoint(self, i):
		print("Moving selected joint :: "+str(self.currentJoint))
 
 
	# Define a procedure to move the camera.
	def spinCameraTask(self, task):
		angleDegrees = task.time * 6.0
		angleRadians = angleDegrees * (pi / 180.0)
		self.camera.setPos(20 * sin(angleRadians), -20.0 * cos(angleRadians), 3)
		self.camera.setHpr(angleDegrees, 0, 0)
		return Task.cont
 
app = MyApp()
app.run()