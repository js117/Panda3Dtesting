# Original Header
# Author: Ryan Myers
# Models: Jeff Styers, Reagan Heller

#improvement : Philippe Cain

# Last Updated: 17/08/2015
#
# This snippets provides an example of :
#   -creating a character
#   -walk around on uneven terrain,
#   -The camera follows the character
#   -The camera displays the objects name when the cursor is "above" an 3D object
#    the name is dsplayed
#   -The player can select the object by clicking with the mouse

### Ralph improvements : modifications by v
# This is a modification of the roaming ralph demo to provide improved controls
# and camera angles, imitating those of modern commercial games as "skyrim" game play.
# The code has been reorganised  in order to well identified all the parameters and
# teh functions.

from direct.showbase.ShowBase import ShowBase

from panda3d.core import WindowProperties
from panda3d.core import CollisionTraverser,CollisionNode
from panda3d.core import CollisionHandlerQueue,CollisionRay
from panda3d.core import CollisionTube,CollisionSegment,CollisionSphere
from panda3d.core import Filename,AmbientLight,DirectionalLight
from panda3d.core import PandaNode,NodePath,Camera,TextNode
from panda3d.core import Point3,Vec3,Vec4,BitMask32
from panda3d.core import LightRampAttrib
from direct.gui.OnscreenText import OnscreenText
from direct.actor.Actor import Actor
import random, sys, os, math


# Function to put instructions on the screen.
def addInstructions(pos, msg):
    return OnscreenText(text=msg, style=1, fg=(1,1,1,1),
                        pos=(-1.3, pos), align=TextNode.ALeft, scale = .05)

# Function to put title on the screen.
def addTitle(text):
    return OnscreenText(text=text, style=1, fg=(1,1,1,1),
                        pos=(1.3,-0.95), align=TextNode.ARight, scale = .07)
class World(ShowBase):

    def __init__(self):
        ShowBase.__init__(self,fStartDirect=False, windowType=None )

        #post instrucions
        self.title = addTitle("Panda3D Tutorial: Ralph improvements")
        self.inst1 = addInstructions(0.95, "[ESC]: Quit")
        self.inst2 = addInstructions(0.90, "arrows keys move Ralph forward, left, back, and right, respectively.")
        self.inst3 = addInstructions(0.85, "Use the mouse to look around and steer Ralph.")
        self.inst4 = addInstructions(0.80, "Zoom in and out using the mouse wheel, or page up and page down keys.")
        self.inst4 = addInstructions(0.75, "Click with the mouse on object to select it.")
        self.text1 = OnscreenText()

        #prepare the window
        self.oWindowProperties = WindowProperties()
        self.oW = 800
        self.oH = 600
        self.oWindowProperties.setSize(self.oW, self.oH)

        #load the world
        self.environ = loader.loadModel("models/world")
        self.environ.reparentTo(render)
        self.environ.setPos(0,0,0)

        #load teapot with a collision sphere
        self.teapot = loader.loadModel("models/teapot")
        self.teapot.reparentTo(render)
        self.teapot.setScale(0.2)
        self.teapot.setPos(10,0,3)
        self.teapot.setTag('object_pickable', 'teapot')

        cs = CollisionSphere(0, 0, 0, 3)
        cnodePath = self.teapot.attachNewNode(CollisionNode('cnode'))
        cnodePath.node().addSolid(cs)
        #cnodePath.show()

        # Create the main character, Ralph
        self.ralph = Actor("models/ralph",  {"run":"models/ralph-run", "walk":"models/ralph-walk"})
        self.ralph.reparentTo(render)
        self.ralph.setScale(0.2)
        self.ralph.setPos(0,0,0)

        # create the cursor in the center of the screen
        OnscreenText(text="||", style=1, fg=(1,1,1,1),pos=(0.0,0.03) , align=TextNode.ARight, scale = .07)
        OnscreenText(text="||", style=1, fg=(1,1,1,1),pos=(0.0,-0.05), align=TextNode.ARight, scale = .07)
        OnscreenText(text="==", style=1, fg=(1,1,1,1),pos=(-0.03,0.0), align=TextNode.ARight, scale = .07)
        OnscreenText(text="==", style=1, fg=(1,1,1,1),pos=(0.055,0.0), align=TextNode.ARight, scale = .07)

       # Accept the control keys for movement and rotation
        self.accept("escape", self.mExit)
        self.accept("arrow_up", self.mGetUserActions, ["forward",True,True])
        self.accept("arrow_left", self.mGetUserActions, ["left",True,True])
        self.accept("arrow_down", self.mGetUserActions, ["backward",True,True])
        self.accept("arrow_right", self.mGetUserActions, ["right",True,True])
        self.accept("arrow_up-up", self.mGetUserActions, ["forward",False,False])
        self.accept("arrow_left-up", self.mGetUserActions, ["left",False,False])
        self.accept("arrow_down-up", self.mGetUserActions, ["backward",False,False])
        self.accept("arrow_right-up", self.mGetUserActions, ["right",False,False])
        self.accept("wheel_up", self.mGetUserActions, ["wheel-in", True])
        self.accept("wheel_down", self.mGetUserActions, ["wheel-out", True])
        self.accept("mouse1", self.mGetUserActions, ["mouse1", True])
        self.accept("mouse1-up", self.mGetUserActions, ["mouse1", False])

        # set the camera and player and collision
        self.mSetUpMoveCameraPlayer(base.camera,self.ralph,'cam','ralph')
        self.mSetUpCollision()
        self.mSetUpCollisionClick3DObject()

        # put in place the 2 main tasks
        taskMgr.add(self.mMove,"moveTask")
        taskMgr.add(self.mClick,"clickObject")

    def mClick(self,task):
        # First we check that the mouse is not outside the screen.
        if base.mouseWatcherNode.hasMouse():

            # This gives up the screen coordinates of the mouse.
            mpos = base.mouseWatcherNode.getMouse()

            # This makes the ray's origin the camera and makes the ray point
            # to the screen coordinates of the mouse.
            self.pickerRay.setFromLens(self.camNode, mpos.getX(), mpos.getY())
            self.picker.traverse(render)
            # Assume for simplicity's sake that myHandler is a CollisionHandlerQueue.
            if self.pq.getNumEntries() > 0 :
                # This is so we get the closest object
                self.pq.sortEntries()
                pickedObj = self.pq.getEntry(0).getIntoNodePath()

                if (self.controlMap["mouse1"] and pickedObj.getDistance(self.oPlayerToMove) < self.minDistanceObjectPickable):
                    self.text1.cleanup()
                    sPickedObj = pickedObj.findNetTag('object_pickable').getTag('object_pickable')
                    if sPickedObj:
                        self.text1 = OnscreenText(text= "-" + sPickedObj  + "-", style=1, fg=(1,1,1,1), bg=(0,0,0,1),pos=(0,0) , align=TextNode.ALeft, scale = .05)
                    else:
                        self.text1 = OnscreenText(text=str(pickedObj) + " picked", style=1, fg=(1,1,1,1),pos=(-1,0.5) , align=TextNode.ALeft, scale = .05)
                else:
                    self.text1.cleanup()
                    self.text1 = OnscreenText(text= str(pickedObj) + " not picked", style=1, fg=(1,1,1,1),pos=(-1,0.5) , align=TextNode.ALeft, scale = .05)

        return task.cont

    def mExit(self):
        #remove the tasks to exit properly
        taskMgr.remove("moveTask")

        self.destroy()

        #stop debuging properly
        sys.exit(0)

    def mGetUserActions(self, key, bStatu , bMove = None):
        self.controlMap[key]    = bStatu
        if bMove <> None:
            self.controlMap["move"] = bMove

    def mMove(self, task):

        # save player's initial position so that we can restore it,
        # in case he falls off the map or runs into something.
        self.oNodeToMovePreviousPosition = self.oNodeToMove.getPos()

        self.mMoveCamera()
        self.mMovePlayer()
        self.mPlayerAnimation()
        self.mPlayerCollision()

        return task.cont

    def mMovePlayer(self):

        # If a move-key is pressed, move player in the specified direction.
        if (self.controlMap["forward"]):
            self.sNewDirection ="forward"
            self.oNodeToMove.setY(self.oNodeToMove, self.forwMovePlayer * globalClock.getDt())
        elif (self.controlMap["backward"]):
            self.sNewDirection ="backward"
            self.oNodeToMove.setY(self.oNodeToMove, self.backMovePlayer * globalClock.getDt())
        elif (self.controlMap["left"]):
            self.sNewDirection ="left"
            self.oNodeToMove.setX(self.oNodeToMove, self.leftMovePlayer * globalClock.getDt())
        elif (self.controlMap["right"]):
            self.sNewDirection ="right"
            self.oNodeToMove.setX(self.oNodeToMove, self.righMovePlayer * globalClock.getDt())
        else:
            return True

        #when the direction change the player will face the new direction
        if self.sOldDirection <> self.sNewDirection:
            self.sOldDirection = self.sNewDirection
            if self.sNewDirection == "forward":
                self.oPlayerToMove.setH(self.oNodeToMove, 0)
            if self.sNewDirection == "backward":
                self.oPlayerToMove.setH(self.oNodeToMove, 180)
            if self.sNewDirection == "left":
                self.oPlayerToMove.setH(self.oNodeToMove, 90)
            if self.sNewDirection == "right":
                self.oPlayerToMove.setH(self.oNodeToMove, -90)

        return True

    def mMoveCamera(self):
        # If a zoom button is used, zoom in or out
        if (self.controlMap["wheel-in"]):
            self.cameraDistance -= self.speedZoom * self.cameraDistance;
            if (self.cameraDistance < self.minDistCameraPlayer):
                self.cameraDistance = self.minDistCameraPlayer
            self.controlMap["wheel-in"] = False

        elif (self.controlMap["wheel-out"]):
            self.cameraDistance += self.speedZoom * self.cameraDistance;
            if (self.cameraDistance > self.maxDistCameraPlayer):
                self.cameraDistance = self.maxDistCameraPlayer
            self.controlMap["wheel-out"] = False

        # Use mouse input to turn both Player and the Camera
        # The mouse is in the center of the screen
        if base.mouseWatcherNode.hasMouse():
            # get changes in mouse position
            md      = base.win.getPointer(0)
            deltaX  = md.getX() - self.oW / 2
            deltaY  = md.getY() - self.oH / 2

            # reset mouse cursor position in order to compare it and identify the move
            base.win.movePointer(0, self.oW / 2 , self.oH / 2)

            # alter player's yaw by an amount proportionate to deltaX
            if self.controlMap["move"]:
                if self.move == False:
                    self.move = True
                    self.oPlayerToMove.detachNode()
                    self.oPlayerToMove.reparentTo(self.oNodeToMove)
                    self.oPlayerToMove.setPos(self.oNodeToMove,self.oDistancePlayerCursor,0,0)
                    self.oPlayerToMove.setH(0)
            else:
                if self.move == True:
                    self.move = False
                    self.oPlayerToMove.detachNode()
                    self.oPlayerToMove.reparentTo(render)
                    self.oPlayerToMove.setPos(self.oNodeToMove,self.oDistancePlayerCursor,0,0)
                    self.oPlayerToMove.setH(self.oNodeToMove.getH())

            self.oNodeToMove.setH(self.oNodeToMove.getH() - self.speedSetHPlayer * deltaX)


            # find the new camera pitch and clamp it to a reasonable range
            self.cameraPitch = self.cameraPitch + self.speedPitchCamera * deltaY
            if (self.cameraPitch < self.minPicthCamera):
                self.cameraPitch = self.minPicthCamera
            if (self.cameraPitch >  self.maxPicthCamera):
                self.cameraPitch =  self.maxPicthCamera
            self.oCameraToMove.setHpr(0,self.cameraPitch,0)

            # set the camera at around player's middle
            # We should pivot around here instead of the view target which is noticebly higher
            self.oCameraToMove.setPos(0,0,self.cameraTargetHeight * self.reduceHeightCamera)
            # back the camera out to its proper distance
            self.oCameraToMove.setY(self.oCameraToMove,self.cameraDistance)
        # point the camera at the view target
        viewTarget = Point3(0,0,self.cameraTargetHeight)
        self.oCameraToMove.lookAt(viewTarget)

        return True


    def mPlayerAnimation(self):
        # If player is moving, loop the run animation.
        # If he is standing still, stop the animation.

        if (self.controlMap["forward"]) or (self.controlMap["left"]) or (self.controlMap["right"]) or (self.controlMap["backward"]):
            if self.isPlayerMoving is False:
                self.oPlayerToMove.loop("run")
                self.isPlayerMoving = True
        else:
            if self.isPlayerMoving:
                self.oPlayerToMove.stop()
                self.oPlayerToMove.pose("walk",5)
                self.isPlayerMoving = False

        return True

    def mPlayerCollision(self):

        viewTarget = Point3(0,0,self.cameraTargetHeight)
        # reposition the end of the  camera's obstruction ray trace
        self.cameraRay.setPointB(self.oCameraToMove.getPos())
        # Now check for collisions.

        self.cTrav.traverse(render)

        # Adjust player's Z coordinate.  If player's ray hit terrain,
        # update his Z. If it hit anything else, or didn't hit anything, put
        # him back where he was last frame.

        entries = []
        for i in range(self.oPlayerToMoveGroundHandler.getNumEntries()):
            entry = self.oPlayerToMoveGroundHandler.getEntry(i)
            entries.append(entry)

        entries.sort(lambda x,y: cmp(y.getSurfacePoint(render).getZ(),
                                     x.getSurfacePoint(render).getZ()))
        if (len(entries)>0) and (entries[0].getIntoNode().getName() == "terrain"):
            self.oNodeToMove.setZ(entries[0].getSurfacePoint(render).getZ())
        else:
            self.oNodeToMove.setPos(self.oNodeToMovePreviousPosition)

        # We will detect anything obstructing the camera via a ray trace
        # from the view target around the avatar's head, to the desired camera
        # position. If the ray intersects anything, we move the camera to the
        # the first intersection point, This brings the camera in between its
        # ideal position, and any present obstructions.

        entries = []
        for i in range(self.cameraColHandler.getNumEntries()):
            entry = self.cameraColHandler.getEntry(i)
            entries.append(entry)
        entries.sort(lambda x,y: cmp(-y.getSurfacePoint(self.oNodeToMove).getY(),
                                     -x.getSurfacePoint(self.oNodeToMove).getY()))
        if (len(entries)>0):
            collisionPoint =  entries[0].getSurfacePoint(self.oNodeToMove)
            collisionVec = ( viewTarget - collisionPoint)
            if ( collisionVec.lengthSquared() < self.cameraDistance * self.cameraDistance ):
                self.oCameraToMove.setPos(collisionPoint)
                if (entries[0].getIntoNode().getName() == "terrain"):
                    self.oCameraToMove.setZ(self.oCameraToMove, 0.2)
                self.oCameraToMove.setY(self.oCameraToMove, 0.3)

        return True

    def mSetUpCollisionClick3DObject(self):

        # Since we are using collision detection to do picking, we set it up like
        # any other collision detection system with a traverser and a handler
        self.picker = CollisionTraverser()  # Make a traverser
        self.pq = CollisionHandlerQueue()  # Make a handler
        # Make a collision node for our picker ray
        self.pickerNode = CollisionNode('mouseRay')
        # Attach that node to the camera since the ray will need to be positioned
        # relative to it
        self.pickerNP = self.oCameraToMove.attachNewNode(self.pickerNode)

        # Everything to be picked will use bit 1. This way if we were doing other
        # collision we could seperate it
        self.pickerNode.setFromCollideMask(BitMask32.bit(1))
        self.pickerRay = CollisionRay()  # Make our ray
        # Add it to the collision node
        self.pickerNode.addSolid(self.pickerRay)
        # Register the ray as something that can cause collisions
        self.picker.addCollider(self.pickerNP, self.pq)
        #self.picker.showCollisions(render)

    def mSetUpCollision(self):

        #minimum dictance between the player and the object
        self.minDistanceObjectPickable = 30

        # We will detect the height of the terrain by creating a collision
        # ray and casting it downward toward the terrain.  One ray will
        # start above ralph's head.
        # A ray may hit the terrain, or it may hit a rock or a tree.  If it
        # hits the terrain, we can detect the height.  If it hits anything
        # else, we rule that the move is illegal.

        self.cTrav                  = CollisionTraverser()

        self.oPlayerToMoveGroundRay = CollisionRay()
        self.oPlayerToMoveGroundRay.setOrigin(0,0,1000)
        self.oPlayerToMoveGroundRay.setDirection(0,0,-1)
        self.oPlayerToMoveGroundCol = CollisionNode(self.sPlayerNameToMove)
        self.oPlayerToMoveGroundCol.addSolid(self.oPlayerToMoveGroundRay)
        self.oPlayerToMoveGroundCol.setFromCollideMask(BitMask32.bit(0))
        self.oPlayerToMoveGroundCol.setIntoCollideMask(BitMask32.allOff())
        self.oPlayerToMoveGroundColNp = self.oPlayerToMove.attachNewNode(self.oPlayerToMoveGroundCol)
        self.oPlayerToMoveGroundHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.oPlayerToMoveGroundColNp, self.oPlayerToMoveGroundHandler)

        # We will detect anything obstructing the camera's view of the player
        self.cameraRay = CollisionSegment((0,0,self.cameraTargetHeight),(0,5,5))
        self.cameraCol = CollisionNode(self.sCameraNameToMove)
        self.cameraCol.addSolid(self.cameraRay)
        self.cameraCol.setFromCollideMask(BitMask32.bit(0))
        self.cameraCol.setIntoCollideMask(BitMask32.allOff())
        self.cameraColNp = self.oNodeToMove.attachNewNode(self.cameraCol)
        self.cameraColHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.cameraColNp, self.cameraColHandler)

        # Uncomment this line to see the collision rays
        #self.oPlayerToMoveGroundColNp.show()
        #self.cameraColNp.show()
        # Uncomment this line to show a visual representation of the
        # collisions occuring
        #self.cTrav.showCollisions(render)

    def mSetUpMoveCameraPlayer(self,oCamera,oPlayer,sCameraName,sPlayerName):
        """
        Setup the parameters to move the player and the camera in a consistent way
        """
        self.move = False
        self.oCameraToMove      = oCamera
        #the node to move is used to move the camera and the player in the game
        self.oNodeToMove        = NodePath("oNodeToMove")
        self.oNodeToMove.reparentTo(render)
        self.oNodeToMove.setPos(0,0,0)

        # the player to move is used to manage the animation of the player
        self.oPlayerToMove      = oPlayer
        self.oPlayerToMove.reparentTo(self.oNodeToMove)
        self.oDiameterPlayer     = int(self.oPlayerToMove.getBounds().getRadius() * 2 )

        #the player is put on the left side in order to let free the center of the screen
        #0.5
        self.oDistancePlayerCursor  = self.oDiameterPlayer / 3.0
        self.oPlayerToMove.setPos(self.oNodeToMove,self.oDistancePlayerCursor,0,0)

        self.sPlayerNameToMove  = sPlayerName
        self.sCameraNameToMove  = sCameraName
        self.isPlayerMoving     = False

        #define player direction and camera zoom
        self.controlMap = {"left":False, "right":False, "forward":False, "backward":False,
            "wheel-in":False, "wheel-out":False , "mouse1":False, "move":False}
        self.sOldDirection      = "forward"
        self.sNewDirection      = "forward"

        # Adding the camera to player is a simple way to keep the camera locked
        # in behind player regardless of player's movement.
        self.oCameraToMove.reparentTo(self.oNodeToMove)

        # We don't actually want to point the camera at player's feet.
        # This value will serve as a vertical offset so we can look over player

        self.cameraTargetHeight = self.oDiameterPlayer



        # How far should the camera be from player
        self.cameraDistance     = 10

        # Initialize the pitch of the camera
        self.cameraPitch        = 10

        #initialise for the player the distance to move in pixel during one frame.
        self.forwMovePlayer     = -10
        self.backMovePlayer     = 10
        self.righMovePlayer     = -10
        self.leftMovePlayer     = 10

        #initialse the minimum and maximum distance between the camera and player
        #self.minDistCameraPlayer= 0.5
        self.minDistCameraPlayer= (self.oDiameterPlayer - self.oDiameterPlayer/2.0) + 0.2
        self.maxDistCameraPlayer= 100
        #initialise the speed of the zoom in/out  proportionaly to this variable
        #to get a smooth zoom , this variable is apply to the self.maxDistCameraPlayer
        self.speedZoom          =  0.1

        #initialise the minimum and maximum camera pitch
        self.minPicthCamera     = -60
        self.maxPicthCamera     = 89.5

        #initilase the speed of the rotation of the player and camera orientation
        self.speedSetHPlayer    = 0.1
        self.speedPitchCamera   = 0.1

        #initialise the height of the camera proportionnaly this variable
        # is applied to self.cameraTargetHeight
        self.reduceHeightCamera = 0.5

        # This just disables the built in camera controls; we're using our own.
        base.disableMouse()

        # The mouse moves rotates the camera so lets get rid of the cursor
        self.oWindowProperties  = WindowProperties()
        self.oWindowProperties.setCursorHidden(True)
        base.win.requestProperties(self.oWindowProperties)



if __name__ == "__main__":
    w = World()
    w.run()

