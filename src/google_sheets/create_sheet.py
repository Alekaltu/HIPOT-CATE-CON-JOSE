import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Asegúrate de que esta ruta sea correcta
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

def create_user_sheet(spreadsheet_id, user_id):
    creds = get_credentials()
    service = build('sheets', 'v4', credentials=creds)
    
    sheet_title = f'Usuario_{user_id}'
    
    try:
        # Obtener información de la hoja 2
        sheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        sheets = sheet_metadata.get('sheets', '')
        hoja_2 = next((sheet for sheet in sheets if sheet['properties']['title'] == 'Hoja 2'), None)
        
        if not hoja_2:
            print("No se encontró la 'Hoja 2'")
            return None
        
        hoja_2_id = hoja_2['properties']['sheetId']
        
        # Duplicar la hoja 2
        request_body = {
            'requests': [{
                'duplicateSheet': {
                    'sourceSheetId': hoja_2_id,
                    'insertSheetIndex': 2,
                    'newSheetName': sheet_title
                }
            }]
        }
        
        response = service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=request_body
        ).execute()
        
        new_sheet_id = response['replies'][0]['duplicateSheet']['properties']['sheetId']
        print(f"Nueva hoja creada: {sheet_title}")
        print(f"Nueva hoja creada con ID: {new_sheet_id}")
        return sheet_title
    except Exception as e:
        print(f"Error al crear la hoja: {e}")
        print(f"Tipo de error: {type(e)}")
        return None

# ... resto de tu código ...