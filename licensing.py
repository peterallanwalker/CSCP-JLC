# Licensing
# https://www.geeksforgeeks.org/how-to-encrypt-and-decrypt-strings-in-python/

import sys  # Used for exiting program if license cannot be validated
import glob  # Used for searching for files by their extension
from pathlib import Path  # Used to get current directory
import subprocess  # Used for reading back Windows UID from PC
from cryptography.fernet import Fernet  # Used for encrypting and decrypting the license keys

import terminal_formatter as terminal  # My file for formatting program header in terminal

TITLE = "Licensing"
VERSION = "0.2"

# Private key for license CAL-JLC encoding & decoding - ** DO NOT MAKE THIS SOURCE CODE PUBLIC! **
KEY = b'edj9nzeY0aEKtVZjE_aCZbak2dUz_ULcsaCUA4krbIg='


# Version 0.2
# License files generated as <host uid>.license
# (so users can identify which license file is for which machine)
# Licenses searched for by .license extension
# (so users can rename license files as long as the maintain the extension)
# Supports multiple .license files being within the folder, will check each until a valid one found

# Version 0.3
# Read system/customer name from second line of license file


def get_host_uid():
    try:
        return subprocess.check_output('wmic csproduct get uuid').decode().split('\n')[1].strip()

    except:
        print("Licensing: Failed to read system ID, cannot validate license")
        #sys.exit()
        return None


def generate_key():
    # generate a key for encryption and decryption
    # You can use fernet to generate
    # the key or use random key generator
    # here I'm using fernet to generate key

    return Fernet.generate_key()


def encrypt(message, key):
    # Instance the Fernet class with the key
    fernet = Fernet(key)

    # then use the Fernet class instance
    # to encrypt the string string must must
    # be encoded to byte string before encryption
    return fernet.encrypt(message.encode())


def decrypt(encMessage, key):
    # Instance the Fernet class with the key
    fernet = Fernet(key)

    # decrypt the encrypted string with the
    # Fernet instance of the key,
    # that was used for encrypting the string
    # encoded byte string is returned by decrypt method,
    # so decode it to string with decode methos
    try:
        return fernet.decrypt(encMessage).decode()
    except:
        return "invalid"


def create_license_file(host_uid, key, customer_reference="Customer Name", system_reference="System"):
    encoded = encrypt(host_uid, key)
    filename = "{}-{}-{}.license".format(customer_reference, system_reference, host_uid)
    try:
        with open(filename, "wb") as f:  # write mode set to write bytes ("wb") rather than strings
            f.write(encoded)
            f.write(str.encode("\n" + customer_reference))
            f.write(str.encode("\n" + system_reference))
            print("Licensing: Created license file {} in {}".format(filename, Path.cwd()))
    except:
        print("Licensing: Failed to create license file")


def read_license_file(file):

    try:
        with open(file, "rb") as f:  # read mode set to read bytes ("rb") rather than strings
            return f.readlines()
    except:
        return None


def validate_license(key):

    # Get a list of files in the current folder that have the relevant extension
    license_files = glob.glob('*.license')

    for file in license_files:
        # Get first line of test from file
        contents = read_license_file(file)
        license = contents[0]
        # Check if license can be decrypted to match the host machine's UID
        if license and get_host_uid() == decrypt(license, key):
            customer_name = contents[1].decode().strip()
            system = contents[2].decode()
            return customer_name, system

    #print("Licensing: Failed to find a valid license, exiting program!")
    #sys.exit()
    return False


if __name__ == '__main__':

    terminal.print_heading(TITLE, VERSION, padding=8)  # Print formatted heading

    # UNIT TESTS
    print("unit tests...")
    host_uid = get_host_uid()
    print("UID for this PC:\n", host_uid)

    key = generate_key()  # Create a new encryption key
    print("\nnew key generated:", key)

    encoded = encrypt(host_uid, key)
    print("UID encoded with new key:", encoded)

    decoded = decrypt(encoded, key)
    print("decoded with new key:", decoded)

    # TYPICAL USAGE
    # To decode, the key used for encryption must be known.
    # ... This private key must be kept secret
    #       DO NOT MAKE SOURCE CODE PUBLIC IF IT CONTAINS A HARD-CODED KEY!  # TODO - best practise?
    key = b'edj9nzeY0aEKtVZjE_aCZbak2dUz_ULcsaCUA4krbIg='

    # CREATING A LICENSE FILE
    # Give the customer an exe that calls get_host_uid()
    # Get them to send their uid via email
    # Call the following to create a license file for the customers machine:
    create_license_file(host_uid, key)

    # CHECK FOR LICENSE FILES AND VALIDATE AGAINST THE HOST MACHINE'S UID
    valid = validate_license(key)
    print("VALID=", valid)
    if valid:
        print("\n*** WELCOME {}, {}".format(valid[0], valid[1]), "You're in! ***")
    else:
        print("\nThis machine is not licensed to run this code!")
        sys.exit()

