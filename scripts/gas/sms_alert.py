from twilio.rest import Client

def send_sms_alert(message, to_phone):
    account_sid = "your_account_sid"         # Your Twilio account SID
    auth_token = "your_auth_token"           # Your Twilio auth token
    client = Client(account_sid, auth_token)
    from_phone = "+1234567890"               # Your Twilio phone number (in E.164 format)
    
    try:
        sms = client.messages.create(
            body=message,
            from_=from_phone,
            to=to_phone
        )
        print(f"SMS alert sent successfully, SID: {sms.sid}")
    except Exception as e:
        print(f"Failed to send SMS: {e}")
