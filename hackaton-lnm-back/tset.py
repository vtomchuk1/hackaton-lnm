import hashlib
import time
import secrets



passn = 'keks8953@gmail.com'

hash_object = hashlib.sha1(passn.encode())
hex_dig = hash_object.hexdigest()

print(hex_dig)

print(secrets.token_hex(8))