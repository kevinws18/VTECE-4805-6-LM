# AUTHOR: STEPHAN MULLER
# OWNER: VIRGINIA TECH/LOCKHEED MARTIN

import SoapySDR

args = dict(driver="lime")
sdr = SoapySDR.Device(args)
del sdr