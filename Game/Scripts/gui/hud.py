import scheduler
import utils
import defs
import bge


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
            self.config['WEAPON_UI_CONFIG']
        )
        
        
    def update(self, delta):
        self.weapon_selector.update(delta)
    
    
    def set_ship(self, ship):
        self.log.debug(self.M("setting_ship"))
        self.weapon_selector.set_ship(ship)
        



class WeaponSelector(utils.BaseClass):
    CONFIG_ITEMS = [
        'RAILGUN',
        'MINIGUN',
    ]
    def __init__(self, obj, conf):
        super().__init__(conf)
        self.log.info(self.M("create_weapon_selector"))
        self.obj = obj
        self.scene = obj.scene
        self.ship = None
        
        self.objs = [FirstItem(self.obj)]
        
        self.recreate()
    
    
    def set_ship(self, ship):
        self.log.debug(self.M("setting_ship"))
        self.ship = ship
        self.recreate()
        
    def recreate(self):
        self.log.info(self.M("redraw_weapon_selector"))
        
        for obj in self.objs[1:]:
            obj.delete()
        self.objs = self.objs[:1]
        
        if self.ship is None:
            self.log.debug(self.M("no_ship"))
            return
        
        counter = 1
        if self.ship.miniguns:
            self.log.debug(self.M("has_miniguns"))
            self.objs.append(WeaponCategory(
                self.config['MINIGUN'],
                self.objs[-1],
                self.ship.miniguns,
                counter
            ))
            counter += 1
            
        if self.ship.railguns:
            self.log.debug(self.M("has_railguns"))
            self.objs.append(WeaponCategory(
                self.config['RAILGUN'],
                self.objs[-1],
                self.ship.railguns,
                counter
            ))
            counter += 1
    
    def update(self, delta):
        keys = {
            bge.events.ONEKEY: 1,
            bge.events.TWOKEY: 2,
            bge.events.THREEKEY:3 ,
            bge.events.FOURKEY: 4,
            bge.events.FIVEKEY: 5,
            bge.events.SIXKEY: 6,
            bge.events.SEVENKEY: 7,
            bge.events.EIGHTKEY: 8,
            bge.events.NINEKEY: 9,
            bge.events.ZEROKEY: 0,
        }
        num = None
        for key in keys.keys():
            if bge.logic.keyboard.events[key] == bge.logic.KX_INPUT_JUST_ACTIVATED:
                num = keys[key]
        if num != None:
            for obj in self.objs:
                obj.set_selected(obj.number == num)



class FirstItem:
    def __init__(self, obj):
        self.obj = obj
        self.bottom = obj
        self.number = 0
    
    def set_subwidgets_visible(self, visible):
        pass
        
    def set_visible(self, visible):
        pass
        
    def set_selected(self, val):
        pass


class StackingWidget(utils.BaseClass):
    def __init__(self, config, above, obj_name):
        super().__init__(config)
        self.scene = above.bottom.scene
        self.above = above
        self.top = self.scene.addObject(obj_name)
        self.top.worldPosition = self.above.bottom.worldPosition.copy()
        self.top.setParent(self.above.bottom)
        
        self.bottom = self.scene.addObject("RefPosition")
        self._bottom = [o for o in self.top.childrenRecursive if 'BOTTOM' in o][0]
        
        self.sub_widgets = [FirstItem(self._bottom)]
        
    def set_subwidgets_visible(self, visible):
        for widget in self.sub_widgets:
            widget.set_visible(visible)
            if not visible:
                widget.set_subwidgets_visible(visible)
            
        if visible:
            self.bottom.worldPosition = self.sub_widgets[-1].bottom.worldPosition
        else:
            print(self.top.name, self._bottom.worldPosition)
            self.bottom.worldPosition = self._bottom.worldPosition.copy()
            

            

class WeaponCategory(StackingWidget):
    CONFIG_ITEMS = [
        'TEXT',
        'IMAGE_OFFSET'
    ]
    def __init__(self, conf, above, guns, number):
        super().__init__(conf, above, "WeaponCategory")
        self.number = number
        self.log.info(self.M("creating_weapon_category"))
        
        self.number_display = [o for o in self.top.childrenRecursive if 'NUMBER' in o][0]
        self.name_display = [o for o in self.top.childrenRecursive if 'NAME' in o][0]
        self.image_display = [o for o in self.top.childrenRecursive if 'IMAGE' in o][0]
        
        self.number_display.text = str(self.number)
        self.name_display.text = self.config['TEXT']
        self.image_display.color = [self.config['IMAGE_OFFSET'], 0, 0, 1]
        
        self.add_clusters(guns)
        self.set_selected(False)
    
    
    def set_selected(self, selected):
        if selected:
            self.image_display.color = [self.config['IMAGE_OFFSET'], 1.0, 0, 1]
            self.number_display.visible = False
            self.set_subwidgets_visible(True)
        else:
            self.image_display.color = [self.config['IMAGE_OFFSET'], 0.5, 0, 1]
            self.number_display.visible = True
            self.set_subwidgets_visible(False)


    def add_clusters(self, guns):
        clusters = guns.by_cluster()
        counter = 1
        
        for cluster_name in sorted(clusters.keys()):
            self.sub_widgets.append(WeaponCluster(
                {},
                self.sub_widgets[-1],
                cluster_name,
                clusters[cluster_name],
                counter
            ))
            counter += 1
            
        self.sub_widgets.append(EndBorder(
            self.sub_widgets[-1]
        ))
        
    def set_visible(self, visible):
        self.number_display.visible = visible
        self.name_display.visible = visible
        self.image_display.visible = visible
        self.top.visible = visible


class EndBorder(StackingWidget):
    def __init__(self, above):
        super().__init__({}, above, "WeaponUiBottom")
    
    def set_visible(self, visible):
        self.top.visible = visible


class WeaponCluster(StackingWidget):
    def __init__(self, config, above, name, guns, number):
        super().__init__(config, above, "WeaponCluster")
        self.number = number
        self.log.info(self.M("creating_weapon_cluster", cluster=name))
        
        self.number_display = [o for o in self.top.childrenRecursive if 'NUMBER' in o][0]
        self.name_display = [o for o in self.top.childrenRecursive if 'NAME' in o][0]
        
        self.number_display.text = str(self.number)
        self.name_display.text = name
        self.add_guns(guns)

    def add_guns(self, guns):
        guns_sorted = sorted(guns, key=lambda x: x.number)
        for gun in guns_sorted:
            self.sub_widgets.append(WeaponItem(
                {},
                self.sub_widgets[-1],
                gun
            ))


    def set_visible(self, visible):
        self.number_display.visible = visible
        self.name_display.visible = visible
        self.top.visible = visible


class WeaponItem(StackingWidget):
    def __init__(self, config, above, gun):
        super().__init__(config, above, "WeaponSingle")
        self.log.info(self.M("creating_weapon_item", name=gun.name, number=gun.number))
        
        self.number_display = [o for o in self.top.childrenRecursive if 'NUMBER' in o][0]
        self.name_display = [o for o in self.top.childrenRecursive if 'NAME' in o][0]
        self.ammo_display = [o for o in self.top.childrenRecursive if 'AMMO' in o][0]
        
        self.number_display.text = str(gun.number)
        self.name_display.text = str(gun.name)
        
        self.set_selected

    def set_visible(self, visible):
        self.number_display.visible = visible
        self.name_display.visible = visible
        self.top.visible = visible
        self.ammo_display.visible = visible
    
    
    def set_selected(self, selected):
        if selected:
            color = [1.0 * 4]
        else:
            color = [0.5 * 4]
        
        self.number_display.color = color
        self.name_display.color = color
