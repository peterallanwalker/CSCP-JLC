# Licensing
# https://www.geeksforgeeks.org/how-to-encrypt-and-decrypt-strings-in-python/

import sys  # Used for exiting program if license cannot be validated (
import subprocess  # Used for reading back Windows UID from PC
from cryptography.fernet import Fernet  # Used for encrypting and decrypting the license keys

import terminal_formatter as terminal  # My file for formatting pregram header in terminal

TITLE = "Licensing"
VERSION = "0.1"


def get_host_uid():
    try:
        return subprocess.check_output('wmic csproduct get uuid').decode().split('\n')[1].strip()

    except:
        print("Licensing: Failed to read system ID")
        sys.exit()


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
        print("Licensing: failed to verify license, exiting program!")
        sys.exit()


def create_license_file(host_uid, key):
    encoded = encrypt(host_uid, key)
    try:
        with open("license", "wb") as f:  # write mode set to write bytes ("wb") rather than strings
            f.write(encoded)
    except:
        print("Licensing: Failed to create license file")


def read_license_file(file="license"):
    try:
        with open(file, "rb") as f:  # read mode set to read bytes ("rb") rather than strings
            return f.readline()
    except:
        print("Licensing: Failed to read license file, exiting program!")
        sys.exit()


def validate_license(key, file="license"):
    license = read_license_file(file)

    if get_host_uid() == decrypt(license, key):
        return True
    else:
        print("Licensing: Failed to validate license, exiting program!")
        sys.exit()


if __name__ == '__main__':

    terminal.print_heading(TITLE, VERSION, padding=8)  # Print formatted heading

    # UNIT TESTS
    print("unit tests...")
    host_uid = get_host_uid()
    print("UID for this PC:\n", host_uid)

    key = generate_key()  # Create a new encryption key
    print("\nnew key generated:", key)

    encoded = encrypt(host_uid, key)
    print("encoded with new key:", encoded)

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

    valid = validate_license(key)  # Checks if license file present and valid for host UID

    if valid:
        print("\n*** WELCOME", "You're in! ***")
    else:
        print("This machine is not licensed to run this code!")



