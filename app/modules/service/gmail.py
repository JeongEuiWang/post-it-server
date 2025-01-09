from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


def create_gmail_service(access_token: str):
    try:
        credentials = Credentials(token=access_token)
        service = build('gmail', 'v1', credentials=credentials)
        return service
    except Exception as e:
        raise HTTPException(status_code=400, detail="Fail to create gmail service")
