import json

from goecharger_api_lite.goecharger_api_lite import GoeCharger

charger = GoeCharger("goecharger.lan")

status = charger.get_status(status_type=charger.STATUS_MINIMUM)
status = charger.get_status(("fna", "oem"))

status = charger.get_status(status_type=charger.STATUS_DEFAULT)
print(json.dumps(status, sort_keys=True, indent=4))

charger.set_phase_mode(charger.SettableValueEnum.PhaseMode.three)
charger.set_ampere(16)

charger.set_charging_mode(charger.SettableValueEnum.ChargingMode.neutral)

status = charger.get_ampere()
print(json.dumps(status, sort_keys=True, indent=4))

status = charger.get_phase_mode()
print(json.dumps(status, sort_keys=True, indent=4))