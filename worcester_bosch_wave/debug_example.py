import os
import time
from pprint import pprint

from wave_thermo import WaveThermostat

# Load environment variables from .env file
def load_env_file():
    """Load environment variables from .env file"""
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value.strip('"\'')
        return True
    return False

load_env_file()

print("🔬 Debug version of Worcester Bosch Wave test")
print("=" * 50)

wave = WaveThermostat(
    serial_number=os.environ.get('WAVE_SERIAL_NUMBER'),
    access_code=os.environ.get('WAVE_ACCESS_CODE'),
    password=os.environ.get('WAVE_PASSWORD'),
)

print("🔍 Testing status update...")
wave.status.update()
print(f"Status data: {wave.status.data}")
print(f"Current temperature: {wave.status.current_temp}")
print(f"Set point temperature: {wave.status.set_point}")

if wave.status.data:
    print("\n✅ SUCCESS! We're getting thermostat data!")
    print('Full status information:')
    pprint(wave.status.data)
else:
    print("\n❌ No data received from thermostat")
    print("The XMPP connection is working but status query failed")