# -*- coding: utf_8 -*-
from pandac.PandaModules import Vec3
from random import randrange

class AIController:
    def __init__(self,clist):
        self.clist = clist

    def update(self, task = None):
        for ch in self.clist.list:
            if ch.aitype == 1:
                if not ch.waypoints and ch.state == 'stand':
                    if ch.aistate.getTimer('wait') <= 0:
                        newx = ch.root.getX() + randrange(-15,15)
                        newy = ch.root.getY() + randrange(-15,15)
                        ch.control('replace_wp', ('goto', Vec3(newx,newy,0)))
                        ch.aistate.setTimer('wait',randrange(3,10))
                    else:
                        ch.aistate.decTimer('wait',task.delayTime)
        if task:
            return task.again

