import requests

GOOGLE_OAUTH_URL = "https://oauth2.googleapis.com/tokeninfo"


def verify_google_oauth(id_token: str) -> dict:
    response = requests.get(GOOGLE_OAUTH_URL, params={"id_token": id_token})
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Invalid Google OAuth token")
