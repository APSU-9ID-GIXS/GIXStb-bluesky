"""
8idChemLab motors
"""

__all__ = """
    m1  m2  m3  m4
    m5  m6  m7  m8
    m9  m10 m11 m12
    m13 m14 m15 m16
    simm1 simm2 simm3
    simm4 simm5 simm6
    simm7 simm8
""".split()

import logging

logger = logging.getLogger(__name__)

logger.info(__file__)

from .. import iconfig
from ophyd import EpicsMotor, Component, EpicsSignal


IOC = iconfig.get("GP_IOC_PREFIX", "gp:")


class MyEpicsMotor(EpicsMotor):
    steps_per_revolution = Component(EpicsSignal, ".SREV", kind="omitted")


m1 = MyEpicsMotor(f"{IOC}m1", name="th-act", labels=("motor",))
m2 = MyEpicsMotor(f"{IOC}m2", name="chi-act", labels=("motor",))
m3 = MyEpicsMotor(f"{IOC}m3", name="m3", labels=("motor",))
m4 = MyEpicsMotor(f"{IOC}m4", name="samx", labels=("motor",))
m5 = MyEpicsMotor(f"{IOC}m5", name="samy", labels=("motor",))
m6 = MyEpicsMotor(f"{IOC}m6", name="m6", labels=("motor",))
m7 = MyEpicsMotor(f"{IOC}m7", name="samz", labels=("motor",))
m8 = MyEpicsMotor(f"{IOC}m8", name="m8", labels=("motor",))
m9 = MyEpicsMotor(f"{IOC}m9", name="m9", labels=("motor",))
m10 = MyEpicsMotor(f"{IOC}m10", name="v_phif", labels=("motor",))
m11 = MyEpicsMotor(f"{IOC}m11", name="v_samx", labels=("motor",))
m12 = MyEpicsMotor(f"{IOC}m12", name="v_samy", labels=("motor",))
m13 = MyEpicsMotor(f"{IOC}m13", name="v_phi_c", labels=("motor",))
m14 = MyEpicsMotor(f"{IOC}m14", name="B_StopY", labels=("motor",))
m15 = MyEpicsMotor(f"{IOC}m15", name="B_StopZ", labels=("motor",))
m16 = MyEpicsMotor(f"{IOC}m16", name="m16", labels=("motor",))


simm1 = MyEpicsMotor(f"{IOC}simm1", name="simulated m1", labels=("motor",))
simm2 = MyEpicsMotor(f"{IOC}simm2", name="simulated m2", labels=("motor",))
simm3 = MyEpicsMotor(f"{IOC}simm3", name="simulated m3", labels=("motor",))
simm4 = MyEpicsMotor(f"{IOC}simm4", name="simulated m4", labels=("motor",))
simm5 = MyEpicsMotor(f"{IOC}simm5", name="simulated m5", labels=("motor",))
simm6 = MyEpicsMotor(f"{IOC}simm6", name="simulated m6", labels=("motor",))
simm7 = MyEpicsMotor(f"{IOC}simm7", name="simulated m7", labels=("motor",))
simm8 = MyEpicsMotor(f"{IOC}simm8", name="simulated m8", labels=("motor",))

# m1.wait_for_connection()
# m1.steps_per_revolution.put(2000)
