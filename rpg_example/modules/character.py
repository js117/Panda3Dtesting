# -*- coding: utf_8 -*-
from direct.actor import Actor
from pandac.PandaModules import CollisionNode,CollisionHandlerQueue,\
CollisionRay,CollisionSphere, CollisionRay, CollisionHandlerPusher, \
CollisionTube
from pandac.PandaModules import BitMask32, Vec3
from direct.interval.IntervalGlobal import *

class characterCollSystem():
    def __init__(self,rootNode,trav,id):
        self.GroundRay=CollisionRay(0,0,10,0,0,-1)
        self.GroundCol = CollisionNode('colDown_'+str(id))
        self.GroundCol.addSolid(self.GroundRay)
        self.GroundCol.setFromCollideMask(BitMask32.bit(1))
        self.GroundCol.setIntoCollideMask(BitMask32.allOff())
        self.GroundColNp = rootNode.attachNewNode(self.GroundCol)
        #self.GroundColNp.show()
        self.GroundHandler = CollisionHandlerQueue()
        trav.addCollider(self.GroundColNp, self.GroundHandler)
        
        self.EnvDetector=CollisionSphere(0, 0, 1, 0.8)
        self.EnvCol = CollisionNode('colEnv_'+str(id))
        self.EnvCol.addSolid(self.EnvDetector)
        self.EnvCol.setFromCollideMask(BitMask32.bit(2))
        self.EnvCol.setIntoCollideMask(BitMask32.allOff())
        self.EnvColNp = rootNode.attachNewNode(self.EnvCol)
        #self.EnvColNp.show()
        self.pusher = CollisionHandlerPusher()
        self.pusher.addCollider(self.EnvColNp, rootNode)
        trav.addCollider(self.EnvColNp, self.pusher)
            
        self.trav=trav

class character():
    def __init__(self,modelstr,anims,trav,id):
        self.id=id
        self.root = render.attachNewNode('character'+str(id))
        self.model = Actor.Actor(modelstr,anims)
        self.model.reparentTo(self.root)
        self.model.setBlend(frameBlend = 1,blendType = 1)
        self.model.enableBlend()
        self.model.loop('walk')
        self.model.loop('stand')
        self.animInterval = LerpAnimInterval(self.model, 1, 'walk', 'stand')
        self.state = ''
        self.collsys = characterCollSystem(self.root,trav,id)
        self.waypoints = []
        self.aitype = 0
        self.aistate = AIState()

    def control(self,action,param):
        if action is'add_wp':
            self.waypoints.append(param)
        elif action is 'replace_wp':
            self.waypoints=[]
            self.waypoints.append(param)

    def switchAnimTo(self,aname,tm):
        self.animInterval.finish()
        self.animInterval=LerpAnimInterval(self.model, tm, self.state, aname)
        self.animInterval.start()
        self.state=aname

    def update(self,task = None):
        if len(self.waypoints)>0:
            act,v = self.waypoints[0]
            if act == 'goto':
                v.setZ(self.root.getZ())
                v = Vec3(v-self.root.getPos())
                if v.length()<0.3:
                    del self.waypoints[0]
                else:
                    v.normalize()
                    v2=Vec3(self.root.getQuat().getForward())
                    v2.normalize()
                    a=v2.angleDeg(v)
                    if a>10:
                        v3=self.root.getRelativeVector(render,v)
                        if v3.getX()>0: a=-a
                        self.root.setH(self.root.getH()+a*0.1)
                    self.root.setPos(self.root,0,0.045,0)
                if self.state is not 'walk':
                    self.switchAnimTo('walk',0.2)
        elif self.state is not 'stand':
            self.switchAnimTo('stand',0.3)
            
        if self.collsys.GroundHandler.getNumEntries()>0:
            self.collsys.GroundHandler.sortEntries()
            self.root.setZ(self.collsys.GroundHandler.getEntry(0).getSurfacePoint(render).getZ())
        if task:
            return task.cont


class CharactersList:
    list = []
    
    def getNewId(self):
        if self.list:
            return max([ch.id for ch in self.list]) + 1
        else: return 0
        
    def newCharacter(self,modelstr,anims,trav):
        newid = self.getNewId()
        tmpch = character(modelstr,anims,trav,newid)
        self.list.append(tmpch)
        return tmpch
        
    def update(self, task = None):
        for tmpch in self.list:
            tmpch.update()
        if task:
            return task.cont


class AIState:
    timers = {}
    
    def incTimer(self,tname,step):
        try:
            self.timers[tname] += step
        except KeyError:
            self.timers[tname] = 0
    
    def decTimer(self,tname,step):
        try:
            self.timers[tname] -= step
        except KeyError:
            self.timers[tname] = 0

    def getTimer(self,tname):
        try:
            t = self.timers[tname]
        except KeyError:
            t = 0
        return t
        
    def setTimer(self,tname,val):
        self.timers[tname] = val
