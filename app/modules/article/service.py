import pandas as pd


def parse_base_message_service(message):
    headers = message["payload"]["headers"]
    date = message["internalDate"]
    utc_date = pd.to_datetime(float(date), unit='ms', utc=True)
    kst_date = utc_date.tz_convert("Asia/Seoul").date()
    payload = {
        "title": next((header["value"] for header in headers if header.get("name") == "Subject"), "-"),
        "snippet": message["snippet"] or "-",
        "date": kst_date.isoformat(),
        "message_id": message["id"]
    }
    return payload

