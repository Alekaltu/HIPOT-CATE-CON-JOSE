import unittest
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import os

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '1qWF-iOdviTQDfitgXnLgpe6d0esFHT--2X3h01jdma0'  # Reemplaza con tu ID de spreadsheet real

def get_credentials():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

class TestGoogleSheetsConnection(unittest.TestCase):
    def test_connection(self):
        creds = get_credentials()
        service = build('sheets', 'v4', credentials=creds)
        
        try:
            sheet = service.spreadsheets()
            result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range='A1:A1').execute()
            values = result.get('values', [])
            self.assertIsNotNone(values, "No se pudo obtener datos de la hoja de cálculo")
            print("Conexión exitosa. Valor en A1:", values[0][0] if values else "Celda vacía")
        except Exception as e:
            self.fail(f"Error al conectar con Google Sheets: {str(e)}")

if __name__ == '__main__':
    unittest.main()
