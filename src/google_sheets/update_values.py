from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import json

# Definir la ruta al archivo de credenciales
SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'hipotecate-con-jose-eb84a5e3dafa.json')
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def get_credentials():
    creds = None
    try:
        # Primero, intentar obtener las credenciales desde una variable de entorno
        google_creds = os.getenv('GOOGLE_CREDENTIALS')
        if google_creds:
            creds_dict = json.loads(google_creds)
            creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
            print("Credenciales cargadas desde variable de entorno")
        elif os.path.exists(SERVICE_ACCOUNT_FILE):
            print(f"Archivo de credenciales encontrado: {SERVICE_ACCOUNT_FILE}")
            creds = service_account.Credentials.from_service_account_file(
                SERVICE_ACCOUNT_FILE, scopes=SCOPES)
            print(f"Credenciales cargadas: {creds.service_account_email}")
            print(f"Proyecto ID: {creds.project_id}")
            print(f"Token URI: {creds.token_uri}")
        else:
            print(f"Archivo de credenciales no encontrado: {SERVICE_ACCOUNT_FILE}")
    except Exception as e:
        print(f"Error al cargar credenciales: {e}")
        print(f"Tipo de error: {type(e)}")
    return creds

def update_user_data(spreadsheet_id, sheet_title, user_data):
    creds = get_credentials()
    service = build('sheets', 'v4', credentials=creds)
    
    print(f"Datos del usuario: {user_data}")
    
    values = [
        ['A2', user_data.get('nombre_completo', '')],
        ['B2', user_data.get('edad', '')],
        ['C2', 'Sí' if user_data.get('trabajando', False) else 'No'],
        ['D2', user_data.get('antiguedad_laboral', '')],
        ['E2', user_data.get('tipo_contrato', '')],
        ['F2', user_data.get('nomina', '')],
        ['G2', user_data.get('ingresos_extra', '')],
        ['H2', user_data.get('deudas', '')],
        ['I2', user_data.get('provincia', '')],
        ['J2', user_data.get('precio_vivienda', '')],
        ['K2', user_data.get('ahorro', '')]
    ]
    
    data = []
    for cell, value in values:
        data.append({
            'range': f"'{sheet_title}'!{cell}",
            'values': [[value]]
        })
    
    body = {
        'valueInputOption': 'USER_ENTERED',
        'data': data
    }
    
    try:
        result = service.spreadsheets().values().batchUpdate(
            spreadsheetId=spreadsheet_id, body=body).execute()
        print(f"Datos actualizados en la hoja: {sheet_title}")
        return result
    except HttpError as error:
        print(f"An error occurred: {error}")
        return error