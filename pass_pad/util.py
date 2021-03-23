# import json
# from base64 import b64encode
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad
# from Cryptodome.Random import get_random_bytes

from binascii import a2b_hex,b2a_hex
# import json
# from base64 import b64decode
# from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import unpad

"""
    data = b"secret"
    key = get_random_bytes(16)
"""
default_iv="xc00000000000000".encode("utf-8")
def align16(key:bytes):
    if len(key) >= 16:
        return key[:16]
    else:
        return key + ( 16 - len(key) ) * b'0'

def en_real(data:bytes,key)->str:
    if data is None: return None
    key=align16(key)
    if type(data)==str:
        data=data.encode("utf-8")
    cipher = AES.new(key, AES.MODE_CBC,iv=default_iv)
    ct_bytes = cipher.encrypt(pad(data, AES.block_size))
    return ct_bytes

def en(data:bytes,key)->str:
    if data is None: return None
    ct_bytes = en_real(data,key)
    # iv = b64encode(cipher.iv).decode('utf-8')
    ciphertext = b2a_hex(ct_bytes)
    # result = json.dumps({'iv':iv, 'ciphertext':ct})
    # print("ciphertext:",ciphertext)
    return ciphertext.decode("utf-8")

def dec(ciphertext, key):
    if ciphertext is None: return None
# We assume that the key was securely shared beforehand
    # b64 = json.loads(json_input)
    # iv = b64decode(default_iv)
    ct = a2b_hex(ciphertext)
    return dec_real(ct,key)

def dec_real(ct:bytes,key)->bytes:
    if ct is None: return None
    key = align16(key)
    cipher = AES.new(key, AES.MODE_CBC, iv=default_iv)
    pt:bytes = unpad(cipher.decrypt(ct), AES.block_size)
    # print("plain text: ", pt)
    return pt



def read_entry_file(file_path:str)->bytes:
    content=[]
    with open(file_path, "rb") as f:
        byte = f.read(1); content.append(byte)
        while byte != b"":
            # Do stuff with byte.
            byte = f.read(1); content.append(byte)
        return b"".join(content)

# data = b"secret"
# key = get_random_bytes(16)

# data = "secret"
# key = b"1234567890ABCDEF"
# ciphertext_b64 = en(data,key)
# dec(ciphertext_b64,key)