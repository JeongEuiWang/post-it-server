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


def find_message_content_html(message_payload) -> str | None:
    message_parts = message_payload["parts"]
    if not message_parts or len(message_parts) == 0:
        # parts가 존재하지 않을 경우
        message_body = message_payload["body"]
        if len(message_body["data"]) == 0:
            return None
        return message_body["data"]
    html_parts = next((part["body"]["data"] for part in message_parts if "html" in part.get("mimeType")), None)
    return html_parts
