import json

from goecharger.goecharger import GoeCharger

charger = GoeCharger("goecharger.lan")
charger.set_forced_state(charger.SettableValueEnums.ForcedState.neutral)

status = charger.get_status(status_type=charger.STATUS_MINIMUM)

status = charger.get_status(("fna", "oem"))
print(json.dumps(status, sort_keys=True, indent=4))
