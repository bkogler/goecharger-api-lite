import inspect
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

        __mappings_psm = {
            0: "auto",
            1: "one",
            2: "three"
        }

        __mappings_var = {
            11: "11KW/16A",
            22: "22KW/32A"
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

                # ampere (currently possible rate)
                case "acu":
                    return "ampere", value

                # ampere (device maximum)
                case "ama":
                    return "ampere_device_maximum", value

                # ampere (allowed rate)
                case "amp":
                    return "ampere_allowed", value

                # car state
                case "car":
                    return "car_state", cls.__mappings_car[value]

                # error code
                case "err":
                    return "error", cls.__mappings_err[value]

                # forced state
                case "frc":
                    return "charging_mode", cls.__mappings_frc[value]

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

                # phase_mode
                case "psm":
                    return "phase_mode", cls.__mappings_psm[value]

                # device temperature
                case "tma":
                    return "temperature", sum(value)/len(value) if len(value) > 0 else None

                # device model (11KW / 22KW)
                case "var":
                    return "device_model", cls.__mappings_var[value]

                # no mapping specified, return unchanged value
                case _:
                    return name, value

    # full status for all elements
    STATUS_FULL: Tuple = ()

    # minimum status (state of car, error)
    STATUS_MINIMUM = (
        "car",  # car_state
        "err",  # error_code
        "frc",  # charging_mode
    )

    # default status
    STATUS_DEFAULT = (
        "acu",  # ampere
        "car",  # car_state
        "err",  # error_code
        "frc",  # charging_mode
        "nrg",  # energy
        "psm",  # phase_mode
        "tma",  # temperature
        "var",  # device_model
    )

    class SettableValueEnum:
        """
        Predefined parameters which can be set on GoeCharger device
        """

        class ChargingMode(Enum):
            neutral = 0
            off = 1
            on = 2

        class PhaseMode(Enum):
            one = 1
            three = 2

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

        self.__device_model = ""

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

    def __send_request(self, request: str, ignore_server_error: bool = False) -> Dict[str, Any]:
        """
        Internal function for sending a prepared request (URL) to goeCharger device.
        Raises an GoeChargerError on any unexpected error or when local HTTP v2 API is not enabled on device
        :param request: request to be sent
        :param ignore_server_error: if set, don't raise a GoeChargerError on HTTP error 500 (useful when setting
                                     api keys)
        :return:
        """
        try:
            response = requests.get(request, timeout=self.__timeout)

            # extra check for 404 error --> HTTP v2 API not enabled on device
            if response.status_code == 404:
                raise GoeChargerError("HTTP API v2 not enabled on GoeCharger device. Please enable")

            # don't raise GoeChargerError on status_code 500, if so requested
            if response.status_code != 500 and not ignore_server_error:
                response.raise_for_status()

        except requests.exceptions.RequestException as e:
            raise GoeChargerError("Error communicating with GoeCharger device") from e

        try:
            response_data = response.json()
        except requests.exceptions.JSONDecodeError as e:
            raise GoeChargerError("Error parsing GoeCharger JSON data") from e

        return response_data

    def __get_status(self, status_type: str | Tuple[str, ...]) -> Dict[str, Any]:
        """
        Internal method for getting status info from GoeCharger device

        :param status_type: Single key name or tuple of key names to request from device.
        :return:
        """
        response = self.__send_request(self.__create_status_request(status_type))
        return self._StatusMapper(response).map_status_response()

    def __set_key(self, key: str, value: Any) -> None:
        """
        Internal method for setting keys on GoeCharger device

        :param key: key to set
        :param key: value for key to set
        """
        response = self.__send_request(self.__create_key_set_request(key, value), ignore_server_error=True)

        if response is None or response.get(key) is not True:
            stack_info = inspect.stack()
            caller_method_name = stack_info[1][3]

            # call from generic set_key method: print name of key in Error
            if caller_method_name == "set_key":
                error_message_setting_name = key

            # call from a shortcut method: print name of shortcut-method in Error
            else:
                key_name = caller_method_name[4:]
                error_message_setting_name = key_name

            raise GoeChargerError(f"Error setting '{error_message_setting_name}', got invalid response: '{response}'")

    def get_status(self, status_type: str | Tuple[str, ...] = STATUS_DEFAULT) -> Dict[str, Any]:
        """
        Returns status of GoeCharger
        :param status_type: Single key name or tuple of key names to request from device.
            Several predefined Tuples are available as class variable.
            If not set, GoeCharger.STATUS_DEFAULT is used as selection
        :return:
        """
        return self.__get_status(status_type)

    def get_ampere(self) -> Dict[str, int]:
        """
        Returns maximum current setting for car in Ampere
        :return:
        """
        return self.__get_status("amp")

    def get_charging_mode(self) -> Dict[str, int]:
        """
        Returns currently active charging mode for GoeCharger device

        :return:
        """
        return self.__get_status("frc")

    def get_phase_mode(self) -> Dict[str, SettableValueEnum.PhaseMode]:
        """
        Returns phase mode of GoeCharger device (1 phase / 3 phases / neutral)
        """
        return self.__get_status("psm")

    def set_key(self, key: str, value: Any) -> None:
        """
        Generic (low-level) function for setting a GoeCharger key to a value.
        For possible keys see official API documentation for device

        :param key: name of key to set
        :param value: value for key to set
        :return: Response received by device
        """
        self.__set_key(key, value)

    def set_ampere(self, value: int | str) -> None:
        """
        Sets maximum current setting for car in Ampere

        :param value: integer value between 6 and ampere_device_maximum (16 / 32)
        :return:
        """

        # check data type of parameter
        if not isinstance(value, int):
            try:
                value = int(value)
            except ValueError:
                raise GoeChargerError("Ampere value needs to be an integer")

        if not self.__device_model:
            self.__device_model = self.get_status("var")["device_model"]

        # check for 32A values on 16A devices
        if self.__device_model.find("11") != -1 and value > 16:
            raise GoeChargerError(
                f"Ampere value of '{value}' too big for charger device_model '{self.__device_model}'")

        # set value
        self.__set_key("amp", value)

    def set_charging_mode(self, value: SettableValueEnum.ChargingMode) -> None:
        """
        Sets value for charging_mode (e.g. to force stop or start a charging session for plugged-in EV)

        :param value: charging_mode to set
        :return:
        """
        self.__set_key("frc", value.value)

    def set_phase_mode(self, value: SettableValueEnum.PhaseMode) -> None:
        """
        Sets phase mode to 1 or 3 phase(s)

        :param value: phase mode to set
        :return:
        """
        self.__set_key("psm", value.value)
