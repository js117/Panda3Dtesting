from pandac.PandaModules import * 
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence
from panda3d.core import Point3
from direct.showbase.InputStateGlobal import inputState



from random import random
import sys
from math import pi, sin, cos
from FirstPersonCamera import FirstPersonCamera
 
class MyApp(ShowBase):
	def __init__(self):
		ShowBase.__init__(self)
		
		self.running = True
		
		############################################### PHYSICS SETUP ####################################################
		# (don't know what I'm doing, just copied some lines from various physics tutorials) 
		base.enableParticles()
		
		node1 = NodePath("PhysicsNode")
		node1.reparentTo(self.render)
		an1 = ActorNode("robot-arm-physics")
		anp1 = node1.attachNewNode(an1)
		base.physicsMgr.attachPhysicalNode(an1)
		
		node2 = NodePath("PhysicsNode")
		node2.reparentTo(self.render)
		an2 = ActorNode("setting-physics")
		anp2 = node2.attachNewNode(an2)
		base.physicsMgr.attachPhysicalNode(an2)
		
		gravityFN=ForceNode('world-forces')
		gravityFNP=render.attachNewNode(gravityFN)
		gravityForce=LinearVectorForce(0,0,-9.81) #gravity acceleration
		gravityFN.addForce(gravityForce) 
		#base.physicsMgr.addLinearForce(gravityForce) # everything falls through floor
		
		############################################## /PHYSICS SETUP ####################################################
		
		self.disableMouse()
 
		# Load the environment model.
		self.scene = self.loader.loadModel("models/setting_test.egg")
		self.scene.reparentTo(anp2) # self.render
		# Apply scale and position transforms on the model.
		self.scene.setScale(5.25, 5.25, 5.25)
		self.scene.setPos(0, 0, 0)
		
		# Load the robot arm
		self.m = Actor("models/arm7.egg")
		self.m.setScale(3, 3, 3)
		# Physics: 
		#jetpackGuy = loader.loadModel("models/jetpack_guy")
		#jetpackGuy.reparentTo(anp)
		self.m.reparentTo(self.render) # self.render, anp1
		
		# Set initial camera
		self.camera.setPos(-9, 6, 6)
		self.camera.setHpr(-104, -27, -1)
		
		# Initialize the useful first person camera class for debugging, positioning, etc
		self.mouseLook = FirstPersonCamera(self, self.cam, self.render)		 

		
		print("------- Joints: ---------")
		print(self.m.listJoints())
		
		# From blender: 
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
		self.lastSelectedJoint = self.currentJoint
		
		self.currentDegPerStep = 1
		self.degPerStepChangeFactor = 1.1
		
		# Set up key input:
		# 1, 2, ..., 6 select the different robot arm joints, Q and W move them forwards/back
		self.accept('escape', sys.exit)
		self.accept('1', self.switchJoint, [1])
		self.accept('2', self.switchJoint, [2])
		self.accept('3', self.switchJoint, [3])
		self.accept('4', self.switchJoint, [4])
		self.accept('5', self.switchJoint, [5])
		self.accept('6', self.switchJoint, [6])
		
		self.accept('z', self.zeroJoints, [0])
		
		self.accept("enter", self.toggle) # to allow toggling between robot moving program and the first person WASD-camera 
		
		inputState.watchWithModifiers('qkey', 'q')
		inputState.watchWithModifiers('wkey', 'w')
		self.taskMgr.add(self.QWmoveTask, "QWmoveTask")

		
		self.accept('p', self.printJoints, [0])
		self.accept('0', self.zeroJoints, [0])
		
		# Debug joint hierarchy visually: 
		walkJointHierarchy(self.m, self.m.getPartBundle('modelRoot'), None)
		
	def QWmoveTask(self, task):
		if inputState.isSet('qkey') and self.running:
			self.moveJoint(0)
		if inputState.isSet('wkey') and self.running:
			self.moveJoint(1)
		return task.cont	
 
	def switchJoint(self, i):
		if self.running == False:
			print("Invalid command -- current in Manual Camera Mode. Press ENTER again to return to Robot Interface Mode.")
			return
		self.currentJoint = i
		self.lastSelectedJoint = self.currentJoint
		print("Current joint switched to :: "+str(i))

	# Acting as a general debug function 
	def printJoints(self, i):
		if self.running == False:
			print("Invalid command -- current in Manual Camera Mode. Press ENTER again to return to Robot Interface Mode.")
			return
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
		print("Current Jpos values ::: ")
		print(self.Jpos[1:])
		pos = self.camera.getPos(); ori = self.camera.getHpr()
		print(str(pos) + " / " + str(ori))
		
	def moveJoint(self, i):
		if self.running == False:
			print("Invalid command -- current in Manual Camera Mode. Press ENTER again to return to Robot Interface Mode.")
			return
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
		j = self.currentJoint
		this_hpr = self.J[j].getHpr(self.J[j])
		old_this_h = this_hpr[0]; new_this_h = old_this_h + dir*self.currentDegPerStep
		old_this_p = this_hpr[1]; new_this_p = old_this_p + dir*self.currentDegPerStep
		old_this_r = this_hpr[2]; new_this_r = old_this_r + dir*self.currentDegPerStep

		# FIGURE OUT WHICH ROTATIONS ACTUALLY MOVE JOINTS PROPERLY: 
		print("Moving selected joint :: "+str(self.currentJoint) + " "+str_dir)
		self.Jpos[j] += dir*self.currentDegPerStep
		self.J[j].setR(self.J[j], new_this_r)
		
	
	def zeroJoints(self, i):
		if self.running == False:
			print("Invalid command -- current in Manual Camera Mode. Press ENTER again to return to Robot Interface Mode.")
			return
		print("Zero-ing joints.")
		for j in range(1, len(self.J)):
			self.Jpos[j] = 0
		
 
	# Manual hack to adjust camera
	# Hack for setting initial camera pos; uses current joint for x/y/z/h/p/r
	def adjustCamera(self, i):
		dir = i
		if i == 0:
			dir = -1
		elif i == 1:
			dir = 1
		else:
			print("Error: moveJoint got unknown direction: "+str(i))
			return

		curr_pos = self.camera.getPos(); curr_hpr = self.camera.getHpr()
		j = self.currentJoint
		if j == 1:
			new_val = curr_pos[0] + dir*self.currentDegPerStep
			self.camera.setPos(new_val, curr_pos[1], curr_pos[2])
		if j == 2:
			new_val = curr_pos[1] + dir*self.currentDegPerStep
			self.camera.setPos(curr_pos[0], new_val, curr_pos[2])
		if j == 3:
			new_val = curr_pos[2] + dir*self.currentDegPerStep
			self.camera.setPos(curr_pos[0], curr_pos[1], new_val)
			
		if j == 4:
			new_val = curr_hpr[0] + dir*self.currentDegPerStep
			self.camera.setHpr(new_val, curr_hpr[1], curr_hpr[2])
		if j == 5:
			new_val = curr_hpr[1] + dir*self.currentDegPerStep
			self.camera.setHpr(curr_hpr[0], new_val, curr_hpr[2])
		if j == 6:
			new_val = curr_hpr[2] + dir*self.currentDegPerStep
			self.camera.setHpr(curr_hpr[0], curr_hpr[1], new_val)

		pos = self.camera.getPos(); ori = self.camera.getHpr()
		print(str(pos) + " / " + str(ori))
	
 
	# Define a procedure to move the camera.
	def spinCameraTask(self, task):
		#angleDegrees = task.time * 6.0
		#angleRadians = angleDegrees * (pi / 180.0)
		#self.camera.setPos(-8 * sin(angleRadians), 8 * cos(angleRadians), 6)
		#self.camera.setHpr(angleDegrees, 0, 0)
		pos = self.camera.getPos(); ori = self.camera.getHpr()
		print(str(pos) + " / " + str(ori))
		return task.cont
		
		
	## Call to start/stop control system 
	def toggle(self): 
		if(self.running): 
			print("\n --- Entering Manual Camera Mode. Press ENTER again to return to Robot Interface Mode. ---\n")
			self.running = False 
		else: 
			print("\n --- Returning to Robot Interface Mode. Press ENTER again to return to Manual Camera Mode. ---\n")
			self.running = True 	
 
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