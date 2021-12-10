import SoapySDR

args = dict(driver="lime")
sdr = SoapySDR.Device(args)
del sdr