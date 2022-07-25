import os
import jwt
import datetime


def generate_password_reset_token(username,password):
    key = os.environ.get("KRK_APP_SECRET_KEY")
    print(key)
    delta = datetime.timedelta(hours=1)
    now = datetime.datetime.utcnow()
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {
            "exp": exp,
            "nbf": now,
            "username": username,
            "pwd":password
        },
        key,
        algorithm="HS256",
    )
    
    return encoded_jwt 