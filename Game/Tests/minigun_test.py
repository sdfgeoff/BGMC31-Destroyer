import minigun
import defs
import logging

logging.basicConfig(level=logging.DEBUG, format='%(message)s')


def test(cont):
    if 'GUN' not in cont.owner:
        cont.owner['GUN'] = minigun.MiniGun(cont.owner, defs.MINIGUN_CONFIG)
        cont.owner['GUN'].target(cont.owner.scene.objects['Sphere'])
