# [goecharger API (lite)](https://github.com/bkogler/goecharger-api-lite)
Lightweight Python API for accessing modern go-eCharger EV wallboxes using local HTTP API v2

[go-eCharger](https://go-e.com) models:
* Gemini
* Gemini flex
* HOMEfix
* HOME+

# Table of contents
<!-- TOC -->
* [Features](#features)
* [Installation](#installation)
* [Usage Examples](#usage-examples)
  * [Query Status](#query-status)
    * [Pretty Print Status](#pretty-print-status)
  * [Set Configuration](#set-configuration)
* [Links](#links)
<!-- TOC -->

# Features
* Query Charger Status
* Set Charger Configuration
* Uses asynchronous aiohttp requests for communication

# Installation
`pip install goecharger-api-lite`

# Usage Examples

## Query Status
````python
from goecharger_api_lite import GoeCharger

charger = GoeCharger("192.168.1.150") # --> change to your IP

# get full status
status = charger.get_status(status_type=GoeCharger.STATUS_FULL)

# essential status (car state, wallbox state, wallbox error)
status = charger.get_status(status_type=GoeCharger.STATUS_MINIMUM)

# status for custom API keys (friendly name, OEM manufacturer) 
status = charger.get_status(("fna", "oem"))
````

#### Hint: Pretty Print Status
````python
import json

print(json.dumps(status, indent=4))
````
````
{
    "fna": "myEVCharger",
    "oem": "go-e"
}
````

## Set Configuration

### Interrupt and restart EV charging session
````python
from goecharger_api_lite import GoeCharger

charger = GoeCharger("192.168.1.150") # --> change to your IP

# STOP current charging session
charger.set_charging_mode(charger.SettableValueEnums.ChargingMode.off)

# restart charging session again
charger.set_charging_mode(charger.SettableValueEnums.ChargingMode.neutral)
````

### Set charge rate (ampere) and number of phases
````python
from goecharger_api_lite import GoeCharger

charger = GoeCharger("192.168.1.150") # --> change to your IP

# set to 1 phase, 13 ampere
charger.set_phase_mode(charger.SettableValueEnum.PhaseMode.one)
charger.set_ampere(13)

# set to 3 phases, 16 ampere
charger.set_phase_mode(charger.SettableValueEnum.PhaseMode.three)
charger.set_ampere(16)

# set phase mode to auto
charger.set_phase_mode(charger.SettableValueEnum.PhaseMode.auto)

# set maximum possible charge rate of the charger (ampere)
# this will limit the maximum charge rate that can be set by the user, i.e. via the app
charger.set_absolute_max_current(10)
````

### Set cable lock mode
````python
from goecharger_api_lite import GoeCharger

charger = GoeCharger("192.168.1.150") # --> change to your IP

# set to require unlocking the car first
charger.set_cable_lock_mode(charger.SettableValueEnum.CableLockMode.unlockcarfirst)

# set to automatically unlock after charging
charger.set_cable_lock_mode(charger.SettableValueEnum.CableLockMode.automatic)

# set to always lock the cable
charger.set_cable_lock_mode(charger.SettableValueEnum.CableLockMode.locked)
````

### Set charge limit
````python
from goecharger_api_lite import GoeCharger

charger = GoeCharger("192.168.1.150") # --> change to your IP

# set charge limit to 2.5 kWh
charger.set_charge_limit(2500)

# Disable charge limit
charger.set_charge_limit(None)
````

### Set Generic API Key
````python
from goecharger_api_lite import GoeCharger

charger = GoeCharger("192.168.1.150") # --> change to your IP

# set generic API key (friendly name: "myEVCharger")
charger.set_key("fna", "myEVCharger")
````

# Links
[goecharger-api-lite GitHub repository](https://github.com/bkogler/goecharger-api-lite)

[goecharger-api-lite on Pypi](https://pypi.org/project/goecharger-api-lite)

[go-E Website (manufacturer)](https://go-e.com)

[go-E API v2 specification](https://github.com/goecharger/go-eCharger-API-v2/blob/main/introduction-en.md)

[go-E API Keys (query status, set configuration)](https://github.com/goecharger/go-eCharger-API-v2/blob/main/apikeys-en.md)
