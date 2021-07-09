# encryption & decryption,
# written for handling Windows PC UIDs for license keys
# ref: https://www.geeksforgeeks.org/how-to-encrypt-and-decrypt-strings-in-python/

from cryptography.fernet import Fernet

TITLE = "Encryption / Decryption"
VERSION = "0.1"


def get_key():
    # generate a key for encryption and decryption
    # You can use fernet to generate
    # the key or use random key generator
    # here I'm using fernet to generate key
    return Fernet.generate_key()


def encode(message, key):
    # Instance the Fernet class with the key
    fernet = Fernet(key)

    # then use the Fernet class instance
    # to encrypt the string string must
    # be encoded to byte string before encryption
    return fernet.encrypt(message.encode())


def decode(message, key):
    # Instance the Fernet class with the key
    fernet = Fernet(key)
    return fernet.decrypt(message).decode()


if __name__ == '__main__':
    print(2 * "\n", 30 * "#", "\n   {}, V{}".format(TITLE, VERSION), "\n", 30 * "-", sep="")
    test = "hello"
    key = get_key()
    encoded = encode(test, key)
    print(encoded)
    decoded = decode(encoded, key)
    print(decoded)
