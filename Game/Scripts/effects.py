import mathutils
import bge


FLOAT_SCALE = 0.05
def smoke_float(cont):
    cont.owner['VELOCITY'] = cont.owner.get('VELOCITY', cont.owner.getAxisVect([0,0,1]) * 0.2)
    cont.owner['VELOCITY'] += mathutils.Vector([
        (bge.logic.getRandomFloat() - 0.5) * FLOAT_SCALE,
        (bge.logic.getRandomFloat() - 0.5) * FLOAT_SCALE,
        (bge.logic.getRandomFloat() - 0.5) * FLOAT_SCALE,
    ])
    cont.owner.worldPosition += cont.owner['VELOCITY']
