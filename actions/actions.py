from typing import Any, Text, Dict, List
import requests
import datetime
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SessionStarted, ActionExecuted, Restarted

class ActionCallApi(Action):
    def name(self) -> Text:
        return "action_call_api"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # URL de Open-Meteo: Libre de llaves, ideal para testing
        api_url = "https://api.open-meteo.com/v1/forecast"
        
        # Buscamos la entidad location del NLU
        location_entity = next(tracker.get_latest_entity_values("location"), None)
        
        # Si la red neuronal falla en extraer la entidad, hacemos un rescate manual del texto
        if not location_entity:
            texto_usuario = tracker.latest_message.get("text", "")
            for separador in [" de ", " en "]:
                if separador in texto_usuario:
                    # Extraer lo que está después del " de " o " en "
                    location_entity = texto_usuario.split(separador)[-1].strip("¿? ")
                    break
        
        # Si todo falló, usamos nuestro lugar por defecto
        location_entity = location_entity or "Oro Verde"
        
        # 1. Separamos ciudad y país si el usuario usó una coma (ej: "La Paz, Bolivia")
        ciudad_busqueda = location_entity
        pais_filtro = None
        if "," in location_entity:
            partes = location_entity.split(",", 1)
            ciudad_busqueda = partes[0].strip()
            pais_filtro = partes[1].strip().lower()

        # Coordenadas de Oro Verde por defecto
        lat, lon = -31.74, -60.51
        ciudad_mostrada = "Oro Verde"
        pais_mostrado = "Argentina"

        # Normalizador de nombres para Open-Meteo
        if ciudad_busqueda and ciudad_busqueda.lower() == "kiev":
            ciudad_busqueda = "Kyiv"

        # 2. Buscamos en Open-Meteo (traemos hasta 10 resultados para buscar el país)
        if ciudad_busqueda and ciudad_busqueda.lower() != "oro verde":
            geo_url = "https://geocoding-api.open-meteo.com/v1/search"
            try:
                geo_params = {"name": ciudad_busqueda, "count": 10, "language": "es"}
                geo_resp = requests.get(geo_url, params=geo_params, timeout=5)
                if geo_resp.status_code == 200:
                    geo_data = geo_resp.json()
                    results = geo_data.get("results")
                    
                    if results and len(results) > 0:
                        mejor_resultado = results[0]
                        # Si el usuario pidio un país específico, lo buscamos entre los 10 resultados
                        if pais_filtro:
                            for res in results:
                                if pais_filtro in res.get("country", "").lower():
                                    mejor_resultado = res
                                    break
                                    
                        lat = mejor_resultado["latitude"]
                        lon = mejor_resultado["longitude"]
                        ciudad_mostrada = mejor_resultado.get("name", ciudad_mostrada)
                        pais_mostrado = mejor_resultado.get("country", "")
                    else:
                        dispatcher.utter_message(text=f"No logré encontrar ningún lugar en el mundo llamado '{ciudad_busqueda}'.")
                        return []
            except Exception:
                dispatcher.utter_message(text="Hubo un problema de conexión al buscar en el mapa mundial.")
                return []

        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,precipitation_probability,wind_speed_10m",
            "timezone": "auto"
        }
        
        try:
            response = requests.get(api_url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                current = data.get("current", {})
                temp = current.get("temperature_2m", "N/A")
                hum_rel = current.get("relative_humidity_2m", "N/A")
                prob_lluvia = current.get("precipitation_probability", "0") # a veces en current no da el pronostico justo, pero probamos
                viento = current.get("wind_speed_10m", "N/A")
                
                texto_lugar = f"{ciudad_mostrada.title()} ({pais_mostrado})" if pais_mostrado else ciudad_mostrada.title()
                dispatcher.utter_message(
                    text=f"En {texto_lugar} la temperatura actual es de {temp}°C. La humedad es del {hum_rel}%, con vientos a {viento} km/h y una probabilidad de lluvia del {prob_lluvia}%."
                )
            else:
                dispatcher.utter_message(text="La API respondió, pero hubo un error en los datos.")
                
        except requests.exceptions.RequestException:
            dispatcher.utter_message(text="Error de red: No pude alcanzar el servidor de la API.")

        return []

class ActionSessionStart(Action):
    """Maneja el reinicio o la salida del usuario (No-input / Despedida)"""
    def name(self) -> Text:
        return "action_session_start"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        
        dispatcher.utter_message(text="Finalizando sesión por inactividad. ¡Hasta pronto!")
        
        # Reinicia el estado del bot por completo
        return [Restarted(), SessionStarted(), ActionExecuted("action_listen")]

class ActionFutureWeather(Action):
    def name(self) -> Text:
        return "action_future_weather"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # 1. Extraer ciudad
        location_entity = next(tracker.get_latest_entity_values("location"), None)
        texto_usuario = tracker.latest_message.get("text", "").lower()
        
        if not location_entity:
            for separador in [" de ", " en "]:
                if separador in texto_usuario:
                    location_entity = texto_usuario.split(separador)[-1].strip("¿? ")
                    break
        location_entity = location_entity or "Oro Verde"
        
        ciudad_busqueda = location_entity
        pais_filtro = None
        if "," in location_entity:
            partes = location_entity.split(",", 1)
            ciudad_busqueda = partes[0].strip()
            pais_filtro = partes[1].strip().lower()

        lat, lon = -31.74, -60.51
        ciudad_mostrada = "Oro Verde"
        pais_mostrado = "Argentina"

        if ciudad_busqueda and ciudad_busqueda.lower() == "kiev":
            ciudad_busqueda = "Kyiv"

        if ciudad_busqueda and ciudad_busqueda.lower() != "oro verde":
            geo_url = "https://geocoding-api.open-meteo.com/v1/search"
            try:
                geo_params = {"name": ciudad_busqueda, "count": 10, "language": "es"}
                geo_resp = requests.get(geo_url, params=geo_params, timeout=5)
                if geo_resp.status_code == 200:
                    results = geo_resp.json().get("results")
                    if results and len(results) > 0:
                        mejor_resultado = results[0]
                        if pais_filtro:
                            for res in results:
                                if pais_filtro in res.get("country", "").lower():
                                    mejor_resultado = res
                                    break
                                    
                        lat = mejor_resultado["latitude"]
                        lon = mejor_resultado["longitude"]
                        ciudad_mostrada = mejor_resultado.get("name", ciudad_mostrada)
                        pais_mostrado = mejor_resultado.get("country", "")
                    else:
                        dispatcher.utter_message(text=f"No logré encontrar ningún lugar en el mundo llamado '{ciudad_busqueda}'.")
                        return []
            except Exception:
                dispatcher.utter_message(text="Hubo un problema de conexión al buscar en el mapa mundial.")
                return []

        # 2. Analizar si busca calor, frio o lluvia
        busca_calor = "calor" in texto_usuario
        busca_frio = "frio" in texto_usuario or "frío" in texto_usuario
        busca_lluvia = "llover" in texto_usuario or "lluvia" in texto_usuario

        # Por defecto buscamos calor si no detecta nada
        if not busca_frio and not busca_lluvia:
            busca_calor = True

        # 3. Petición de pronóstico a 7 días
        api_url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum"],
            "timezone": "auto"
        }
        
        try:
            response = requests.get(api_url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                daily = data.get("daily", {})
                dates = daily.get("time", [])
                max_temps = daily.get("temperature_2m_max", [])
                min_temps = daily.get("temperature_2m_min", [])
                precip = daily.get("precipitation_sum", [])
                
                encontrado = False
                texto_lugar = f"{ciudad_mostrada.title()} ({pais_mostrado})" if pais_mostrado else ciudad_mostrada.title()
                
                for i in range(len(dates)):
                    fecha_str = dates[i]
                    # Convertir 'YYYY-MM-DD' a objeto date para formatearlo
                    fecha_obj = datetime.datetime.strptime(fecha_str, "%Y-%m-%d").date()
                    dia_semana = fecha_obj.strftime("%d/%m")
                    
                    t_max = max_temps[i]
                    t_min = min_temps[i]
                    p_sum = precip[i]
                    
                    if busca_calor and t_max > 28:
                        dispatcher.utter_message(f"El próximo día de calor en {texto_lugar} será el {dia_semana}, alcanzando los {t_max}°C.")
                        encontrado = True
                        break
                    elif busca_frio and t_min < 10:
                        dispatcher.utter_message(f"El próximo día de frío en {texto_lugar} será el {dia_semana}, bajando hasta los {t_min}°C.")
                        encontrado = True
                        break
                    elif busca_lluvia and p_sum > 1.0:
                        dispatcher.utter_message(f"Se esperan lluvias en {texto_lugar} para el {dia_semana}, con aprox {p_sum}mm de caída.")
                        encontrado = True
                        break
                
                if not encontrado:
                    if busca_calor:
                        dispatcher.utter_message(f"Revisé los próximos 7 días en {texto_lugar} y no encontré temperaturas mayores a 28°C.")
                    elif busca_frio:
                        dispatcher.utter_message(f"Revisé los próximos 7 días en {texto_lugar} y no habrá días de temperatura menor a 10°C.")
                    elif busca_lluvia:
                        dispatcher.utter_message(f"Revisé la semana en {texto_lugar} y, según el pronóstico, no hay probabilidad de lluvias fuertes.")
            
            else:
                dispatcher.utter_message("No pude obtener el pronóstico a 7 días en este momento.")
        except Exception as e:
            dispatcher.utter_message("Error de red conectando con el pronóstico del clima extrendido.")

        return []