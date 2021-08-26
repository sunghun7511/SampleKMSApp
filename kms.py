from boto3 import client

kms = client("kms")

KEY_SPEC = "AES_256"


def generate_key(cmk_id):
    response = kms.generate_data_key(KeyId=cmk_id, KeySpec=KEY_SPEC)
    return response['CiphertextBlob'], response['Plaintext']


def decrypt_key(encrypted_key):
    response = kms.decrypt(CiphertextBlob=encrypted_key)
    return response['Plaintext']
