from base64 import b64decode, b64encode
from os import urandom

from Crypto.Cipher import AES

BLOCK_SIZE = AES.block_size


def _pad(n):
    pad_size = BLOCK_SIZE - len(n) % BLOCK_SIZE
    return n + pad_size * chr(pad_size).encode()


def _unpad(n):
    return n[: -ord(n[len(n) - 1:])]


def encrypt_aes(key, data):
    iv = urandom(AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return b64encode(iv + cipher.encrypt(_pad(data)))


def decrypt_aes(key, data):
    enc = b64decode(data)
    iv = enc[: AES.block_size]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return _unpad(cipher.decrypt(enc[AES.block_size:]))
