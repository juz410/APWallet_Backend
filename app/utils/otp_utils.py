import pyotp
def generate_otp(secret):
    totp = pyotp.TOTP(secret)
    return totp.now()

def verify_otp(secret, otp):
    totp = pyotp.TOTP(secret)
    return totp.verify(otp)