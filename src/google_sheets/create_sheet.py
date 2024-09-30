import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Asegúrate de que esta ruta sea correcta
SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'hipotecate-con-jose-2bde0457b966.json')

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def get_credentials():
    creds = None
    if os.path.exists(SERVICE_ACCOUNT_FILE):
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        print(f"Credenciales cargadas: {creds.service_account_email}")
    else:
        print(f"Archivo de credenciales no encontrado: {SERVICE_ACCOUNT_FILE}")
    return creds

def create_user_sheet(spreadsheet_id, user_id):
    creds = get_credentials()
    if not creds:
        print("No se pudieron obtener las credenciales")
        return None
    
    service = build('sheets', 'v4', credentials=creds)
    
    try:
        print(f"Intentando crear hoja para usuario {user_id} en spreadsheet {spreadsheet_id}")
        
        # Obtener información de la hoja 2
        sheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        sheets = sheet_metadata.get('sheets', '')
        hoja_2 = next((sheet for sheet in sheets if sheet['properties']['title'] == 'Hoja 2'), None)
        
        if not hoja_2:
            print("No se encontró la 'Hoja 2'")
            return None
        
        hoja_2_id = hoja_2['properties']['sheetId']
        
        # Duplicar la hoja 2
        sheet_name = f'Usuario_{user_id}'
        request_body = {
            'requests': [{
                'duplicateSheet': {
                    'sourceSheetId': hoja_2_id,
                    'insertSheetIndex': 2,
                    'newSheetName': sheet_name
                }
            }]
        }
        
        response = service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=request_body
        ).execute()
        
        new_sheet_id = response['replies'][0]['duplicateSheet']['properties']['sheetId']
        print(f"Nueva hoja creada: Usuario_{user_id}")
        print(f"Nueva hoja creada con ID: {new_sheet_id}")
        return new_sheet_id
    except Exception as e:
        print(f"Error al crear la hoja: {e}")
        print(f"Tipo de error: {type(e)}")
        if hasattr(e, 'reason'):
            print(f"Razón del error: {e.reason}")
        return None

# ... resto de tu código ...
