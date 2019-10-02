import utils


class Gun(utils.BaseClass):
    def __init__(self, obj, conf):
        self.cluster = obj['CLUSTER']
        self.name = obj['NAME']
        self.number = obj['ID']
        super().__init__(conf)
