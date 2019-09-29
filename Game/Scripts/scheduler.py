import collections
import bge
import logging
import cProfile
import config

from utils import StructuredMessage

TIME_FUNC = bge.logic.getClockTime
LOGGER = logging.getLogger(__name__)

Event = collections.namedtuple("Event", ['function'])

profiler = cProfile.Profile()



previous_time = TIME_FUNC()
events = []
counter = 0
create_scene_frame = -1

def ensure_scheduler_exists():
    """ Makes sure that something will run the scheduler every frame """
    for scene in bge.logic.getSceneList():
        if scene.name == 'ScriptLinker':
            break
    else:
        global create_scene_frame
        if create_scene_frame != counter:
            create_scene_frame = counter
            LOGGER.info(StructuredMessage("create_scheduler_scene", frame=create_scene_frame))
            bge.logic.addScene('ScriptLinker')
            create_scene_frame = counter


def add_event(event):
    """ Register an event to be run each frame """
    ensure_scheduler_exists()
    events.append(event)


def remove_event(event):
    """ Removes an event that has been running each frame """
    events.remove(event)


def update_events():
    """ Updates all events currently registered to the scheduler """
    if config.get('PROFILE'):
        profiler.runcall(_do_update)
        
    else:
        _do_update()

def _do_update():
    global previous_time
    global counter
    counter += 1
    now = TIME_FUNC()
    delta = now - previous_time
    previous_time = now
    for event in events:
        event.function(delta)



class OnExit:
    def __del__(self):
        if config.get('PROFILE'):
            profiler.print_stats(sort='tottime')

bge.logic.globalDict['Exit'] = OnExit()
