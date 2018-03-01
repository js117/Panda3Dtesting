import direct.directbase.DirectStart
from direct.actor.Actor import Actor
from pandac.PandaModules import *
import random
from panda3d.core import *

class RalphWorld:
	def __init__(self):
		# Initialize ODE stuff
		self.world = OdeWorld()
		self.space = OdeSimpleSpace()
		self.contactgroup = OdeJointGroup()
	
		self.FPS = 90.0
		self.DTAStep = 1.0 / self.FPS

		self.world.setAutoDisableFlag(0)
		self.world.setAutoDisableLinearThreshold(0.15)
		self.world.setAutoDisableAngularThreshold(0.15)
		self.world.setAutoDisableSteps(2)
		self.world.setGravity(0,0,-9.81)
		self.world.initSurfaceTable(1)
		self.world.setSurfaceEntry(0,0, 150, 0.0, 9.1, 0.9, 0.00001, 0.0, 0.002)

		self.space.setAutoCollideWorld(self.world)
		self.space.setAutoCollideJointGroup(self.contactgroup)
		self.world.setQuickStepNumIterations(8)
		self.DTA = 0.0

		# Create a plane for Ralph to fall onto.
		self.floor = OdePlaneGeom(self.space, Vec4(0.0, 0.0, 1.0, 0.0))
		self.floor.setCollideBits(BitMask32(0x00000001))
		self.floor.setCategoryBits(BitMask32(0x00000002))

		# Now set up Ralph.
		self.ralph = Actor('models/arm7.egg')
		self.ralph.reparentTo(render)

		# Put him up in the air.  Ralph's due for a fall.
		self.ralph.setPos(0, 0, 20)
		#self.ralph.setHpr(random.uniform(0, 360), random.uniform(-90, 90), random.uniform(0, 180))

		# If any part of Ralph is visible, draw all of him.  This is
		# necessary because we might be animating some of his joints
		# outside of his original bounding volume.
		self.ralph.node().setFinal(1)

		# Set up the joints as OdeBody objects.
		self.joints = []
		self.setupRagdoll(self.ralph)

		# Set the camera back a bit.
		base.trackball.node().setPos(0, 50, -10)

		# Start the simulation running, after a brief pause.
		taskMgr.doMethodLater(3, self.__simulationTask, "simulation task")
		
		print("init ran")

	def __walkJointHierarchy(self, actor, part, parentNode, parentBody):
		if isinstance(part, CharacterJoint):

			# Create a node that we can control to animate the
			# corresponding joint.  Make sure it is a child of the
			# parent joint's node.
			np = parentNode.attachNewNode(part.getName())
			actor.controlJoint(np, 'modelRoot', part.getName())

			# Ensure the node's original transform is the same as the
			# joint's original transform.
			#np.setMat(part.getInitialValue())

			# Create an OdeBody object to apply physics to that node.
			body = self.__makeJointBody(np)

			# Create an OdeUniversalJoint to connect this node to its parent.
			bj = OdeUniversalJoint(self.world)
			bj.attachBodies(parentBody, body)
			bj.setAnchor(np.getPos(render))

			parentNode = np
			parentBody = body
			
		for i in range(part.getNumChildren()):
			self.__walkJointHierarchy(actor, part.getChild(i), parentNode, parentBody)

	def __makeJointBody(self, np):
		density = 1
		radius = 1

		body = OdeBody(self.world)
		M = OdeMass()
		M.setSphere(density, radius)
		body.setMass(M)
		body.setPosition(np.getPos(render))
		body.setQuaternion(np.getQuat(render))

		geom = OdeSphereGeom(self.space, radius)
		geom.setCollideBits(BitMask32(0x00000002))
		geom.setCategoryBits(BitMask32(0x00000001))
		geom.setBody(body)

		self.joints.append((np, body))

		return body

	def setupRagdoll(self, actor):
		""" Recursively create a hierarchy of NodePaths, parented to
		the actor, matching the hierarchy of joints.  Each NodePath
		can be used to control its corresponding joint (as in
		actor.controlJoint()). """
		
		bundle = actor.getPartBundle('modelRoot')
		# A body for the overall actor.
		body = self.__makeJointBody(actor)
		self.__walkJointHierarchy(actor, bundle, actor, body)
		
		print("setupRagdoll end of function")
		
	def __simulationTask(self, task):
		# Run the appropriate number of ODE steps according to the
		# elapsed time since the last time this task was run.
		self.DTA += globalClock.getDt()
		while self.DTA >= self.DTAStep:
			self.DTA -= self.DTAStep
			self.__simulateStep()

		# Apply ODE transforms to the Panda joints.
		for np, body in self.joints:
			pos = body.getPosition()
			# body.getQuaternion() should return a Quat, but it
			# returns a VBase4 instead.  A nuisance.
			quat = Quat(body.getQuaternion())
			
			np.setPosQuat(render, pos, quat)

		return task.cont
		
	def __simulateStep(self):
		self.space.autoCollide() # Detect collisions and create contact joints
		self.world.quickStep(self.DTAStep) # Simulate
		
		self.contactgroup.empty() # Remove all contact joints

rw = RalphWorld()
run()