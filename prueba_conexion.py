from google import genai

# Usamos la nueva clave de tu proyecto A.B.R.I.L.
CLAVE_API = "AIzaSyBtgFaAFpEH4qr-4v6V8xIkHHdTPZR6gTQ"

# La nueva forma de inicializar el cliente
client = genai.Client(api_key=CLAVE_API)

print("Iniciando la conexion con el sistema y Gemini...")

# Enviamos el pulso usando el modelo flash
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents="Iniciando sistema. Por favor, confirma tu estado operativo en una sola oración concisa."
)

print("\nRespuesta de A.B.R.I.L:")
print(response.text)