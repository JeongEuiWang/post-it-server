def validate_header(authorization: str = None):
    if authorization is None:
        raise Exception("Authorization header missing")
    if not authorization.startswith("Bearer "):
        raise Exception("Invalid Authorization header format")
