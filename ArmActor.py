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

# Import examples:
# from FirstPersonCamera import FirstPersonCamera
# from ArmActor import ArmActor
# arm = ArmActor(base, "models/arm7.egg")

class ArmActor(ShowBase):

	def __init__(self, gameApp, modelPathString):
	
		self.running = True
	
		self.gameApp = gameApp
	
		self.m = Actor(modelPathString) # "models/arm7.egg"
		#self.m.setScale(3, 3, 3)
		
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
		
		# "You can create collision geometry in a separate model and attach it to the various joints of your actor later via the exposeJoint() method. 
		# Collision geometry will always be rigid geometry--your actor will be like a tin man, not a cowardly lion." 
		
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
		self.gameApp.taskMgr.add(self.QWmoveTask, "QWmoveTask")

		
		self.accept('p', self.printJoints, [0])
		self.accept('0', self.zeroJoints, [0])
		
		# Debug joint hierarchy visually: 
		self.walkJointHierarchy(self.m, self.m.getPartBundle('modelRoot'), None)
		
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
			
	def walkJointHierarchy(self, actor, part, parentNode = None, indent = ""):
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
			self.walkJointHierarchy(actor, child, parentNode, indent + "  ") 
			
	## Call to start/stop control system 
	def toggle(self): 
		if(self.running): 
			print("\n --- Entering Manual Camera Mode. Press ENTER again to return to Robot Interface Mode. ---\n")
			self.running = False 
		else: 
			print("\n --- Returning to Robot Interface Mode. Press ENTER again to return to Manual Camera Mode. ---\n")
			self.running = True 