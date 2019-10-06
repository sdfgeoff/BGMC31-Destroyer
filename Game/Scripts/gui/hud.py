import scheduler
import utils
import defs
import bge
import config
from .weapon_ui import WeaponUiVisuals


class HUD(utils.BaseClass):
    CONFIG_ITEMS = [
        'WEAPON_UI_CONFIG'
    ]
    def __init__(self, scene, conf, mouse):
        super().__init__(conf)
        self.log.info(self.M("create_hud"))
        self._event = scheduler.Event(self.update)
        scheduler.add_event(self._event)
        
        self.scene = scene
        self.ship = None
        self.mouse = mouse
        
        self.weapon_selector = WeaponSelector(
            [o for o in scene.objects if 'WEAPON_SELECTOR' in o][0],
            self.config['WEAPON_UI_CONFIG'],
            self.mouse
        )
        
        
    def update(self, delta):
        self.weapon_selector.update(delta)
    
    
    def set_ship(self, ship):
        self.log.debug(self.M("setting_ship"))
        self.weapon_selector.set_ship(ship)
        



class WeaponSelector(utils.BaseClass):
    """ Logic for navigating through weapon selection """
    def __init__(self, obj, conf, mouse):
        super().__init__({})
        self.log.info(self.M("create_weapon_selector"))
        self.obj = obj
        self.scene = obj.scene
        self.ship = None
        self.mouse = mouse
        
        self._display_config = conf
        self.widgets = WeaponUiVisuals(conf, self.obj, self.ship)
        self.selection_chain = [self.widgets]
        self.widgets.set_subwidgets_visible(True)
    
    def set_ship(self, ship):
        self.log.debug(self.M("setting_ship"))
        self.ship = ship
        self.recreate()
        
    def recreate(self):
        self.log.info(self.M("redraw_weapon_selector"))
        self.widgets.delete()
        self.widgets = WeaponUiVisuals(self._display_config, self.obj, self.ship)
        self.selection_chain = [self.widgets]
        self.widgets.set_subwidgets_visible(True)
        self.widgets.select_all()
    
    def update(self, delta):
        keys = {
            'ONEKEY': 1,
            'TWOKEY': 2,
            'THREEKEY':3 ,
            'FOURKEY': 4,
            'FIVEKEY': 5,
            'SIXKEY': 6,
            'SEVENKEY': 7,
            'EIGHTKEY': 8,
            'NINEKEY': 9,
            'ZEROKEY': 0,
        }
        num = None
        for key in keys.keys():
            if key_triggered(key):
                num = keys[key]

        if num != None:
            current_tip = self.selection_chain[-1]
            new_tip = get_widget_by_number(current_tip.sub_widgets, num)
            if new_tip is not None:
                self.add_to_selection_chain(new_tip)
        
        if len(self.selection_chain) > 1:
            if key_triggered(config.get('KEYS/WEAPON_SELECTION/BACK')):
                self.pop_from_selection_chain()
            if key_triggered(config.get('KEYS/WEAPON_SELECTION/RESET')):
                self.clear_selection_chain()
        
        
        if self.mouse.did_click:
            over = self.mouse.get_over(self.scene).obj
            if over:
                owner = over.get('WEAPON_WIDGET')
                if owner == self.selection_chain[-1]:
                    # Clicking on active element, close it
                    self.pop_from_selection_chain()
                else:
                    self.rebuild_selection_chain(owner)
        
        self.widgets.update(delta)
    
    def rebuild_selection_chain(self, widget):
        chain = [widget]
        while chain[-1].parent != None:
            chain.append(chain[-1].parent)
        
        self.clear_selection_chain()
        for elem in reversed(chain):
            self.add_to_selection_chain(elem)
    
    
    def add_to_selection_chain(self, new_element):
        current_tip = self.selection_chain[-1]
        current_tip.select_subwidget(new_element)
        self.selection_chain.append(new_element)
        new_element.set_subwidgets_visible(True)
        new_element.set_selected(True)
    
    def pop_from_selection_chain(self):
        assert len(self.selection_chain) > 1
        old_element = self.selection_chain.pop()
        new_element = self.selection_chain[-1]
        
        old_element.set_subwidgets_visible(False)
        old_element.set_selected(False)
        
        new_element.set_subwidgets_visible(True)
        new_element.select_all()
    
    def clear_selection_chain(self):
        while len(self.selection_chain) > 1:
            self.pop_from_selection_chain()
    
    def get_selected_guns(self):
        return self.selection_chain[-1].guns
        


def get_widget_by_number(li, num):
    found = [l for l in li if l.number == num]
    if found:
        return found[0]
    return None


def key_triggered(keyname):
    keycode = bge.events.__dict__[keyname]
    return bge.logic.keyboard.events[keycode] == bge.logic.KX_INPUT_JUST_ACTIVATED
