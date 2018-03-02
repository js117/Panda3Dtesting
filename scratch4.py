# SOURCE: https://www.panda3d.org/forums/viewtopic.php?f=8&t=11938 

#http://www.ode.org/ode-latest-userguide.html#sec_6_3_0
#http://www.panda3d.org/manual/index.php/Collision_Detection_with_ODE
#http://pyode.sourceforge.net/tutorials/tutorial1.html
#http://www.panda3d.org/manual/index.php/Collision_Detection_with_ODE
#import __Header
#import PandaHeader
import direct.directbase.DirectStart

from pandac.PandaModules import Point3, DirectionalLight, VBase4, VBase3
from pandac.PandaModules import Filename
import random
import math
import time
from pandac.PandaModules import *
#from _CameraHandler import clCameraHandler
from direct.showbase.DirectObject import DirectObject
from direct.actor.Actor import Actor

from FirstPersonCamera import FirstPersonCamera
from ArmActor import ArmActor


  # // test if geom o1 and geom o2 can collide
  # cat1 = dGeomGetCategoryBits (o1);
  # cat2 = dGeomGetCategoryBits (o2);
  # col1 = dGeomGetCollideBits (o1);
  # col2 = dGeomGetCollideBits (o2);
  # if ((cat1 & col2) || (cat2 & col1)) {
	# // call the callback with o1 and o2
  # }
  # else {
	# // do nothing, o1 and o2 do not collide
# }

def MakeWall(size, vb4Color = VBase4( .6, .6, .6, 1)):
   temp = CardMaker('')
   temp.setFrame(-size, size, -size, size)
   npSquare = NodePath( temp.generate() )
   npSquare.setColor( vb4Color )
   npSquare.setTwoSided(True)
   return npSquare


class clSim(DirectObject):
   booDebugDrawMouseLine = False
   booTimeit = False
   def __init__(self, objCamera = None):
	  world = OdeWorld()
	  world.setGravity( 0, 0, -10.0)
#	  world.setErp(0.8)
#	  world.setCfm(1E-5)
	  world.initSurfaceTable(1)
	  world.setSurfaceEntry(0, 0, 150, 0.0, 9.1, 0.9, 0.00001, 0.0, 0.002)

	  space = OdeQuadTreeSpace( Point3(0,0,0), VBase3( 200, 200, 200), 7 )
	  space.setAutoCollideWorld(world)
	  contactgroupWorld = OdeJointGroup()
	  space.setAutoCollideJointGroup( contactgroupWorld )
	  
	  self.world = world
	  self.space = space
	  self.spacegeom = OdeUtil.spaceToGeom( self.space )
	  self.contactgroupWorld = contactgroupWorld

	  self.dictStaticObjects = {}
	  self.tlist = []
	  self.dictDynamicObjects = {}
	  self.raygeomMouse = OdeRayGeom( 10 )
	  self.idMouseRayGeom = self.raygeomMouse.getId().this
	  
	  self.InitBoxPrototype()
	  
	  self.objCamera = objCamera
	  self.npCamera = base.cam if objCamera == None else objCamera.GetNpCamera()
	  self.EnableMouseHit()
	  taskMgr.add( self.taskSimulation, 'taskSimulation')
	  
   def AddStaticTriMeshObject(self, npObj, strName = '', bitMaskCategory = BitMask32(0x0), bitMaskCollideWith = BitMask32(0x0)):
	  trimeshData = OdeTriMeshData( npObj, True )
	  trimeshGeom = OdeTriMeshGeom( self.space, trimeshData )
	  trimeshGeom.setCollideBits( bitMaskCollideWith )
	  trimeshGeom.setCategoryBits( bitMaskCategory )
	  
	  trimeshGeom.setPosition( npObj.getPos() )
	  trimeshGeom.setQuaternion( npObj.getQuat() )
	  
	  id = trimeshGeom.getId().this
	  self.dictStaticObjects[ id ] = ( strName, trimeshGeom )
	  
   def EnableMouseHit(self):
	  self.accept('mouse1', self.OnMouseBut1 )
	  
   def DisableMouseHit(self):
	  self.ignore('mouse1')
	  
   def InitBoxPrototype(self):
	  npBox = loader.loadModel("box")
	  #Center the box. it starts out 0 <= x,y,z <=1
	  npBox.setPos(-.5, -.5, -.5)
	  npBox.flattenLight() # Apply transform
	  npBox.setTextureOff()
	  self.npBox = npBox
	  
   def RefreshMousePointerRayGeom(self):
	  pt3CamNear = Point3( 0,0,0)
	  pt3CamFar = Point3(0,0,0)
	  pt2Mpos = base.mouseWatcherNode.getMouse()
	  self.npCamera.node().getLens().extrude( pt2Mpos, pt3CamNear, pt3CamFar)
	  
	  pt3CamNear = render.getRelativePoint( self.npCamera, pt3CamNear )
	  pt3CamFar = render.getRelativePoint( self.npCamera, pt3CamFar )
	  
	  if self.booDebugDrawMouseLine:
		 npLine = CreateConnectedLine( [pt3CamNear, pt3CamFar] )
		 npLine.reparentTo( render )
	  
	  pt3Dir = pt3CamFar - pt3CamNear
	  fLength = pt3Dir.length()
	  self.raygeomMouse.setLength( fLength )
	  self.raygeomMouse.set( pt3CamNear, pt3Dir/fLength )

   def OnMouseBut1(self):
	  self.RefreshMousePointerRayGeom()
	  
	  OdeUtil.collide2( self.raygeomMouse, self.spacegeom, '33', self.CollideNear_Callback )
	  if self.tlist != []:
		 self.tlist.sort()
		 print 'Mouse hit', time.time()
		 self.PrintObject( self.tlist[0][1].getG1().getId().this )
		 self.PrintObject( self.tlist[0][1].getG2().getId().this )
		 self.tlist = []
   
   def PrintObject(self, id):
	  if id != self.idMouseRayGeom:
		 if id in self.dictStaticObjects:
			print self.dictStaticObjects[ id ]
		 elif id in self.dictDynamicObjects:
			print self.dictDynamicObjects[ id ]
		 else:
			print 'id', id, 'not recognized!'

   def CollideNear_Callback(self, data, geom1, geom2):
	  contactGroup = OdeUtil.collide( geom1, geom2 )
	  if contactGroup.getNumContacts() != 0:
		 tupDistContact = self.FindNearestContactFromGroup( contactGroup )
		 self.tlist.append( tupDistContact )

   def FindNearestContactFromGroup(self, contactGroup):
	  camPos = self.npCamera.getPos()
	  tlist = [ ((contactGroup[i].getPos() - camPos).length(), contactGroup[i]) for i in xrange(contactGroup.getNumContacts()) ]
	  tlist.sort()
	  return tlist[0]
   
   def taskSimulation(self, task):
	  if self.booTimeit:
		 fStarttime = time.clock()
	  self.space.autoCollide() # Setup the contact joints
	  # Step the simulation and set the new positions
	  self.world.quickStep(globalClock.getDt())
	  for id in self.dictDynamicObjects:
		 np = self.dictDynamicObjects[id][3]
		 body = self.dictDynamicObjects[id][2]
		 np.setPosQuat(render, body.getPosition(), Quat(body.getQuaternion()))
	  self.contactgroupWorld.empty() # Clear the contact joints
	  if self.booTimeit:
		 print time.clock() - fStarttime
	  return task.cont

   def AddBox(self, strId = '', pt3Pos = Point3(0, 0, 20), vb4Color = VBase4( 1, 1, 1, 1) ):
	  newbox = self.npBox.copyTo( render ) # npBox: from loadModel() 
	  #newbox.setColor( vb4Color )
	  newbox.setPos( pt3Pos )
	  
	  M = OdeMass()
	  M.setBox(20, 1, 1, 1)
	  
	  boxBody = OdeBody( self.world )
	  boxBody.setMass(M)
	  boxBody.setPosition( newbox.getPos() )
	  boxBody.setQuaternion( newbox.getQuat() )
	  
	  boxGeom = OdeBoxGeom( self.space, 1, 1, 1 )
	  boxGeom.setCollideBits( BitMask32( 3 ) )
	  boxGeom.setCategoryBits( BitMask32( 2 ) )
	  
	  ## Links the transformation matrices of the space and the world together.
	  boxGeom.setBody( boxBody )
	  
	  self.dictDynamicObjects[ boxGeom.getId().this ] = ( strId, boxGeom, boxBody, newbox )

	  
   # Added by JS 
   def AddDynamicTriMeshObject(self, npObj, strName = '', bitMaskCategory = BitMask32(0x0), bitMaskCollideWith = BitMask32(0x0)):
	  npObj.reparentTo( render )
	  trimeshData = OdeTriMeshData( npObj, True )
	  
	  trimeshBody = OdeBody( self.world ) 
	  trimeshBody.setPosition( npObj.getPos() )
	  trimeshBody.setQuaternion( npObj.getQuat() )
	  
	  trimeshGeom = OdeTriMeshGeom( self.space, trimeshData )
	  trimeshGeom.setCollideBits( bitMaskCollideWith )
	  trimeshGeom.setCategoryBits( bitMaskCategory )

	  ## Links the transformation matrices of the space and the world together.
	  trimeshGeom.setBody( trimeshBody )
	  
	  id = trimeshGeom.getId().this
	  print("trimeshGeom Id: "+str(id))
	  self.dictDynamicObjects[ trimeshGeom.getId().this ] = ( strName, trimeshGeom, trimeshBody, npObj )

	  
	  print("AddDynamicTriMeshObject function successful")

scale = 20
#objCamera = clCameraHandler( pt3CameraPos = Point3(0, -scale*4, scale*4 ), tupNearFar = (0.05, scale*20 ) )
objCamera = None
base.cam.setPos( Point3(0, -scale*2, scale*2 ) )
base.cam.lookAt( Point3(0, 0, 0 ) )

ground = MakeWall( scale )
left = MakeWall( scale, vb4Color = VBase4( .6, 0, 0, 1) )
right = MakeWall( scale, vb4Color = VBase4( .6, 0, 0, 1) )
front = MakeWall( scale, vb4Color = VBase4( 0, 0.6, 0, 1) )
#back = MakeWall( scale, vb4Color = VBase4( 0, 0, 0.6, .2) )

for i in [ground, left, right, front]:
   i.reparentTo( render )

ground.setHpr( 0, -90, 0)
right.setPos( scale, 0, scale )
right.setHpr( 90, 0, 0 )
left.setPos( -scale, 0, scale)
left.setHpr( 90, 0, 0 )
front.setPos( 0, scale, scale )
#back.setPos( 0, -scale, scale )
#back.setTransparency( True )


global nBoxes
global objSim
global nStartTime

# Look at AddBox function for hints ? 
#arm = Actor("models/arm7.egg")

arm = ArmActor(base, "models/arm7.egg")
#arm.m.setScale(6,6,6)
#arm.m.copyTo( render )

mouseLook = FirstPersonCamera(base, base.cam, render)

#arm.setScale(10, 10, 10)
#arm.setPos(5,-5,0)
#arm.reparentTo(render)

objSim = clSim( objCamera )
objSim.AddStaticTriMeshObject( ground, 'ground', bitMaskCategory = BitMask32( 1 ), bitMaskCollideWith = BitMask32( 2 ) )
objSim.AddStaticTriMeshObject( left, 'left', bitMaskCategory = BitMask32( 1 ), bitMaskCollideWith = BitMask32( 2 ) )
objSim.AddStaticTriMeshObject( right, 'right', bitMaskCategory = BitMask32( 1 ), bitMaskCollideWith = BitMask32( 2 ) )
objSim.AddStaticTriMeshObject( front, 'front', bitMaskCategory = BitMask32( 1 ), bitMaskCollideWith = BitMask32( 2 ) )

objSim.AddDynamicTriMeshObject( arm.m, 'arm', bitMaskCategory = BitMask32( 2 ), bitMaskCollideWith = BitMask32( 3 ) ) 

#objSim.AddTriMesh( arm.m, 'arm' ) #  bitMaskCategory = BitMask32( 2 ), bitMaskCollideWith = BitMask32( 3 )

#objSim.AddBox( strId = 'red', vb4Color = (0, 0.6, 0, 1) )
nBoxes = 0
nStartTime = int(time.time() + 1)


def taskAddBall(task):
   global nBoxes
   global objSim
   global nStartTime
   if nBoxes < 50:
	  if ((time.time() - nStartTime) > 1):
		 objSim.AddBox( strId = str( 'box '+ str( nBoxes )) , vb4Color = ( 1.*nBoxes/50, 0.6 ,0, 1) )
		 nBoxes += 1
		 nStartTime = time.time()
	  return task.cont
   return task.done

taskMgr.add( taskAddBall, 'addball' )

run()