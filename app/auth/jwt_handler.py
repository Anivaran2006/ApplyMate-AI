from datetime import datetime, timedelta
import os

from jose import jwt, JWTError
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


# ---------------- CREATE TOKEN ----------------

from datetime import datetime, timedelta, timezone

def create_access_token(data: dict):

    to_encode = data.copy()

    now = datetime.now(timezone.utc)
    expire = now + timedelta(hours=24)

    print("NOW:", now)
    print("EXPIRE:", expire)

    to_encode.update({"exp": expire})

    token = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    print("NEW TOKEN:", token)

    return token

# ---------------- VERIFY TOKEN ----------------
def verify_access_token(token: str):

    print("SECRET_KEY =", SECRET_KEY)
    print("ALGORITHM =", ALGORITHM)
    print("TOKEN =", token)

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        print("PAYLOAD =", payload)

        return payload

    except JWTError as e:
        print("JWT ERROR =", str(e))
        return None