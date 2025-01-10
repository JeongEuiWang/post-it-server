import requests

GOOGLE_OAUTH_URL = "https://oauth2.googleapis.com/tokeninfo"


def verify_google_oauth(id_token: str):
    response = request_google_auth({"id_token": id_token})
    if response.status_code == 200:
        token_info = response.json()
        return parse_google_user(token_info)
    else:
        raise Exception("Invalid Google OAuth token")


def verify_google_access(access_token: str):
    response = request_google_auth({"access_token": access_token})
    if response.status_code == 200:
        token_info = response.json()
        return parse_google_user(token_info)
    else:
        raise Exception("Invalid Google Access token")


def request_google_auth(params: dict):
    return requests.get(GOOGLE_OAUTH_URL, params=params)


def parse_google_user(token_info):
    return {
        "user_id": token_info.get("user_id"),
        "email": token_info.get("email"),
        "email_verified": token_info.get("email_verified"),
        "expires_in": token_info.get("expires_in")
    }
