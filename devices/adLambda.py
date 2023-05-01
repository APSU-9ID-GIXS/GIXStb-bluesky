"""
EPICS area_detector Lambda 750, IOC uses AD 3-2
"""

__all__ = """
    adLambda
    create_lambda
    config_lambda
    load_lambda
""".split()

import logging

logger = logging.getLogger(__name__)

logger.info(__file__)

from .. import iconfig

from ophyd.areadetector import Lambda750kCam
from ophyd.areadetector import SingleTrigger

#from apstools.devices import CamMixin_V34

from .calculation_records import calcs
from apstools.devices import AD_plugin_primed
from apstools.devices import AD_prime_plugin2
#from apstools.devices import SingleTrigger_V34
from ophyd import ADComponent
from ophyd import DetectorBase
from ophyd import SimDetectorCam
from ophyd.areadetector.filestore_mixins import FileStoreHDF5IterativeWrite
#from ophyd.areadetector.plugins import HDF5Plugin_V34
from ophyd.areadetector.plugins import HDF5Plugin
#from ophyd.areadetector.plugins import ImagePlugin_V34
from ophyd.areadetector.plugins import ImagePlugin
import numpy as np
import pathlib


IOC = iconfig["ADLAMBDA_IOC_PREFIX"]
IMAGE_DIR = iconfig["ADLAMBDA_IMAGE_DIR"]
AD_IOC_MOUNT_PATH = pathlib.Path(iconfig["AD_MOUNT_PATH"])
# MUST end with a `/`, pathlib will NOT provide it
WRITE_PATH_TEMPLATE = f"{AD_IOC_MOUNT_PATH / IMAGE_DIR}/"

#TODO sort directories to be used by Chmlab
BLUESKY_MOUNT_PATH = pathlib.Path(iconfig["BLUESKY_MOUNT_PATH"])

# MUST end with a `/`, pathlib will NOT provide it
READ_PATH_TEMPLATE = f"{BLUESKY_MOUNT_PATH / IMAGE_DIR}/"


#class LambdaDetectorCam_V34(CamMixin_V34, Lambda750kCam):
#    """Update LambdaDetectorCam to ADCore 3.4+."""


#class MyHDF5Plugin(FileStoreHDF5IterativeWrite, HDF5Plugin_V34):
class MyHDF5Plugin(FileStoreHDF5IterativeWrite, HDF5Plugin):
    """
    Add data acquisition methods to HDF5Plugin.

    * ``stage()`` - prepare device PVs befor data acquisition
    * ``unstage()`` - restore device PVs after data acquisition
    * ``generate_datum()`` - coordinate image storage metadata
    """

    def stage(self):
        self.stage_sigs.move_to_end("capture", last=True)
        super().stage()


#class LambdaDetector_V34(SingleTrigger_V34, DetectorBase):
class LambdaDetector(SingleTrigger, DetectorBase):
    """
    ADLambda750k

    SingleTrigger:

    * stop any current acquisition
    * sets image_mode to 'Multiple'
    """

#    cam = ADComponent(LambdaDetectorCam_V34, "cam1:")
    cam = ADComponent(Lambda750kCam, "cam1:")
    hdf1 = ADComponent(
        MyHDF5Plugin,
        "HDF1:",
        write_path_template=WRITE_PATH_TEMPLATE,
        read_path_template=READ_PATH_TEMPLATE,
    )
#    image = ADComponent(ImagePlugin_V34, "image1:")
    image = ADComponent(ImagePlugin, "image1:")


def create_lambda(IOC, name = 'Lambda750k', labels=("area_detector",), timeout=15):
    
#    detector = LambdaDetector_V34(IOC, name=name, labels=labels)
    detector = LambdaDetector(IOC, name=name, labels=labels)
    detector.wait_for_connection(timeout=timeout)
    
    return detector

def config_lambda(detector):
    detector.missing_plugins()  # confirm all plugins are defined
    detector.read_attrs.append("hdf1")  # include `hdf1` plugin with 'detector.read()'
    
    # override default settings from ophyd
    # Plugins will tell the camera driver when acquisition is finished.
    # RunEngine will wait until `adLambda:cam1:AcquireBusy_RBV` PV goes to zero.
#    detector.cam.stage_sigs["wait_for_plugins"] = "Yes"
#    detector.hdf1.stage_sigs["blocking_callbacks"] = "No"
#    detector.image.stage_sigs["blocking_callbacks"] = "No"

    return detector
    
def load_lambda(IOC, name = 'Lambda', labels=("area_detector",), timeout=15):
    try: 
        adLambda = create_lambda(IOC, name=name, labels=labels, timeout=timeout)
    except TimeoutError:
        logger.warning("Did not connect to Lambda 750k area detector IOC '%s'", IOC)
        adLambda = None 
    else:
        adLambda = config_lambda(adLambda)
        
    return adLambda
        
adLambda = load_lambda(IOC)

