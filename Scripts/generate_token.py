import datetime
import os

import jwt


def generate_password_reset_token(username, password):
    key = os.environ.get("KRK_APP_SECRET_KEY")
    print(key)
    #Set time this token is valid
    delta = datetime.timedelta(hours=48)
    now = datetime.datetime.utcnow()
    expires = now + delta
    exp = expires.timestamp()
    #Encode token
    encoded_jwt = jwt.encode(
        {
            "exp": exp,
            "nbf": now,
            "username": username,
            "pwd": password
        },
        key,
        algorithm="HS256",
    )

    return encoded_jwt
