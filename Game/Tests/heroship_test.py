import ship
import logging
import defs

logging.basicConfig(level=logging.DEBUG, format='%(message)s')


def test(cont):
    if 'SHIP' not in cont.owner:
        cont.owner['SHIP'] = ship.Ship(cont.owner, defs.HERO_CONFIG)
