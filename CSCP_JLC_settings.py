# CSCP_JLC_settings
# Used by the CSCP-JLC application.

# Handles loading and saving of connection configuration settings to/from json file
# Gets user confirmation and allows user to edit the settings.
# Copyright Peter Walker 2021.

import json

CONFIG_FILE = "settings.json"


# THESE FIRST FUNCTIONS ARE INTENDED FOR PRIVATE USE,
# THEY ARE CALLED BY THE PUBLIC FUNCTIONS FURTHER BELOW
def _yes_or_no(string, enter=False, edit=False):
    """
    For parsing cmd line input from user - yes/no prompts
    if string is 'y' or 'yes', case-insensitive, returns 'y'
    if string is 'n' or 'no', case-insensitive, returns 'n'
    else, returns False
    :param string: typically, user input('y/n?')
    :param enter: optional, if enter=True, when string is empty (Enter key alone), returns 'y'
    :param edit: optional, if edit=True, when string is 'e'/'E', return 'n'
    :return: 'y' for affirmative response/acceptance, 'n' for negative response or edit, False for invalid response
    """
    string = string.lower().strip()

    if string in ("y", "yes") or (string == "" and enter):
        return "y"
    elif string in ("n", "no") or (string == "e" and edit):
        return "n"
    else:
        return False


def _validate_ip_address(address):
    """
    Checks if input is a valid IPv4 address
    :param address: string
    :return: True if valid IPv4 address, else False
    """
    address = address.split(".")

    if len(address) != 4:
        return False

    for segment in address:
        try:
            segment = int(segment)
        except ValueError:
            return False

        if segment not in range(255):
            return False

    return True


def _load_settings():
    """
    Check if configuration file exists
    :return: Dict of settings (returns defaults if none saved)
    """
    try:
        with open(CONFIG_FILE, "r") as config:
            # TODO - Should really validate the settings file rather than blindly loading it
            r = json.load(config)

    except FileNotFoundError:
        print("'{}' file not found. Enter a few details to get started...\n".format(CONFIG_FILE))
        r = False

    except json.decoder.JSONDecodeError:
        print("'{}' file is invalid. Enter a few details to get started...\n".format(CONFIG_FILE))
        r = False

    if not r:
        r = {
             "Mixer IP Address": None,
             "Mixer CSCP Port": None,
             "JLC IP Address": None,
             "JLC Port": None,
             "Mixer Faders": (0, 1, 2, 3, 4, 5, 6, 7),
             "Two-Way Fader Control": True,
             }
    return r


def _ask_ip_address(device):
    """
    Asks user to input an IP address
    Checks input is a valid IP address, keeps asking until it is
    :return: string - user inputted IP address
    """
    valid = False
    while not valid:
        ip_address = input("Enter {} IP address: ".format(device))
        if _validate_ip_address(ip_address):
            return ip_address


def _ask_port(device):
    """
    Asks user for a TCP port value,
    Keeps asking until they input a number in range 0 - 65,000
    :return:
    """
    valid = False
    while not valid:
        port = input("Enter {} CSCP port: ".format(device))
        try:
            port = int(port)
            if port in range(65000):
                return port
        except ValueError:
            pass


def _ask_two_way():
    if input("Enable two-way fader control? (y/n): ").lower() == "y":
        return True
    else:
        return False


def _ask_faders():
    r = []
    for f in range(8):
        r.append(int(input("JLC fader {} controls mixer fader: ".format(f+1))) - 1)
    return r


def _print_faders(config):
    print("\t", "CSCP Mixer Faders : ", end='')
    for fader in config["Mixer Faders"]:
        print(fader+1, end=', ')

    print("\n")


def _confirm_settings(config):
    """
    Ask user if they want to keep the last used settings or enter new ones
    :return: Dict of user confirmed settings
    """
    use_settings = False

    # Present last used settings and ask to confirm or update
    while not use_settings:
        print("  Current Connection Settings:")
        for heading in config:
            if heading == "Mixer Faders":
                _print_faders(config)
            else:
                print("\t", heading, ":", config[heading])

        use_settings = _yes_or_no(input("\nUse these settings? (y/n): "), enter=True)

    if use_settings == "n":
        # User does not want to keep last used settings, so get their input for new settings
        config["Mixer IP Address"] = _ask_ip_address("Mixer")
        config["Mixer CSCP Port"] = _ask_port("Mixer")
        config["JLC IP Address"] = _ask_ip_address("JLC")
        config["JLC Port"] = _ask_port("JLC")
        config["Mixer Faders"] = _ask_faders()
        config["Two-Way Fader Control"] = _ask_two_way()

    return config


# THE FOLLOWING FUNCTIONS ARE INTENDED AS PUBLIC / TO BE CALLED FROM OTHER APPLICATION
def get_settings():
    """
    Loads CSCP-MIDI settings & gets user to confirm or edit
    :return: dict of user confirmed settings
    """
    r = _load_settings()
    r = _confirm_settings(r)
    return r


def load_settings():
    """
    Requested by DB/ITN, load settings without prompting to confirm
    :return: dict of connection settings loaded from json file
    """
    return _load_settings()


def save_settings(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)


if __name__ == '__main__':
    print("\n", 23 * "-", "\n   CSCP-JLC Settings   \n", 23 * "-")
    settings = get_settings()
    save_settings(settings)

    for setting in settings:
        print(setting, ":", settings[setting])
