# from ..config import settings
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from ..config import settings
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad,unpad

# Read the private key from the .env file
private_key_pem = settings.private_key

# Load the private key into a RsaKey object
private_key = RSA.import_key(private_key_pem)

def decrypt_secret_key(encrypted_secret_key: str) -> str:
    encrypted_data = base64.b64decode(encrypted_secret_key)
    cipher = PKCS1_OAEP.new(private_key)
    decrypted_data = cipher.decrypt(encrypted_data)
    return decrypted_data.decode('utf-8')

def decrypt_aes_encryption(encrpyted_data,key,iv):
  encrpyted_data = encrpyted_data.encode('utf-8')
  iv = iv.encode('utf-8')
  encrpyted_data = base64.b64decode(encrpyted_data)
  cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv)
  return (unpad(cipher.decrypt(encrpyted_data),16)).decode('utf-8')

def encrypt_aes_encryption(data,key,iv):
    data= pad(data.encode(),16)
    cipher = AES.new(key.encode('utf-8'),AES.MODE_CBC,iv)
    return base64.b64encode(cipher.encrypt(data))

def derive_aes_key(secret_key: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return kdf.derive(secret_key)

