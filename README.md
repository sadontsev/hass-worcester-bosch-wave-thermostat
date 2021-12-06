# WORK IN PROGRESS!
# HASS Worcester Bosch Wave thermostat 🌡

A Home Assistant Integration for the Worcester Bosch Wave Smart Thermostat.

This same codebase may also work with the NeFit thermostat.

## Installation
Not possible yet!

## Requirements
You must first connect the thermostat to the mobile companion app and set a
password for it there.

To run the integraion you will need the following values:
- A WiFi connected Worcester Bosch Wave thermostat.
- The serial number of your unit. (Printed on the back of the unit)
- The access code for the unit. (Printed on the back of the unit)
- The password you have chosen for the unit. (The one used to log in via the app)

## Local testing
The `example.py` file should be fairly explanatory.

## Contributions
Original discovery by Dr Robin Wilson, [read more here.](http://blog.rtwilson.com/hacking-the-worcester-wave-thermostat-in-python-part-1/)

Original attempts at old-style HASS conversion by [comm](https://github.com/comm) & [Chaddie](https://github.com/Chaddie).

## Known issues
- `pycrypto` is deprecated and should be replaced with `pycryptodome`
- `sleekxmpp` is deprecated and should be replaced with `slixmpp`

## Disclaimers
I am in no way affiliated with the manufacturer, everything here is based on
open source contributions and discoveries. There is no warranty, and I cannot
be held accountable for any issues.

## License
MIT
