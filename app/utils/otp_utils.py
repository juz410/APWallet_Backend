import base64
import pyotp
def generate_otp(secret, interval = 300):
    secret = base64.b32encode(secret.encode('utf-8'))
    totp = pyotp.TOTP(secret, interval = interval)
    return totp.now()

def verify_otp(secret, otp, interval = 300, valid_window=1):
    secret = base64.b32encode(secret.encode('utf-8'))
    totp = pyotp.TOTP(secret, interval = interval)
    return totp.verify(otp, valid_window=valid_window)