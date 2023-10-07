import base64
import os.path
import json
import re
import time
import dateutil.parser
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import logging

# Si modificas estos SCOPES, elimina el archivo token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    """Muestra mensajes básicos de Gmail.
    """
    creds = None
    # El archivo token.json almacena el token de acceso y refresco del usuario, y se
    # crea automáticamente cuando el flujo de autorización se completa por primera vez.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # Si no hay credenciales disponibles, permite que el usuario se autentique.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)  # reemplaza 'path/to/credentials.json' con la ruta a tu archivo de credenciales
            creds = flow.run_local_server(port=0)
        # Guarda las credenciales para la próxima ejecución
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    # Llama a la API de Gmail
    service = build('gmail', 'v1', credentials=creds)
    return service

# def list_messages(service):
#     # Llama a la API de Gmail para listar los mensajes
#     results = service.users().messages().list(userId='me', labelIds=['INBOX']).execute()
#     messages = results.get('messages', [])
#     for message in messages:
#         msg = service.users().messages().get(userId='me', id=message['id']).execute()
#         print(msg['snippet'])

if __name__ == '__main__':
    service = get_gmail_service()
    # list_messages(service)
