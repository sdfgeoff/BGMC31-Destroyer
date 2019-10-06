import utils

NUMERAL_WIDTH = 860 # Width of all the numbers in the font measured in em


class FirstItem:
    def __init__(self, obj):
        self.obj = obj
        self.bottom = obj
        self.number = None
        
    def set_selected(self, val):
        pass
    
    def update(self, delta):
        pass
        
    def delete(self):
        pass


class StackingWidget(utils.BaseClass):
    """ Display of weapon selection """
    def __init__(self, scene, config, obj_name, number):
        super().__init__(config)
        self.log.info(self.M("creating_stacking_widget", obj=obj_name))
        self.parent = None
        self.number = number
        self.scene = scene
        
        self.top = self.scene.addObject(obj_name)
        
        self.top['WEAPON_WIDGET'] = self # So we can click on things and find our way back to this class
        
        self.bottom = self.scene.addObject("RefPosition")
        self._bottom = [o for o in self.top.childrenRecursive if 'BOTTOM' in o][0]
        self.bottom.worldPosition = self._bottom.worldPosition.copy()
        
        self.bottom.setParent(self._bottom)
        
        self.sub_widgets = [FirstItem(self._bottom)]
        self._expanded = False
    
    def append_subwidget(self, widget):
        prev_bottom = self.sub_widgets[-1]
        widget.top.setParent(prev_bottom.bottom)
        widget.top.worldPosition = prev_bottom.bottom.worldPosition
        
        self.sub_widgets.append(widget)
        
        self.bottom.setParent(widget.bottom)
        self.bottom.worldPosition = widget.bottom.worldPosition
        
        widget.parent = self  # So we can navigate up the tree
    
    def remove_subwidget(self, widget):
        self.log.info(self.M("removing_subwidget", obj=self.top.name))
        assert widget in self.sub_widgets
        assert widget != self.sub_widgets[0]
        
        assert widget == self.sub_widgets[-1] # Tempoarily ensure we only remove the end subwidget
        
        self.sub_widgets.remove(widget)
        
        for child in widget.bottom.children:
            child.setParent(self.sub_widgets[-1].bottom)
        
        bottom_widget = self.sub_widgets[-1]
        self.bottom.setParent(bottom_widget.bottom)
        self.bottom.worldPosition = bottom_widget.bottom.worldPosition


    def delete_subwidgets(self):
        for widget in reversed(self.sub_widgets[1:]):
            widget.delete()
        self.sub_widgets = self.sub_widgets[:1]
        
    
    def select_subwidget(self, selection):
        for widget in self.sub_widgets:
            if widget == selection:
                widget.set_selected(True)
            else:
                widget.set_selected(False)
    
    def select_all(self):
        for widget in self.sub_widgets:
            widget.set_selected(True)
    
    def update(self, delta):
        for w in self.sub_widgets:
            w.update(delta)
        
    def delete(self):
        self.log.info(self.M("deleting_stacking_widget", obj=self.top.name))
        
        # Remove all subwidgets first
        self.delete_subwidgets()
        
        if self.parent != None:
            self.parent.remove_subwidget(self)
        
        for o in self.top.childrenRecursive:
            o.endObject()
        
        self.top.endObject()
        print(self.top, self.bottom.parent)
        assert self._bottom is self.bottom.parent
        self.bottom.endObject()
    
    
    def set_expanded(self, expanded):
        if expanded:
            if not self._expanded:
                self.log.info(self.M("expanding_widget", obj=self.top.name))
                self.add_subwidgets()
        else:
            self.log.info(self.M("unexpanding_widget", obj=self.top.name))
            self.delete_subwidgets()
        self._expanded = expanded
    
    
    def add_subwidgets(self):
        self.log.warn(self.M("add_subwidgets_not_overridden", obj=self.top.name))


class WeaponUiVisuals(StackingWidget):
    CONFIG_ITEMS = [
        'RAILGUN',
        'MINIGUN',
    ]
    def __init__(self, scene, conf, obj, ship):
        super().__init__(scene, conf, "WeaponSelectionHeading", None)
        self.top.setParent(obj)
        self.top.worldPosition = obj.worldPosition
        self.guns = []
        self.ship = ship
        
        if self.ship is None:
            self.log.debug(self.M("no_ship"))
        else:
            self.guns.extend(self.ship.miniguns)
            self.guns.extend(self.ship.railguns)
        
    def add_subwidgets(self):
        if self.ship is None:
            self.log.debug(self.M("no_ship"))
            return

        counter = 1
        if self.ship.miniguns:
            self.log.debug(self.M("has_miniguns"))
            self.append_subwidget(WeaponCategory(
                self.scene,
                self.config['MINIGUN'],
                self.ship.miniguns,
                counter
            ))
            counter += 1
            
        if self.ship.railguns:
            self.log.debug(self.M("has_railguns"))
            self.append_subwidget(WeaponCategory(
                self.scene,
                self.config['RAILGUN'],
                self.ship.railguns,
                counter
            ))
            counter += 1
    
    def set_selected(self, val):
        pass
        
            
class WeaponCategory(StackingWidget):
    CONFIG_ITEMS = [
        'TEXT',
        'IMAGE_OFFSET'
    ]
    def __init__(self, scene, conf, guns, number):
        super().__init__(scene, conf, "WeaponCategory", number)
        self.guns = guns
        
        self.number_display = [o for o in self.top.childrenRecursive if 'NUMBER' in o][0]
        self.name_display = [o for o in self.top.childrenRecursive if 'NAME' in o][0]
        self.image_display = [o for o in self.top.childrenRecursive if 'IMAGE' in o][0]
        
        self.number_display.text = str(self.number)
        self.name_display.text = self.config['TEXT']
        self.image_display.color = [self.config['IMAGE_OFFSET'], 0, 0, 1]
        
        utils.fix_text(self.number_display)
        utils.fix_text(self.name_display)
    
    def set_selected(self, selected):
        if selected:
            image_color = [self.config['IMAGE_OFFSET'], 0.5, 0, 1]
            text_color = [0, 0, 0, 1]
        else:
            
            image_color = [self.config['IMAGE_OFFSET'], 0.5, 0, 1]
            text_color = [0, 0, 0, 0.5]
        
        self.image_display.color = image_color
        self.number_display.color = text_color

    def add_subwidgets(self):
        clusters = self.guns.by_cluster()
        counter = 1
        
        for cluster_name in sorted(clusters.keys()):
            self.append_subwidget(WeaponCluster(
                self.scene,
                {},
                cluster_name,
                clusters[cluster_name],
                counter
            ))
            counter += 1
            
        self.append_subwidget(EndBorder(self.scene))


class EndBorder(StackingWidget):
    def __init__(self, scene):
        super().__init__(scene, {}, "WeaponUiBottom", None)
    
    def set_selected(self, selected):
        pass


class WeaponCluster(StackingWidget):
    def __init__(self, scene, config, name, guns, number):
        super().__init__(scene, config, "WeaponCluster", number)
        self.guns = guns
        
        self.number_display = [o for o in self.top.childrenRecursive if 'NUMBER' in o][0]
        self.name_display = [o for o in self.top.childrenRecursive if 'NAME' in o][0]
        
        self.number_display.text = str(self.number)
        self.name_display.text = name
        
        utils.fix_text(self.number_display)
        utils.fix_text(self.name_display)

    def set_selected(self, selected):
        if selected:
            color = [1.0] * 4
        else:
            color = [0.5] * 4
        
        self.number_display.color = color
        self.name_display.color = color
        

    def add_subwidgets(self):
        guns_sorted = sorted(self.guns, key=lambda x: x.number)
        for gun in guns_sorted:
            self.append_subwidget(WeaponItem(
                self.scene,
                {},
                gun
            ))


class WeaponItem(StackingWidget):
    def __init__(self, scene, config, gun):
        super().__init__(scene, config, "WeaponSingle", gun.number)
        self.log.info(self.M("creating_weapon_item", name=gun.name, number=gun.number))
        self.gun = gun
        self.guns = [gun]
        self.number_display = [o for o in self.top.childrenRecursive if 'NUMBER' in o][0]
        self.name_display = [o for o in self.top.childrenRecursive if 'NAME' in o][0]
        self.ammo_display = [o for o in self.top.childrenRecursive if 'AMMO' in o][0]
        
        utils.fix_text(self.number_display)
        utils.fix_text(self.name_display)
        utils.fix_text(self.ammo_display)
        
        
        self.number_display.text = str(gun.number)
        self.name_display.text = str(gun.name)
        
        self._ammo_display_pos = self.ammo_display.localPosition.copy()
        
    def update(self, delta):
        now = self.gun.ammo_remaining()
        total = self.gun.ammo_maximum()
        self.ammo_display.text = "{}/{}".format(
            now,
            total
        )
        
        self.ammo_display.localPosition.x = self._ammo_display_pos.x - len(self.ammo_display.text) * 0.45
    
    
    def set_selected(self, selected):
        if selected:
            color = [1.0] * 4
        else:
            color = [0.5] * 4
        
        self.number_display.color = color
        self.name_display.color = color
