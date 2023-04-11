from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
from ..config import settings

key = bytes.fromhex(settings.secret_key)

def encrypt(plaintext):
    backend = default_backend()
    cipher = Cipher(algorithms.AES(key), modes.CBC(key[:16]), backend=backend)
    encryptor = cipher.encryptor()

    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(plaintext.encode()) + padder.finalize()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    return base64.b64encode(ciphertext).decode()

def decrypt(ciphertext):
    backend = default_backend()
    cipher = Cipher(algorithms.AES(key), modes.CBC(key[:16]), backend=backend)
    decryptor = cipher.decryptor()

    decoded_data = base64.b64decode(ciphertext.encode())
    decrypted_data = decryptor.update(decoded_data) + decryptor.finalize()

    unpadder = padding.PKCS7(128).unpadder()
    plaintext = unpadder.update(decrypted_data) + unpadder.finalize()

    return plaintext.decode()
