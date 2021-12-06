import os
import time
from pprint import pprint

from wave_thermo import WaveThermostat

wave = WaveThermostat(
    serial_number=os.environ.get('WAVE_SERIAL_NUMBER'),
    access_code=os.environ.get('WAVE_ACCESS_CODE'),
    password=os.environ.get('WAVE_PASSWORD'),
)

wave.status.update()
print('Current temperature: ', wave.status.current_temp)
print('Set point temperature: ', wave.status.set_point)
print('Full status information:')
pprint(wave.status.data)

print('Setting temperature to 24 degrees')
wave.set_temperature(24)
wave.status.update()
print('Current temperature: ', wave.status.current_temp)
print('Set point temperature: ', wave.status.set_point)

print('Waiting for 5 seconds')
time.sleep(5)

print('Turning off override - so back to where we were before')
wave.override(False)
wave.status.update()
print('Current temperature: ', wave.status.current_temp)
print('Set point temperature: ', wave.status.set_point)
