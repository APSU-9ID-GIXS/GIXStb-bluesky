"""
EPICS area_detector Pilatus 1M
"""

__all__ = """
    pilatus
    config_pilatus
    create_pilatus
    load_pilatus
    prepare_pilatus
""".split()

import logging

logger = logging.getLogger(__name__)

logger.info(__file__)

from .. import iconfig
import pathlib
from apstools.devices import AD_plugin_primed
from apstools.devices import AD_prime_plugin2

from apstools.devices import CamMixin_V34
from ophyd.areadetector import PilatusDetectorCam
from ophyd.areadetector import SingleTrigger
from ophyd.areadetector.filestore_mixins import FileStoreHDF5IterativeWrite
from apstools.devices import AD_EpicsFileNameHDF5Plugin
from ophyd.areadetector.plugins import HDF5Plugin_V34 as HDF5Plugin
from ophyd.areadetector.plugins import ROIPlugin_V34, StatsPlugin_V34
#from ophyd.areadetector.plugins import HDF5Plugin
from apstools.devices import SingleTrigger_V34
from ophyd import ADComponent
#from ophyd import Component as Cpt

from ophyd.areadetector import DetectorBase
from ophyd.areadetector.plugins import ImagePlugin_V34
from ophyd.areadetector.plugins import ImagePlugin
from ophyd.areadetector.plugins import PvaPlugin_V34

import bluesky.plan_stubs as bps

IOC = iconfig["ADPILATUS_IOC_PREFIX"]
IMAGE_DIR = iconfig["ADPILATUS_IMAGE_DIR"]
# Pilatus IOC sees a different local file system when it saves (HDF or other
# kinds of) files
AD_IOC_MOUNT_PATH = pathlib.Path(iconfig["PILATUS_MOUNT_PATH"])
# MUST end with a `/`, pathlib will NOT provide it
WRITE_PATH_TEMPLATE = f"{AD_IOC_MOUNT_PATH / IMAGE_DIR}/"

#TODO sort directories to be used by Chmlab
BLUESKY_MOUNT_PATH = pathlib.Path(iconfig["BLUESKY_MOUNT_PATH"])

# MUST end with a `/`, pathlib will NOT provide it
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

class HDF5PluginCustomFile(AD_EpicsFileNameHDF5Plugin):
    """
    Add data acquisition methods to HDF5Plugin.

    * ``stage()`` - prepare device PVs befor data acquisition
    * ``unstage()`` - restore device PVs after data acquisition
    * ``generate_datum()`` - coordinate image storage metadata
    """

	#Does stage need to calc NumCapture?? Probably straightforward
	# to get num_images from cam; but how to get number of points in scan?

    def stage(self):
        self.stage_sigs.move_to_end("capture", last=True)
        super().stage()
            
class PilatusDetector_V34(SingleTrigger_V34, DetectorBase):
#class PilatusDetectorHDF(SingleTrigger, DetectorBase):
    """
    ADSimDetector

    SingleTrigger:

    * stop any current acquisition
    * sets image_mode to 'Multiple'
    """
    _default_configuration_attrs = ('roi1', 'roi2', 'roi3', 'roi4')
    _default_read_attrs = ('cam', 'stats1', 'stats2', 'stats3', 'stats4')

    cam = ADComponent(PilatusDetectorCam_V34, "cam1:")
#    cam = ADComponent(PilatusDetectorCam, "cam1:")
    hdf1 = ADComponent(
        HDF5PluginCustomFile,
#       MyHDF5Plugin,
        "HDF1:",
        write_path_template=WRITE_PATH_TEMPLATE,
        read_path_template=READ_PATH_TEMPLATE,
    )
    image = ADComponent(ImagePlugin_V34, "image1:")

#    stats1 = Cpt(StatsPlugin_V34, 'Stats1:')
#    stats2 = Cpt(StatsPlugin_V34, 'Stats2:')
#    stats3 = Cpt(StatsPlugin_V34, 'Stats3:')
#    stats4 = Cpt(StatsPlugin_V34, 'Stats4:')
#   stats5 = Cpt(StatsPlugin, 'Stats5:')
    stats1 = ADComponent(StatsPlugin_V34, 'Stats1:')
    stats2 = ADComponent(StatsPlugin_V34, 'Stats2:')
    stats3 = ADComponent(StatsPlugin_V34, 'Stats3:')
    stats4 = ADComponent(StatsPlugin_V34, 'Stats4:')
    stats5 = ADComponent(StatsPlugin_V34, 'Stats5:')

#    roi1 = Cpt(ROIPlugin_V34, 'ROI1:')
#    roi2 = Cpt(ROIPlugin_V34, 'ROI2:')
#    roi3 = Cpt(ROIPlugin_V34, 'ROI3:')
#    roi4 = Cpt(ROIPlugin_V34, 'ROI4:')
    roi1 = ADComponent(ROIPlugin_V34, 'ROI1:')
    roi2 = ADComponent(ROIPlugin_V34, 'ROI2:')
    roi3 = ADComponent(ROIPlugin_V34, 'ROI3:')
    roi4 = ADComponent(ROIPlugin_V34, 'ROI4:')

    pva = ADComponent(PvaPlugin_V34, "Pva1:")

class PilatusDetector(SingleTrigger, DetectorBase):
    """
    ADSimDetector

    SingleTrigger:

    * stop any current acquisition
    * sets image_mode to 'Multiple'
    """

#    cam = ADComponent(PilatusDetectorCam_V34, "cam1:")
    cam = ADComponent(PilatusDetectorCam, "cam1:")

    # What file type should I put here? TIFF?


#    image = ADComponent(ImagePlugin_V34, "image1:")
    image = ADComponent(ImagePlugin, "image1:")



def create_pilatus(IOC, name = 'Pilatus1M', labels=("area_detector",), timeout=15, hdf = False):
    detector = PilatusDetector_V34(IOC, name=name, labels=labels)
#    if hdf:
#        detector = PilatusDetectorHDF(IOC, name=name, labels=labels)
#    else:
#        detector = PilatusDetector(IOC, name=name, labels=labels)

    detector.wait_for_connection(timeout=timeout)

    return detector


def config_pilatus(detector, hdf = False):
    detector.missing_plugins()  # confirm all plugins are defined
    if hdf:
        detector.read_attrs.append("hdf1")  # include `hdf1` plugin with 'detector.read()'

    # override default settings from ophyd
    # Plugins will tell the camera driver when acquisition is finished.
    # RunEngine will wait until `pilatus:cam1:AcquireBusy_RBV` PV goes to zero.
    detector.cam.stage_sigs["wait_for_plugins"] = "Yes"
    if hdf:
        detector.hdf1.stage_sigs["blocking_callbacks"] = "No"
    detector.image.stage_sigs["blocking_callbacks"] = "No"

    if hdf and not iconfig.get("ALLOW_AREA_DETECTOR_WARMUP"):
        logger.info("HDF plugin warmup for area detector IOC '%s'", IOC)
        # Even with `lazy_open=1`, ophyd checks if the area
        # detector HDF5 plugin has been primed.  We might
        # need to prime it.  Here's ophyd's test:
        # if np.array(adsimdet.hdf1.array_size.get()).sum() == 0:
        #     logger.info(f"Priming {adsimdet.hdf1.name} ...")
        #     adsimdet.hdf1.warmup()
        #     logger.info(f"Enabling {adsimdet.image.name} plugin ...")
        #     adsimdet.image.enable.put("Enable")
        # This test is not sufficient.
        # WORKAROUND (involving a few more tests)
        if not AD_plugin_primed(detector.hdf1):
            logger.info("Priming HDF plugin for area detector IOC '%s'", IOC)
            AD_prime_plugin2(detector.hdf1)

    logger.info("Setting up ROI and STATS defaults for '%s'",IOC)
    for name in detector.component_names:
        if "roi" in name:
            roi = getattr(detector, name)
            roi.wait_for_connection(timeout=10)
            roi.nd_array_port.put("PIL")
            logger.info(f"Setting {roi.port_name.get()} input to PIL")
        if "stats" in name:
            stat = getattr(detector, name)
            stat.wait_for_connection(timeout=10)
            stat_portName = stat.port_name.get()
            if stat_portName[-1] == '5':
                logger.info(f"Setting {stat_portName} input to PIL")
                stat.nd_array_port.put("PIL")
            else:
                logger.info(f"Setting {stat_portName} input to ROI{stat_portName[-1]}")
                stat.nd_array_port.put(f"ROI{stat_portName[-1]}")
    return detector


def load_pilatus(IOC, name = 'Pilatus1M', labels=("area_detector",), timeout=15, hdf = False):
    try:
        pilatus = create_pilatus(IOC, name=name, labels=labels, timeout=timeout, hdf = hdf)
    except TimeoutError:
        logger.warning("Did not connect to Pilatus 1M area detector IOC '%s'", IOC)
        pilatus = None
    else:
        logger.info("Configuring plugins for area detector IOC '%s'", IOC)
        pilatus = config_pilatus(pilatus, hdf = hdf)

    return pilatus

def prepare_pilatus(
    detector, plugin, file_name,
    exposure_time=None,
    acquire_period=None,
    n_images=None,
    auto_increment="Yes",
    auto_save="Yes",
    compression=None,
    create_directory=-5,
    file_path=None,
    file_template=None,
):
    
    try: 
        comp = getattr(detector, plugin)
    except:
        print(f"Can\'t find {name} in detector. Prep incomplete")
        return
    
    exposure_time = exposure_time or detector.cam.acquire_time.get()
    acquire_period = acquire_period or detector.cam.acquire_period.get()
    n_images= n_images or detector.cam.num_images.get()
    n_images = max(n_images, 1)
    compression = compression or "zlib"
    file_path = file_path or comp.write_path_template  # WRITE_PATH_TEMPLATE
    file_template = file_template or "%s%s_%4.4d.h5"

    yield from bps.mv(
        detector.cam.num_images, n_images,
        detector.cam.acquire_time, exposure_time,
        detector.cam.acquire_period, acquire_period,
        comp.auto_increment, auto_increment,
        comp.auto_save, auto_save,
        comp.create_directory, create_directory,
        comp.file_name, file_name,
        comp.file_path, file_path,
        comp.num_capture, 0,  # save all frames received
        comp.compression, compression,
        comp.file_template, file_template,
    )


    
    
pilatus = load_pilatus(IOC, hdf = True)




