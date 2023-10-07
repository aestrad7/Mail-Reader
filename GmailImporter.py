import base64
import os
import re
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dateutil import parser

class GmailImporter:
    def __init__(self, credentials_path, token_path):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = self.get_gmail_service()

    def get_gmail_service(self):
        creds = None
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, ['https://www.googleapis.com/auth/gmail.readonly'])
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, ['https://www.googleapis.com/auth/gmail.readonly'])
                creds = flow.run_local_server(port=0)
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
        service = build('gmail', 'v1', credentials=creds)
        return service

    def get_messages(self, n_days):
        query = f'after:{(datetime.utcnow() - timedelta(days=n_days)).strftime("%Y/%m/%d")}'
        results = self.service.users().messages().list(userId='me', q=query).execute()
        messages = results.get('messages', [])
        return messages

    def process_message(self, message_id):
        msg = self.service.users().messages().get(userId='me', id=message_id).execute()
        email_data = {
            'from': '',
            'to': '',
            'subject': '',
            'date': '',
            'body': ''
        }
        headers = msg['payload']['headers']
        for header in headers:
            name = header['name']
            if name == 'From':
                email_data['from'] = header['value']
            if name == 'To':
                email_data['to'] = header['value']
            if name == 'Subject':
                email_data['subject'] = header['value']
            if name == 'Date':
                email_data['date'] = header['value']
        body = msg['payload'].get('body', {}).get('data', '')
        if body == '':
            body = msg['payload'].get('parts', [{}])[0].get('body', {}).get('data', '')
        if body != '':
            body = base64.urlsafe_b64decode(body).decode('utf-8')
            body = re.sub(r'<.*?>', '', body)  # Remove HTML tags
        email_data['body'] = body
        return email_data

    def save_messages(self, n_days):
        messages = self.get_messages(n_days)
        file_name = f'{datetime.utcnow().strftime("%Y-%m-%d")}_lag_{n_days}_dias.txt'
        with open(file_name, 'w', encoding='utf-8') as file:
            for message in messages:
                email_data = self.process_message(message['id'])
                file.write(f"From: {email_data['from']}\n")
                file.write(f"To: {email_data['to']}\n")
                file.write(f"Subject: {email_data['subject']}\n")
                file.write(f"Date: {email_data['date']}\n")
                file.write(f"Body:\n{email_data['body']}\n")
                file.write("\n####################################################\n")

