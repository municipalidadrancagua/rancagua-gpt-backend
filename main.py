from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path
from dotenv import load_dotenv
from sheets_utils import agregar_pregunta

import pandas as pd
import re
import os
import openai
from datetime import datetime

# Cargar variables de entorno
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

# Activar CORS (para conexión frontend-backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo de datos
class Pregunta(BaseModel):
    pregunta: str

# Cargar CSV con respuestas simuladas
archivo_csv = Path(__file__).parent / "respuestas_demo.csv"
try:
    respuestas_demo = pd.read_csv(archivo_csv)
except Exception as e:
    print(f"⚠️ Error al cargar respuestas_demo.csv: {e}")
    respuestas_demo = pd.DataFrame(columns=["pregunta", "respuesta"])

# Palabras comunes para ignorar
STOPWORDS = {"de", "la", "el", "en", "los", "las", "y", "a", "un", "una", "por", "qué", "cuál", "cuáles", "dónde", "cómo", "para", "es"}

# Funciones auxiliares
def limpiar_palabras(texto):
    palabras = re.findall(r"\b\w+\b", texto.lower(), re.UNICODE)
    return [p for p in palabras if p not in STOPWORDS]

def buscar_respuesta_simulada(pregunta_usuario):
    tokens_usuario = set(limpiar_palabras(pregunta_usuario))
    mejor_coincidencia = None
    puntaje_mayor = 0

    for _, row in respuestas_demo.iterrows():
        tokens_pregunta = set(limpiar_palabras(row["pregunta"]))
        coincidencias = tokens_usuario.intersection(tokens_pregunta)
        puntaje = len(coincidencias)

        if puntaje > puntaje_mayor:
            puntaje_mayor = puntaje
            mejor_coincidencia = row["respuesta"]

    if puntaje_mayor == 0:
        return "🤖 Lo siento, esa información está fuera de mis conocimientos actuales."
    return mejor_coincidencia

def guardar_interaccion_txt(pregunta, respuesta):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("preguntas.txt", "a", encoding="utf-8") as archivo:
        archivo.write(f"[{now}] Usuario: {pregunta}\n")
        archivo.write(f"[{now}] Rancagua GPT: {respuesta}\n\n")

# Endpoint principal
@app.post("/preguntar")
async def preguntar(pregunta: Pregunta):
    if not openai.api_key or openai.api_key.startswith("sk-reemplaza"):
        respuesta = buscar_respuesta_simulada(pregunta.pregunta)
    else:
        try:
            completado = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un asistente virtual de la Municipalidad de Rancagua."},
                    {"role": "user", "content": pregunta.pregunta}
                ]
            )
            respuesta = completado["choices"][0]["message"]["content"]
        except Exception as e:
            respuesta = f"⚠️ Error al obtener la respuesta: {str(e)}"

    # Guardar historial local y remoto
    guardar_interaccion_txt(pregunta.pregunta, respuesta)
    try:
        agregar_pregunta(pregunta.pregunta)
    except Exception as e:
        print(f"⚠️ Error al guardar en Google Sheets: {e}")

    return {"respuesta": respuesta}

# Servir archivos estáticos (como documentos PDF)
app.mount("/documentos", StaticFiles(directory="documentos"), name="documentos")