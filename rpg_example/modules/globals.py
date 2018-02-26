# -*- coding: utf_8 -*-
from modules.character import CharactersList
from modules.aicontroller import AIController
import direct.directbase.DirectStart
from pandac.PandaModules import CollisionTraverser

base.cTrav=CollisionTraverser()
clist = CharactersList()
aictrl = AIController(clist)
player = clist.newCharacter('res/actors/gnum',{'stand':'res/actors/gnum-stand','walk':'res/actors/gnum-walk'},base.cTrav)
player.model.setScale(0.3)

taskMgr.add(clist.update,'characters update')
taskMgr.doMethodLater(0.5, aictrl.update, 'AI update')
