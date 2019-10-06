import utils

NUMERAL_WIDTH = 860 # Width of all the numbers in the font measured in em


class FirstItem:
    def __init__(self, obj):
        self.obj = obj
        self.bottom = obj
        self.number = None
        self.above = None
    
    def set_subwidgets_visible(self, visible):
        pass
        
    def set_visible(self, visible):
        pass
        
    def set_selected(self, val):
        pass
    
    def update(self, delta):
        pass


class StackingWidget(utils.BaseClass):
    """ Display of weapon selection """
    def __init__(self, config, above, obj_name, number):
        super().__init__(config)
        self.parent = None
        self.number = number
        self.scene = above.bottom.scene
        self.above = above
        self.top = self.scene.addObject(obj_name)
        self.top.worldPosition = self.above.bottom.worldPosition.copy()
        self.top.setParent(self.above.bottom)
        
        self.top['WEAPON_WIDGET'] = self
        
        self.bottom = self.scene.addObject("RefPosition")
        
        self.sub_widgets = []
        
        _bottom = [o for o in self.top.childrenRecursive if 'BOTTOM' in o]
        if _bottom:
            self._bottom = _bottom[0]
        else:
            self._bottom = self.top
        self.append_subwidget(FirstItem(self._bottom))
        
    def set_subwidgets_visible(self, visible):
        if visible:
            self.bottom.worldPosition = self.sub_widgets[-1].bottom.worldPosition
        else:
            self.bottom.worldPosition = self._bottom.worldPosition.copy()
            
            
        for widget in self.sub_widgets:
            widget.set_visible(visible)
            if not visible:
                widget.set_subwidgets_visible(visible)
    
    def append_subwidget(self, widget):
        self.sub_widgets.append(widget)
        self.bottom.setParent(widget.bottom)
        self.bottom.worldPosition = widget.bottom.worldPosition
        widget.parent = self
    
    def select_subwidget(self, selection):
        for widget in self.sub_widgets:
            if widget == selection:
                widget.set_selected(True)
            else:
                widget.set_selected(False)
    
    def select_all(self):
        for widget in self.sub_widgets:
            widget.set_selected(True)
    
    def set_visible(self, val):
        self.top.visible = val
        if val:
            self.top.collisionGroup = 1
        else:
            self.top.collisionGroup = 8
    
    def update(self, delta):
        for w in self.sub_widgets:
            w.update(delta)
        

            
class WeaponUiVisuals(StackingWidget):
    CONFIG_ITEMS = [
        'RAILGUN',
        'MINIGUN',
    ]
    def __init__(self, conf, obj, ship):
        super().__init__(conf, FirstItem(obj), "RefPosition", None)

        self.ship = ship
        if self.ship is None:
            self.log.debug(self.M("no_ship"))
            return
        
        self.guns = []
        
        counter = 1
        if self.ship.miniguns:
            self.log.debug(self.M("has_miniguns"))
            self.append_subwidget(WeaponCategory(
                self.config['MINIGUN'],
                self.sub_widgets[-1],
                self.ship.miniguns,
                counter
            ))
            counter += 1
            self.guns.extend(self.ship.miniguns)
            
        if self.ship.railguns:
            self.log.debug(self.M("has_railguns"))
            self.append_subwidget(WeaponCategory(
                self.config['RAILGUN'],
                self.sub_widgets[-1],
                self.ship.railguns,
                counter
            ))
            counter += 1
            self.guns.extend(self.ship.railguns)
    
    def delete(self):
        self.log.warn("Deleting not supported")
    
    
    def set_selected(self, val):
        pass
        
            
            

class WeaponCategory(StackingWidget):
    CONFIG_ITEMS = [
        'TEXT',
        'IMAGE_OFFSET'
    ]
    def __init__(self, conf, above, guns, number):
        super().__init__(conf, above, "WeaponCategory", number)
        self.log.info(self.M("creating_weapon_category"))
        self.guns = guns
        
        self.number_display = [o for o in self.top.childrenRecursive if 'NUMBER' in o][0]
        self.name_display = [o for o in self.top.childrenRecursive if 'NAME' in o][0]
        self.image_display = [o for o in self.top.childrenRecursive if 'IMAGE' in o][0]
        
        self.number_display.text = str(self.number)
        self.name_display.text = self.config['TEXT']
        self.image_display.color = [self.config['IMAGE_OFFSET'], 0, 0, 1]
        
        self.add_clusters(guns)
        self.set_subwidgets_visible(False)
    
    def set_selected(self, selected):
        if selected:
            image_color = [self.config['IMAGE_OFFSET'], 0.5, 0, 1]
            text_color = [0, 0, 0, 1]
        else:
            image_color = [self.config['IMAGE_OFFSET'], 0.5, 0, 1]
            text_color = [0, 0, 0, 0.5]
        
        self.image_display.color = image_color
        self.number_display.color = text_color


    def add_clusters(self, guns):
        clusters = guns.by_cluster()
        counter = 1
        
        for cluster_name in sorted(clusters.keys()):
            self.append_subwidget(WeaponCluster(
                {},
                self.sub_widgets[-1],
                cluster_name,
                clusters[cluster_name],
                counter
            ))
            counter += 1
            
        self.append_subwidget(EndBorder(
            self.sub_widgets[-1]
        ))
        
    def set_visible(self, visible):
        super().set_visible(visible)
        self.number_display.visible = visible
        self.name_display.visible = visible
        self.image_display.visible = visible
        self.top.visible = visible


class EndBorder(StackingWidget):
    def __init__(self, above):
        super().__init__({}, above, "WeaponUiBottom", None)
    
    def set_selected(self, selected):
        pass


class WeaponCluster(StackingWidget):
    def __init__(self, config, above, name, guns, number):
        super().__init__(config, above, "WeaponCluster", number)
        self.log.info(self.M("creating_weapon_cluster", cluster=name))
        self.guns = guns
        
        self.number_display = [o for o in self.top.childrenRecursive if 'NUMBER' in o][0]
        self.name_display = [o for o in self.top.childrenRecursive if 'NAME' in o][0]
        
        self.number_display.text = str(self.number)
        self.name_display.text = name
        self.add_guns(guns)
        self.set_subwidgets_visible(False)

    def set_selected(self, selected):
        if selected:
            color = [1.0] * 4
        else:
            color = [0.5] * 4
        
        self.number_display.color = color
        self.name_display.color = color
        

    def add_guns(self, guns):
        guns_sorted = sorted(guns, key=lambda x: x.number)
        for gun in guns_sorted:
            self.append_subwidget(WeaponItem(
                {},
                self.sub_widgets[-1],
                gun
            ))

    def set_visible(self, visible):
        super().set_visible(visible)
        self.number_display.visible = visible
        self.name_display.visible = visible
        


class WeaponItem(StackingWidget):
    def __init__(self, config, above, gun):
        super().__init__(config, above, "WeaponSingle", gun.number)
        self.log.info(self.M("creating_weapon_item", name=gun.name, number=gun.number))
        self.gun = gun
        self.guns = [gun]
        self.number_display = [o for o in self.top.childrenRecursive if 'NUMBER' in o][0]
        self.name_display = [o for o in self.top.childrenRecursive if 'NAME' in o][0]
        self.ammo_display = [o for o in self.top.childrenRecursive if 'AMMO' in o][0]
        
        self.number_display.text = str(gun.number)
        self.name_display.text = str(gun.name)
        self.set_subwidgets_visible(False)
        
        self._ammo_display_pos = self.ammo_display.localPosition.copy()

    def set_visible(self, visible):
        super().set_visible(visible)
        self.number_display.visible = visible
        self.name_display.visible = visible
        self.ammo_display.visible = visible
        
    def update(self, delta):
        now = self.gun.ammo_remaining()
        total = self.gun.ammo_maximum()
        self.ammo_display.text = "{}/{}".format(
            now,
            total
        )
    
    
    def set_selected(self, selected):
        if selected:
            color = [1.0] * 4
        else:
            color = [0.5] * 4
        
        self.number_display.color = color
        self.name_display.color = color
