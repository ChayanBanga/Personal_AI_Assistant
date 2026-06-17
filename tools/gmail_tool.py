import os
import base64
import email as email_lib
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify'
]

def get_gmail_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = Flow.from_client_secrets_file(
                'credentials.json',
                scopes=SCOPES,
                redirect_uri='urn:ietf:wg:oauth:2.0:oob'
            )
            auth_url, _ = flow.authorization_url(prompt='consent')
            print(f"\nOpen this URL in browser:\n{auth_url}\n")
            code = input("Paste the authorization code here: ")
            flow.fetch_token(code=code)
            creds = flow.credentials
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def get_body(payload):
    body = ""
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                data = part['body'].get('data', '')
                if data:
                    body = base64.urlsafe_b64decode(data).decode('utf-8')
                    break
    elif 'body' in payload:
        data = payload['body'].get('data', '')
        if data:
            body = base64.urlsafe_b64decode(data).decode('utf-8')
    return body[:1000] if body else "No body content"

# Tool 1 - get latest emails
def get_latest_emails(max_results: int = 5) -> str:
    service = get_gmail_service()
    results = service.users().messages().list(userId='me', maxResults=max_results).execute()
    messages = results.get('messages', [])
    if not messages:
        return "No emails found."
    output = ""
    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
        headers = msg_data['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
        date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')
        body = get_body(msg_data['payload'])
        output += f"ID: {msg['id']}\nFrom: {sender}\nSubject: {subject}\nDate: {date}\nBody: {body}\n"
        output += "-"*40 + "\n\n"
    return output

# Tool 2 - search emails
def search_emails(query: str, max_results: int = 5) -> str:
    service = get_gmail_service()
    results = service.users().messages().list(userId='me', q=query, maxResults=max_results).execute()
    messages = results.get('messages', [])
    if not messages:
        return f"No emails found for query: {query}"
    output = f"Search results for '{query}':\n\n"
    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
        headers = msg_data['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
        date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')
        body = get_body(msg_data['payload'])
        output += f"ID: {msg['id']}\nFrom: {sender}\nSubject: {subject}\nDate: {date}\nBody: {body}\n"
        output += "-"*40 + "\n\n"
    return output

# Tool 3 - read specific email by ID
def read_email(email_id: str) -> str:
    service = get_gmail_service()
    msg_data = service.users().messages().get(userId='me', id=email_id, format='full').execute()
    headers = msg_data['payload']['headers']
    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
    sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
    date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')
    body = get_body(msg_data['payload'])
    return f"From: {sender}\nSubject: {subject}\nDate: {date}\n\nBody:\n{body}"

# Tool 4 - send email
def send_email(to: str, subject: str, body: str) -> str:
    service = get_gmail_service()
    message = MIMEText(body)
    message['to'] = to
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    service.users().messages().send(userId='me', body={'raw': raw}).execute()
    return f"✅ Email sent to {to} with subject '{subject}'"

# Tool 5 - reply to email
def reply_to_email(email_id: str, reply_body: str) -> str:
    service = get_gmail_service()
    original = service.users().messages().get(userId='me', id=email_id, format='full').execute()
    headers = original['payload']['headers']
    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
    sender = next((h['value'] for h in headers if h['name'] == 'From'), '')
    thread_id = original['threadId']
    message = MIMEText(reply_body)
    message['to'] = sender
    message['subject'] = f"Re: {subject}"
    message['In-Reply-To'] = email_id
    message['References'] = email_id
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    service.users().messages().send(
        userId='me',
        body={'raw': raw, 'threadId': thread_id}
    ).execute()
    return f"✅ Reply sent to {sender}"