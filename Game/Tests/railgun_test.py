import railgun
import defs
import logging

logging.basicConfig(level=logging.DEBUG, format='%(message)s')


def test(cont):
    if 'GUN' not in cont.owner:
        cont.owner['GUN'] = railgun.RailGun(cont.owner, defs.RAILGUN_CONFIG)
        cont.owner['GUN'].target(cont.owner.scene.objects['Sphere'])
