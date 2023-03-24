"""
EPICS area_detector Pilatus 1M
"""

__all__ = """
	pilatus
""".split()

import logging

logger = logging.getLogger(__name__)

logger.info(__file__)

from .. import iconfig
import pathlib
from apstools.devices import CamMixin_V34
from ophyd.areadetector import PilatusDetectorCam
from ophyd.areadetector.filestore_mixins import FileStoreHDF5IterativeWrite
from ophyd.areadetector.plugins import HDF5Plugin_V34 as HDF5Plugin
from apstools.devices import SingleTrigger_V34
from ophyd import ADComponent
from ophyd.areadetector import DetectorBase

IOC = iconfig["ADPILATUS_IOC_PREFIX"]

#TODO sort directories to be used by Chmlab
IMAGE_DIR = iconfig["AD_IMAGE_DIR"]
AD_IOC_MOUNT_PATH = pathlib.Path(iconfig["AD_MOUNT_PATH"])
BLUESKY_MOUNT_PATH = pathlib.Path(iconfig["BLUESKY_MOUNT_PATH"])

# MUST end with a `/`, pathlib will NOT provide it
WRITE_PATH_TEMPLATE = f"{AD_IOC_MOUNT_PATH / IMAGE_DIR}/"
READ_PATH_TEMPLATE = f"{BLUESKY_MOUNT_PATH / IMAGE_DIR}/"


class PilatusDetectorCam_V34(CamMixin_V34, PilatusDetectorCam):
    """Update PilatusDetectorCam to ADCore 3.4+."""


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


class PilatusDetector_V34(SingleTrigger_V34, DetectorBase):
    """
    ADSimDetector

    SingleTrigger:

    * stop any current acquisition
    * sets image_mode to 'Multiple'
    """

    cam = ADComponent(PilatusDetectorCam_V34, "cam1:")
    hdf1 = ADComponent(
        MyHDF5Plugin,
        "HDF1:",
        write_path_template=WRITE_PATH_TEMPLATE,
        read_path_template=READ_PATH_TEMPLATE,
    )
    image = ADComponent(ImagePlugin, "image1:")


try:
	pilatus = PilatusDetector_V34(IOC, name="pilatus1M")
	pilatus.wait_for_connection(timeout=15)
except TimeoutError:
    logger.warning("Did not connect to Pilatus 1M area detector IOC '%s'", IOC)
    pilatus = None
else:
    pilatus.missing_plugins()  # confirm all plugins are defined
	pilatus.read_attrs.append("hdf1")  # include `hdf1` plugin with 'pilatus.read()'
	
	# override default settings from ophyd
	# Plugins will tell the camera driver when acquisition is finished.
	# RunEngine will wait until `pilatus:cam1:AcquireBusy_RBV` PV goes to zero.
	pilatus.cam.stage_sigs["wait_for_plugins"] = "Yes"
	pilatus.hdf1.stage_sigs["blocking_callbacks"] = "No"
	pilatus.image.stage_sigs["blocking_callbacks"] = "No"

	# override default settings from ophyd
	# Plugins will tell the camera driver when acquisition is finished.
	# RunEngine will wait until `pilatus:cam1:AcquireBusy_RBV` PV goes to zero.
	pilatus.cam.stage_sigs["wait_for_plugins"] = "Yes"
	pilatus.hdf1.stage_sigs["blocking_callbacks"] = "No"
	pilatus.image.stage_sigs["blocking_callbacks"] = "No"


