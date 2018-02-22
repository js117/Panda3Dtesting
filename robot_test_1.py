from pandac.PandaModules import * 
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence
from panda3d.core import Point3

from random import random
import sys
from math import pi, sin, cos
 
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
		
		
		self.m = Actor("models/arm7.egg")
		self.m.setScale(5, 5, 5)
		self.m.reparentTo(self.render)
		
		
		
		print("------- Joints: ---------")
		print(self.m.listJoints())
		
		#J1_y = ob.pose.bones['Bone.001']	  # base rotation / shoulder yaw
		#J2_y = ob.pose.bones['Bone.002']	  # shoulder pitch
		#J3_y = ob.pose.bones['Bone.004']	  # elbow pitch
		#J4_y = ob.pose.bones['Bone.007']	  # elbow roll
		#J5_y = ob.pose.bones['Bone.008']	  # wrist pitch
		#J6_y = ob.pose.bones['Bone.009']	  # wrist roll
		
		self.J = [0,0,0,0,0,0,0]
		self.J[1] = self.m.controlJoint(None, 'modelRoot', 'Bone.001')
		self.J[2] = self.m.controlJoint(None, 'modelRoot', 'Bone.002')
		self.J[3] = self.m.controlJoint(None, 'modelRoot', 'Bone.004')
		self.J[4] = self.m.controlJoint(None, 'modelRoot', 'Bone.007')
		self.J[5] = self.m.controlJoint(None, 'modelRoot', 'Bone.008')
		self.J[6] = self.m.controlJoint(None, 'modelRoot', 'Bone.009')
		
		
		self.Jpos = [0,0,0,0,0,0,0]
		self.Jpos[1] = 0 # ID == 1
		self.Jpos[2] = 0 # ID == 2
		self.Jpos[3] = 0 # ID == 3
		self.Jpos[4] = 0 # ID == 4
		self.Jpos[5] = 0 # ID == 5
		self.Jpos[6] = 0 # ID == 6
		
		self.currentJoint = 1 # default to joint ID == 1
		
		self.currentDegPerStep = 1
		self.degPerStepChangeFactor = 1.1
		
		# Set up key input
		self.accept('escape', sys.exit)
		self.accept('1', self.switchJoint, [1])
		self.accept('2', self.switchJoint, [2])
		self.accept('3', self.switchJoint, [3])
		self.accept('4', self.switchJoint, [4])
		self.accept('5', self.switchJoint, [5])
		self.accept('6', self.switchJoint, [6])
		
		self.accept('q', self.moveJoint, [0])
		self.accept('w', self.moveJoint, [1])
		
		self.accept('p', self.printJoints, [0])
		self.accept('0', self.zeroJoints, [0])
		
		# Debug joint hierarchy visually: 
		walkJointHierarchy(self.m, self.m.getPartBundle('modelRoot'), None)

		
		
 
	def switchJoint(self, i):
		self.currentJoint = i
		print("Current joint switched to :: "+str(i))

	def printJoints(self, i):
		print("---")
		for j in range(1, len(self.J)):
			if j == 1:
				this_hpr = self.J[j].getHpr(self.render)
			else:
				this_hpr = self.J[j].getHpr(self.J[j-1])
			#this_hpr = self.J[j].getHpr(self.J[j])
			this_h = round(this_hpr[0], 4)
			this_p = round(this_hpr[1], 4)
			this_r = round(this_hpr[2], 4)
			print("Joint :: "+str(j)+ " // "+"H: "+str(this_h)+" / "+"P: "+str(this_p)+" / "+"R: "+str(this_r)+" / "); 
			print("---")
		
	def moveJoint(self, i):
		dir = i
		str_dir = ""
		if i == 0:
			str_dir = "forwards"
			dir = -1
		elif i == 1:
			str_dir = "backwards"
			dir = 1
		else:
			print("Error: moveJoint got unknown direction: "+str(i))
			return
		print("Moving selected joint :: "+str(self.currentJoint) + " "+str_dir)
		j = self.currentJoint
		this_hpr = self.J[j].getHpr(self.J[j])
		
		old_this_h = this_hpr[0]; new_this_h = old_this_h + dir*self.currentDegPerStep
		old_this_p = this_hpr[1]; new_this_p = old_this_p + dir*self.currentDegPerStep
		old_this_r = this_hpr[2]; new_this_r = old_this_r + dir*self.currentDegPerStep

		# FIGURE OUT WHICH ROTATIONS ACTUALLY MOVE JOINTS PROPERLY: 
		
		self.J[j].setR(self.J[j], new_this_r)
		
		#if j == 1:
		#	self.J[j].setR(self.J[j], new_this_r)
		#
		#if j == 2:
		#	self.J[j].setR(self.J[j], new_this_r)
		
		#if j >= 2:
		#	self.J[j].setH(self.J[j], new_this_h)
		#else:
		#	self.J[j].setH(new_this_h)
		#self.J[j].setP(new_this_p)
		#self.J[j].setR(new_this_r)
	
	def zeroJoints(self, i):
		print("Zero-ing joints.")
		for j in range(1, len(self.J)):
			self.J[j].setHpr(0,0,0)
 
 
	
 
	# Define a procedure to move the camera.
	def spinCameraTask(self, task):
		angleDegrees = task.time * 6.0
		angleRadians = angleDegrees * (pi / 180.0)
		self.camera.setPos(20 * sin(angleRadians), -20.0 * cos(angleRadians), 3)
		self.camera.setHpr(angleDegrees, 0, 0)
		return Task.cont
 
def walkJointHierarchy(actor, part, parentNode = None, indent = ""):
		if isinstance(part, CharacterJoint):
			np = actor.exposeJoint(None, 'modelRoot', part.getName())
			if parentNode and parentNode.getName() != "root":
				lines = LineSegs()
				lines.setThickness(3.0)
				lines.setColor(random(), random(), random())
				lines.moveTo(0, 0, 0)
				lines.drawTo(np.getPos(parentNode))
				lnp = parentNode.attachNewNode(lines.create())
				lnp.setBin("fixed", 40)
				lnp.setDepthWrite(False)
				lnp.setDepthTest(False)
			parentNode = np
		for child in part.getChildren():
			walkJointHierarchy(actor, child, parentNode, indent + "  ") 
 
app = MyApp()
app.run()