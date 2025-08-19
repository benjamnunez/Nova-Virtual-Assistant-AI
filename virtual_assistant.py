#IMPORT OPENAI
from openai import OpenAI

#ASISTENTE VIRTUAL MEJORADO
import speech_recognition as sr
import edge_tts
import asyncio
import unicodedata
import os
from datetime import datetime
import pygame
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Configuración de OpenAI

client = OpenAI(
    api_key="OPENAI_API_KEY"
)



sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id="IDSPOTIFY_CLIENT_ID",
    client_secret="CLIENT_SECRET_SPOTIFY",
    redirect_uri="URI_DE_REDIRECCIONAMIENTO",
    scope="user-read-playback-state,user-modify-playback-state,user-read-currently-playing"
))



# Comando de activación
comando_activacion = "oye nova activa asistente virtual"
comando_spotify = "oye nova activa modo spotify"


def reproducir_spotify(cancion):
    resultados = sp.search(q=cancion, limit=1, type="track")
    if resultados["tracks"]["items"]:
        track_uri = resultados["tracks"]["items"][0]["uri"]
        sp.start_playback(uris=[track_uri])
        return f"Reproduciendo {cancion} en Spotify."
    else:
        return "No encontré esa canción en Spotify."


def normalizar(texto):
    return unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII').lower().strip()

async def hablar(texto):
    """Función mejorada usando edge-tts y pygame"""
    try:
        print(f"Bot dice: {texto}")
        voice = "es-MX-JorgeNeural"
        communicate = edge_tts.Communicate(text=texto, voice=voice)
        await communicate.save("temp_voice.mp3")
        
        # Reproducir y esperar hasta que termine
        pygame.mixer.init()
        pygame.mixer.music.load("temp_voice.mp3")
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            await asyncio.sleep(0.1)
        pygame.mixer.quit()
        
    except Exception as e:
        print(f"Error al hablar: {e}")

def ejecutar_hablar(texto):
    """Wrapper para ejecutar la función asíncrona desde código síncrono"""
    asyncio.run(hablar(texto))

def main():
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 4000
    recognizer.dynamic_energy_threshold = True
    
    activo = False # El asistente inicia en modo pasivo
    activo_spotify = False # El modo Spotify inicia en modo pasivo
    
    # Prueba inicial de voz
    ejecutar_hablar("Sistema NOVA iniciado. Dime el comando de activación para empezar a interactuar.")
    
    with sr.Microphone() as source:
        print("Ajustando al ruido ambiente...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        
        while True:
            try:
                print("\nEscuchando...")
                audio = recognizer.listen(source)
                texto = recognizer.recognize_google(audio, language='es-ES')
                texto_normalizado = normalizar(texto)
                
                print(f"Has dicho: {texto_normalizado}")
                
                # Procesamiento de comandos
                
                # Activación por comando de voz
                if comando_activacion in texto_normalizado :
                    ejecutar_hablar("Hola, te escucho.")
                    activo = True
                    continue
                
                
                # Activación por comando de voz para Spotify
                if comando_spotify in texto_normalizado:
                    ejecutar_hablar("Modo Spotify activado. ¿Qué canción quieres escuchar?")
                    activo_spotify = True
                    continue
                
                if activo_spotify:
                    palabra_spotify = "pon" or "reproduce" or "escucha"
                    print("Modo Spotify activo.")
                    if "pon" in texto_normalizado:
                        cancion = texto_normalizado.replace(palabra_spotify, "").strip()
                        respuesta = reproducir_spotify(cancion)
                        ejecutar_hablar(respuesta)
                        devices = sp.devices()
                        print(devices)
                        activo = False  # Activa el asistente después de reproducir música
                
                
                
                if "nada" in texto_normalizado or "salir" in texto_normalizado:
                    print("Asistente inactivo. Di 'Oye Nova' para activarlo.")
                    ejecutar_hablar("OK.")
                    activo = False
                    continue
                
                # Desactivación por comando de voz
                
                if not activo and "apagate" in texto_normalizado:
                    print("Saliendo del asistente virtual.")
                    ejecutar_hablar("Claro, que tengas un buen día.")
                    break
                
                    
                if activo:
                        
                    response = client.responses.create(
                        model="gpt-4o-mini",
                        input=texto_normalizado,
                        store=True,
                        max_output_tokens=1000,
                        temperature=0.7,
                        top_p=0.9,
                    )
                    respuesta_ia = normalizar(response.output_text).replace("*", "").replace("#", "")
                    ejecutar_hablar(respuesta_ia)
                    activo = False  # Desactiva después de responder
                    print("asistente virtual desactivado. Di 'hola nova' para volver a activarlo.")
                else:
                    print("Esperando comando de activación...")
                
                
            except sr.WaitTimeoutError:
                print("Tiempo de espera agotado")
                continue

            except sr.UnknownValueError:
                print("No se pudo entender el audio")
                continue

            except sr.RequestError as e:
                print(f"Error con el servicio de reconocimiento: {str(e)}")
                ejecutar_hablar("Hay un problema con el servicio de voz. Revisa tu conexión a internet.")
                continue

            except Exception as e:
                print(f"Error inesperado: {str(e)}")
                continue

if __name__ == "__main__":
    main()
