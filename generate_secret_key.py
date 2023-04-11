import os
import secrets
from dotenv import load_dotenv

load_dotenv()

key = os.getenv('SECRET_KEY')

if key is None:
    key = secrets.token_bytes(32)
    with open('.env', 'a') as env_file:
        env_file.write(f"SECRET_KEY={key.hex()}\n")
    os.environ['SECRET_KEY'] = key.hex()
else:
    key = bytes.fromhex(key)
