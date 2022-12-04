# goecharger API (lite)
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

# Installation
`pip install goecharger-api-lite`

# Usage Examples

## Query Status
````python
from goecharger import GoeCharger

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

### Set Generic API Key (friendly name)
````python
from goecharger import GoeCharger

charger = GoeCharger("192.168.1.150") # --> change to your IP

# set generic API key (friendly name: "myEVCharger")
charger.set_key("fna", "myEVCharger")
````

### Interrupt EV charging session
````python
from goecharger import GoeCharger

charger = GoeCharger("192.168.1.150") # --> change to your IP

# STOP current charging session
charger.set_forced_state(charger.SettableValueEnums.ForcedState.off)

# restart charging session again
charger.set_forced_state(charger.SettableValueEnums.ForcedState.neutral)
````

# Links
[go-E Website (manufacturer)](https://go-e.com)

[go-E API v2 specification](https://github.com/goecharger/go-eCharger-API-v2/blob/main/introduction-en.md)

[go-E API Keys (query status, set configuration)](https://github.com/goecharger/go-eCharger-API-v2/blob/main/apikeys-en.md)