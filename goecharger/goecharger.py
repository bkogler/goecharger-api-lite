import json
from collections import OrderedDict
from enum import Enum
from typing import Union, Tuple, Any, Dict, Optional

import requests

from goecharger.excpetion import GoeChargerError


class GoeCharger:
    """
    Lightweight communication class for go-eCharger EV wall boxes using local HTTP API v2

    API documentation:
    https://github.com/goecharger/go-eCharger-API-v2

    Manufacturer:
    https://go-e.com
    """

    class _StatusMapper:
        """
        Internal class for mapping status to a more convenient format
        """

        __mappings_car = {
            0: "Unknown/Error",
            1: "Idle",
            2: "Charging",
            3: "WaitCar",
            4: "Complete",
            5: "Error",
        }

        __mappings_err = {
            0: None,
            1: "FiAc",
            2: "FiDc",
            3: "Phase",
            4: "Overvolt",
            5: "Overamp",
            6: "Diode",
            7: "Ppinvalid",
            8: "GndInvalid",
            9: "ContactorStuck",
            10: "ContactorMiss",
            11: "FiUnknown",
            12: "Unknown",
            13: "Overtemp",
            14: "NoComm",
            15: "StatusLockStuckOpen",
            16: "StatusLockStuckLocked",
            20: "Reserved20",
            21: "Reserved21",
            22: "Reserved22",
            23: "Reserved23",
            24: "Reserved24"
        }

        __mappings_frc = {
            0: "neutral",
            1: "off",
            2: "on"
        }

        def __init__(self, response: Dict[str, Any]):
            self.__response = response

        def map_status_response(self) -> Dict[str, Any]:
            """
            Maps a dict containing a GoeCharger status response.
            Keys, for which a mapping isn't defined, are returned unchanged.

            :return: Dict containing mapped key/value pairs
            """
            mapped_response: Dict[str, Any] = {}

            for item in self.__response.items():
                mapped_name, mapped_value = self.__map_element(item)
                mapped_response[mapped_name] = mapped_value

            return self.__order_dict(mapped_response)

        @classmethod
        def __order_dict(cls, dict_to_order: Dict[Any, Any]) -> OrderedDict[Any, Any]:
            """
            Takes a dictionary and creates an OrderedDict ordered by keys (ascending)
            :param dict_to_order:
            :return: OrderedDict
            """
            ordered_dict = OrderedDict()

            for key in sorted(dict_to_order.keys()):
                ordered_dict[key] = dict_to_order[key]

            return ordered_dict

        @classmethod
        def __map_element(cls, element: Tuple[str, Any]) -> Tuple[str, Any]:
            """
            Maps a single Tuple (key/value) into it's corresponding key/value format.
            Returns a Tuple with unchanged key/value info, if no mapping is defined.

            :param element: Tuple to be mapped
            :return:
            """

            name = element[0]
            value = element[1]

            match name:
                # car state
                case "car":
                    return "car_state", cls.__mappings_car[value]

                # error code
                case "err":
                    return "error", cls.__mappings_err[value]

                # forced state
                case "frc":
                    return "forced_state", cls.__mappings_frc[value]

                # energy array
                case "nrg":
                    return "energy", {
                        "voltage": {
                            "L1": value[0],
                            "L2": value[1],
                            "L3": value[2],
                            "N": value[3],
                        },
                        "current": {
                            "L1": value[4],
                            "L2": value[5],
                            "L3": value[6],
                        },
                        "power": {
                            "L1": value[7],
                            "L2": value[8],
                            "L3": value[9],
                            "N": value[10],
                            "total": value[11],
                        },
                        "power_factor": {
                            "L1": value[12],
                            "L2": value[13],
                            "L3": value[14],
                        }
                    }

                # device temperature
                case "tma":
                    return "temperature", sum(value)/len(value) if len(value) > 0 else None

                # no mapping specified, return unchanged value
                case _:
                    return name, value

    # full status for all elements
    STATUS_FULL: Tuple = ()

    # minimum status (state of car, error)
    STATUS_MINIMUM = (
        "car",  # car_state
        "err",  # error_code
        "frc",  # forced_state
    )

    # default status
    STATUS_DEFAULT = (
        "car",  # car_state
        "err",  # error_code
        "frc",  # forced_state
        "nrg",  # energy
        "tma",  # temperature
    )

    # forced_state
    class SettableValueEnums:
        """
        Predefined parameters which can be set on GoeCharger device
        """

        class ForcedState(Enum):
            neutral = 0
            off = 1
            on = 2

    def __init__(self, host: str, timeout: Optional[float] = 3.0) -> None:
        """
        Initialises GoeCharger connection

        :param host: hostname of GoeCharger device
        :param timeout: timeout to wait for a response from device in seconds
        """

        if host is None or host == "":
            raise ValueError("Host needs to be set")

        self.__host = host
        self.__timeout = timeout

    def __create_status_request(self, filter_elements: Union[str, Tuple[str, ...]] | None = None) -> str:
        """
        Creates URL for a status request
        :param filter_elements: If set, only these keys are requested from GoeCharger device
        :return: prepared URL
        """
        url = f"http://{self.__host}/api/status"

        if filter_elements and len(filter_elements) > 0:

            # convert str to tuple with 1 element
            if type(filter_elements) is str:
                filter_elements = (filter_elements, )

            filter_url_appendix = "?filter=" + ",".join(filter_elements)
            url += filter_url_appendix

        return url

    def __create_key_set_request(self, key: str, value: Any) -> str:
        """
        Creates URL for setting a key to a value
        :param key: Key to set
        :param value: Value to set
        :return: prepared URL
        """
        url = f"http://{self.__host}/api/set?{key}="

        # value has to be JSON encoded
        value_json = json.dumps(value, separators=(',', ':'))

        return url + value_json

    def __send_request(self, request: str) -> Dict[str, Any]:
        """
        Internal function for sending a prepared request (URL) to goeCharger device.
        Raises an GoeChargerError on any unexpected error or when local HTTP v2 API is not enabled on device
        :param request: request to be sent
        :return:
        """
        try:
            response = requests.get(request, timeout=self.__timeout)

            # extra check for 404 error --> HTTP v2 API not enabled on device
            if response.status_code == 404:
                raise GoeChargerError("HTTP API v2 not enabled on GoeCharger device. Please enable")

            response.raise_for_status()
        except requests.exceptions.RequestException:
            raise GoeChargerError("Error communicating with GoeCharger device")

        try:
            response_data = response.json()
        except requests.exceptions.JSONDecodeError:
            raise GoeChargerError("Error parsing GoeCharger JSON data")

        return response_data

    def get_status(self, status_type: str | Tuple[str, ...] = STATUS_DEFAULT) -> Dict[str, Any]:
        """
        Returns status of GoeCharger
        :param status_type: Single key name or tuple of key names to request from device.
            Several predefined Tuples are available as class variable.
            If not set, GoeCharger.STATUS_DEFAULT is used as selection
        :return:
        """
        response = self.__send_request(self.__create_status_request(status_type))
        return self._StatusMapper(response).map_status_response()

    def set_key(self, key: str, value: Any) -> Dict[str, Any]:
        """
        Low level function to generically set a key of GoeCharger device

        :param key: name of key to set
        :param value: value for key to set
        :return: Response received by device
        """
        response = self.__send_request(self.__create_key_set_request(key, value))
        return response

    def set_forced_state(self, value: SettableValueEnums.ForcedState) -> None:
        """
        Set's value for forced_state (e.g. to force stop or start a charging session for plugged-in EV)

        :param value: forced state to set
        :return:
        """
        key = "frc"
        response = self.set_key(key, value.value)

        if not response.get(key):
            raise GoeChargerError(f"Error setting forced_state, got invalid response with content '{response}'")
