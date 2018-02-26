# -*- coding: utf_8 -*-
from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import CollisionTraverser,CollisionNode
from pandac.PandaModules import CollisionHandlerQueue,CollisionRay
from pandac.PandaModules import BitMask32,Vec3
from modules.globals import *
#import math

class mouseControl(DirectObject):
    def __init__(self):
        self.picker         = CollisionTraverser()            
        self.pickerQ        = CollisionHandlerQueue()         
        pickerCollN         = CollisionNode('mouseRay')       
        pickerCamN          = base.camera.attachNewNode(pickerCollN) 
        pickerCollN.setFromCollideMask(BitMask32.bit(1))         
        pickerCollN.setIntoCollideMask(BitMask32.allOff())         
        self.pickerRay      = CollisionRay()                
        pickerCollN.addSolid(self.pickerRay)      
        self.picker.addCollider(pickerCamN, self.pickerQ) 
        self.accept('mouse1',self.pick)                
    
    def pick(self):
        if base.mouseWatcherNode.hasMouse():
            mpos = base.mouseWatcherNode.getMouse()
            self.pickerRay.setFromLens(base.camNode, mpos.getX(), mpos.getY())
            self.picker.traverse(render)
            for i in xrange(self.pickerQ.getNumEntries()):
                entry=self.pickerQ.getEntry(i)
                player.control('replace_wp', ('goto', Vec3(entry.getSurfacePoint(render))))

class heightChecker():
    def __init__(self):
        self.picker         = CollisionTraverser()            
        self.pickerQ        = CollisionHandlerQueue()         
        pickerCollN         = CollisionNode('heightChecker')       
        self.pickerNode     = render.attachNewNode(pickerCollN) 
        pickerCollN.setFromCollideMask(BitMask32.bit(1))         
        pickerCollN.setIntoCollideMask(BitMask32.allOff())         
        self.pickerRay      = CollisionRay(0,0,300,0,0,-1)                
        pickerCollN.addSolid(self.pickerRay)      
        self.picker.addCollider(self.pickerNode, self.pickerQ)
    def getHeight(self,obj,pos):
        res=0
        self.pickerNode.setPos(pos)
        self.picker.traverse(obj)
        if self.pickerQ.getNumEntries() > 0:
            self.pickerQ.sortEntries()
            res=self.pickerQ.getEntry(0).getSurfacePoint(render).getZ()
        return res

class cameraHandler(DirectObject):
    def __init__(self):
        base.disableMouse()
        self.mx,self.my=0,0
        self.dragging=False
        self.hc=heightChecker()
        
        self.j1 = render.attachNewNode('cam_j1')
        self.j2 = self.j1.attachNewNode('cam_j2')
        self.j2.setZ(5)
        self.j3 = self.j2.attachNewNode('cam_j3')
        self.j3.setY(-40)
        
        self.accept("mouse3",self.drag,[True])
        self.accept("mouse3-up",self.drag,[False])
        self.accept("wheel_up", self.adjustCamDist,[0.9])
        self.accept("wheel_down", self.adjustCamDist,[1.1])    
        
        taskMgr.add(self.dragTask,'dragTask')   

    def turnCamera(self,tx,ty):
        self.j1.setH(self.j1.getH()+tx)
        self.j2.setP(self.j2.getP()-ty)
        if self.j2.getP()<-80:
            self.j2.setP(-80)
        if self.j2.getP()>-10:
            self.j2.setP(-10)

    def drag(self,bool):
        self.dragging=bool

    def adjustCamDist(self,aspect):
        self.j3.setY(self.j3.getY()*aspect)

    def dragTask(self,task):
        if base.mouseWatcherNode.hasMouse():
            mpos = base.mouseWatcherNode.getMouse() 
            if self.dragging:
                self.turnCamera((self.mx-mpos.getX())*100,(self.my-mpos.getY())*100)
            else:
                if self.my>0.8:
                    aspect=-(1-self.my-0.2)*5
                    self.j1.setY(self.j1,aspect)
                if self.my<-0.8:
                    aspect=(1+self.my-0.2)*5
                    self.j1.setY(self.j1,aspect)
                if self.mx>0.8:
                    aspect=-(1-self.mx-0.2)*5
                    self.j1.setX(self.j1,aspect)
                if self.mx<-0.8:
                    aspect=(1+self.mx-0.2)*5
                    self.j1.setX(self.j1,aspect)
            self.mx=mpos.getX()
            self.my=mpos.getY()                               
        self.j1.setZ(self.hc.getHeight(render,self.j1.getPos()))
        deltaZ=self.j3.getZ(render)-(self.hc.getHeight(render,self.j3.getPos(render))+5)
        if deltaZ<0:
            self.turnCamera(0,-deltaZ)
        vDir=Vec3(self.j3.getPos(render))-Vec3(base.camera.getPos(render))
        vDir=vDir*0.2
        base.camera.setPos(Vec3(base.camera.getPos())+vDir)
        base.camera.lookAt(self.j1.getPos(render))
        return task.cont   
