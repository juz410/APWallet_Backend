from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, PublicFormat, NoEncryption
from dotenv import load_dotenv, set_key
import os

load_dotenv()

def generate_rsa_key_pair():
    # Check if the keys already exist
    existing_private_key = os.getenv("PRIVATE_KEY")
    existing_public_key = os.getenv("PUBLIC_KEY")

    if existing_private_key and existing_public_key:
        print("RSA key pair already exists.")
        return

    # Generate the private key
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    # Serialize the private key
    private_pem = private_key.private_bytes(encoding=Encoding.PEM, format=PrivateFormat.PKCS8, encryption_algorithm=NoEncryption())

    # Generate the public key
    public_key = private_key.public_key()
    # Serialize the public key
    public_pem = public_key.public_bytes(encoding=Encoding.PEM, format=PublicFormat.SubjectPublicKeyInfo)

    # Save the keys to the .env file
    private_pem_str = private_pem.decode('utf-8')
    public_pem_str = public_pem.decode('utf-8')
    set_key(".env", "PRIVATE_KEY", private_pem_str)
    set_key(".env", "PUBLIC_KEY", public_pem_str)
    print("New RSA key pair generated and saved to .env file.")


generate_rsa_key_pair()
