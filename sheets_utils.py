from pathlib import Path
import os
import gspread
from google.oauth2.service_account import Credentials

# Base de tu proyecto
BASE_DIR = Path(__file__).parent

# Ruta por defecto local
local = BASE_DIR / "credenciales" / "credencialgoogle.json"
# Ruta en Render cuando subes el Secret File
remote = Path("/etc/secrets/credencialgoogle.json")

# Elige la que exista
RUTA_CREDENCIALES = Path(os.getenv("GOOGLE_CREDENTIALS_PATH", local if local.exists() else remote))

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = "TU_ID_DE_HOJA"

def agregar_pregunta(pregunta):
    creds = Credentials.from_service_account_file(str(RUTA_CREDENCIALES), scopes=SCOPES)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_ID).sheet1
    sheet.append_row([pregunta])
