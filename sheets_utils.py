import gspread
from google.oauth2.service_account import Credentials

# Define el alcance (scopes) para editar hojas de cálculo
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Ruta a tu archivo de credenciales
RUTA_CREDENCIALES = "C:/Users/kevin/Downloads/RancaguaGPT_MVP/credenciales/credencialgoogle.json"  # <- cambia el nombre del archivo si es necesario

# ID de tu Google Sheet (sacado de la URL de la hoja)
SPREADSHEET_ID = "1UiWySOPYU77172vdi5wqczgHjqAA8aGX0M1BqTp6GO0"

def agregar_pregunta(pregunta):
    # Autenticación
    creds = Credentials.from_service_account_file(RUTA_CREDENCIALES, scopes=SCOPES)
    client = gspread.authorize(creds)

    # Abrir la hoja y seleccionar la primera pestaña
    sheet = client.open_by_key(SPREADSHEET_ID).sheet1

    # Insertar la pregunta como nueva fila al final
    sheet.append_row([pregunta])
