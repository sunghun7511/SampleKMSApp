from boto3 import client

from encryption import encrypt_aes, decrypt_aes

kms = client("kms")

KEY_SPEC = "AES_256"
LENGTH_BYTES = 2


def generate_key(cmk_id):
    response = kms.generate_data_key(KeyId=cmk_id, KeySpec=KEY_SPEC)
    return response['CiphertextBlob'], response['Plaintext']


def decrypt_key(encrypted_key):
    response = kms.decrypt(CiphertextBlob=encrypted_key)
    return response['Plaintext']


def encrypt(cmk_id, bytes):
    encrypted_key, key = generate_key(cmk_id)
    data = encrypt_aes(key, bytes)

    return len(encrypted_key).to_bytes(LENGTH_BYTES, "little") + encrypted_key + data


def decrypt(encrypted):
    key_size = int.from_bytes(encrypted[:LENGTH_BYTES], "little")
    key = decrypt_key(encrypted[LENGTH_BYTES:LENGTH_BYTES+key_size])
    return decrypt_aes(key, encrypted[LENGTH_BYTES+key_size:])
