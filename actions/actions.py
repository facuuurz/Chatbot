# actions/actions.py
# ================================================================
# Acciones personalizadas — Bot NASA.
#
# REQUISITO 1 — Conexión a APIs externas (NASA API):
#   • action_get_apod       → GET https://api.nasa.gov/planetary/apod
#                             Astronomy Picture of the Day
#
#   • action_get_asteroids  → GET https://api.nasa.gov/neo/rest/v1/feed
#                             Near Earth Objects (asteroides cercanos)
#
# REQUISITO 2 — No-input:
#   • action_handle_no_input → contador de turnos vacíos, cierre de sesión
#
# API Key: DEMO_KEY (30 req/hora, 50/día — sin registro)
#          Para producción: registrarse en https://api.nasa.gov/
#
# Sin dependencias nuevas: usa requests (ya instalado) y datetime (stdlib)
# ================================================================

import logging
import random
import requests
from datetime import date
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, ConversationPaused

logger = logging.getLogger(__name__)

# ── NASA API ──────────────────────────────────────────────────
NASA_API_KEY = "DEMO_KEY"
NASA_APOD_URL = "https://api.nasa.gov/planetary/apod"
NASA_NEO_URL  = "https://api.nasa.gov/neo/rest/v1/feed"

# ── Frases de cierre para APOD ────────────────────────────────
APOD_CLOSINGS = [
    "La NASA lo capturó. Millones de años de historia cósmica en una imagen. 🔭",
    "El universo tiene 93 mil millones de años luz de diámetro y aun así eligió mostrar esto hoy. 🌌",
    "Trece mil millones de años de evolución cósmica. Un solo día para verlo. ✨",
    "Saturno, Júpiter y toda la burocracia galáctica aprueban esta imagen. 🪐",
    "No es una pantalla de fondo de escritorio random — la NASA la eligió hoy para vos. 📸",
]

# ── Frases de cierre para asteroides ──────────────────────────
NEO_CLOSINGS = [
    "La NASA los rastrea. Vos los conocés. Misión cumplida. 🛰️",
    "El universo lanza rocas espaciales todo el tiempo. Lo tranquilizador es que hay alguien mirando. 📡",
    "Todos estos objetos pasan cerca. Ninguno va a impactar. Por ahora. 😅🪐",
    "El sistema solar es básicamente un campo de asteroides con planetas esquivando todo el tiempo. 🚀",
]

# ── Fallback offline APOD ─────────────────────────────────────
APOD_FALLBACK = [
    {
        "title": "Pilares de la Creación (Nebulosa del Águila)",
        "date": "1995-04-01",
        "explanation": (
            "El Telescopio Espacial Hubble capturó columnas de gas y polvo "
            "en la Nebulosa del Águila donde nacen nuevas estrellas. "
            "Cada pilar mide varios años luz de altura. Tomadas en 1995 y "
            "redescrubiertas por el James Webb en 2022 con resolución infrarroja."
        ),
        "url": "https://apod.nasa.gov/apod/image/2210/PillarsOfCreation_Webb.jpg",
    },
    {
        "title": "Agujero Negro M87* — Primera Imagen Real",
        "date": "2019-04-10",
        "explanation": (
            "El Event Horizon Telescope capturó la primera imagen directa de un "
            "agujero negro: M87*, a 55 millones de años luz en la galaxia Messier 87. "
            "Su masa equivale a 6.500 millones de soles. La sombra visible es el "
            "horizonte de eventos, el punto de no retorno."
        ),
        "url": "https://apod.nasa.gov/apod/image/1904/M87bhEht_large.jpg",
    },
    {
        "title": "Tierra desde la Luna — Earthrise (Apollo 8)",
        "date": "1968-12-24",
        "explanation": (
            "Tomada por William Anders durante la misión Apollo 8, es una de las "
            "fotos más influyentes de la historia. La Tierra emerge sobre el horizonte "
            "lunar, frágil y sola en el espacio. Dicen que esta imagen inició el "
            "movimiento ambientalista moderno."
        ),
        "url": "https://apod.nasa.gov/apod/image/1012/AS8-14-2383HR.jpg",
    },
]

# ── Fallback offline NEO ──────────────────────────────────────
NEO_FALLBACK = [
    {
        "name": "99942 Apophis",
        "diameter_km": 0.370,
        "velocity_kmh": 108_000,
        "miss_distance_km": 37_600,
        "hazardous": True,
    },
    {
        "name": "2023 DW",
        "diameter_km": 0.052,
        "velocity_kmh": 74_000,
        "miss_distance_km": 1_800_000,
        "hazardous": False,
    },
    {
        "name": "1994 PC1",
        "diameter_km": 1.052,
        "velocity_kmh": 71_556,
        "miss_distance_km": 1_993_825,
        "hazardous": True,
    },
]


# ================================================================
# ACCIÓN 1: Foto astronómica del día — NASA APOD
# ================================================================
class ActionGetApod(Action):
    """
    GET https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY

    Devuelve la imagen o video astronómico que la NASA elige cada día.
    Respuesta JSON: title, date, explanation, url, media_type,
                   hdurl (opcional), copyright (opcional)
    """

    def name(self) -> Text:
        return "action_get_apod"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        try:
            response = requests.get(
                NASA_APOD_URL,
                params={"api_key": NASA_API_KEY},
                timeout=15,
            )
            response.raise_for_status()
            data = response.json()

            title      = data.get("title", "Sin título")
            explanation = data.get("explanation", "Sin descripción disponible.")
            media_type = data.get("media_type", "image")
            url        = data.get("url", "")
            date_apod  = data.get("date", str(date.today()))
            copyright_ = data.get("copyright", "NASA").strip().replace("\n", " ")

            # Truncar descripción si es muy larga
            if len(explanation) > 450:
                explanation = explanation[:447] + "..."

            # Distinguir imagen de video (a veces es un YouTube embed)
            if media_type == "video":
                media_line = f"🎬 *Video del día:* {url}"
            else:
                media_line = f"🔭 *Ver imagen completa:* {url}"

            message = (
                f"📸 **Foto Astronómica del Día — {date_apod}**\n\n"
                f"🌌 **{title}**\n"
                f"_(© {copyright_})_\n\n"
                f"📖 {explanation}\n\n"
                f"{media_line}\n\n"
                f"_{random.choice(APOD_CLOSINGS)}_"
            )
            dispatcher.utter_message(text=message)

        except requests.exceptions.Timeout:
            logger.error("Timeout al conectar con NASA APOD")
            dispatcher.utter_message(
                text="⏳ El servidor de la NASA tardó demasiado en responder. "
                     "Puede ser por el límite de la DEMO_KEY (30 req/hora). "
                     "Esperá unos minutos e intentá de nuevo."
            )

        except requests.exceptions.HTTPError as e:
            status = getattr(e.response, "status_code", "?")
            logger.error(f"HTTP Error en NASA APOD: {e}")
            if status == 429:
                dispatcher.utter_message(
                    text="😤 La NASA me puso límite de consultas (DEMO_KEY: 30/hora). "
                         "Esperá unos minutos e intentá de nuevo. 🕐"
                )
            else:
                # Para 503 y otros errores del servidor, usar imagen offline
                vision = random.choice(APOD_FALLBACK)
                dispatcher.utter_message(
                    text=f"🔌 Servidor de la NASA inaccesible (error {status}). Del archivo histórico:\n\n"
                         f"📸 **{vision['title']}** ({vision['date']})\n\n"
                         f"📖 {vision['explanation']}\n\n"
                         f"🔭 *Referencia:* {vision['url']}\n\n"
                         f"_{random.choice(APOD_CLOSINGS)}_"
                )

        except requests.exceptions.ConnectionError:
            logger.error("Error de conexión con NASA APOD — usando imagen offline")
            vision = random.choice(APOD_FALLBACK)
            dispatcher.utter_message(
                text=f"🔌 Sin conexión con la NASA ahora mismo. Del archivo histórico:\n\n"
                     f"📸 **{vision['title']}** ({vision['date']})\n\n"
                     f"📖 {vision['explanation']}\n\n"
                     f"🔭 *Referencia:* {vision['url']}\n\n"
                     f"_{random.choice(APOD_CLOSINGS)}_"
            )

        except Exception as e:
            logger.error(f"Error inesperado en action_get_apod: {e}")
            dispatcher.utter_message(
                text="😵 Algo salió mal al conectar con la NASA. "
                     "Intentá de nuevo en unos momentos."
            )

        return []


# ================================================================
# ACCIÓN 2: Asteroides cercanos a la Tierra — NASA NeoWs
# ================================================================
class ActionGetAsteroids(Action):
    """
    GET https://api.nasa.gov/neo/rest/v1/feed
        ?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD&api_key=DEMO_KEY

    Devuelve los Near Earth Objects (NEOs) del día actual.
    Muestra los 3 más relevantes: el más grande, el más rápido
    y si hay alguno potencialmente peligroso.
    """

    def name(self) -> Text:
        return "action_get_asteroids"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        today = str(date.today())

        try:
            response = requests.get(
                NASA_NEO_URL,
                params={
                    "start_date": today,
                    "end_date":   today,
                    "api_key":    NASA_API_KEY,
                },
                timeout=15,
            )
            response.raise_for_status()
            data = response.json()

            neos = data.get("near_earth_objects", {}).get(today, [])
            total = data.get("element_count", len(neos))

            if not neos:
                dispatcher.utter_message(
                    text=f"📡 Hoy ({today}) no hay NEOs registrados para este rango. "
                         f"Intentá mañana — el sistema solar nunca descansa. 🪐"
                )
                return []

            # ── Clasificar NEOs ───────────────────────────────────
            peligrosos = [n for n in neos if n.get("is_potentially_hazardous_asteroid")]
            no_peligrosos = [n for n in neos if not n.get("is_potentially_hazardous_asteroid")]

            # Ordenar por diámetro promedio descendente
            def avg_diam(neo):
                d = neo.get("estimated_diameter", {}).get("kilometers", {})
                return (d.get("estimated_diameter_min", 0) + d.get("estimated_diameter_max", 0)) / 2

            neos_sorted = sorted(neos, key=avg_diam, reverse=True)
            top3: list = list(neos_sorted[:3])

            # ── Encabezado ────────────────────────────────────────
            if peligrosos:
                header = (
                    f"☄️ **Monitoreo de Asteroides — {today}**\n\n"
                    f"📡 La NASA rastrea **{total} objeto(s)** cercanos hoy.\n"
                    f"⚠️ **{len(peligrosos)} potencialmente peligroso(s)** según la clasificación NASA.\n\n"
                    f"---\n"
                )
            else:
                header = (
                    f"☄️ **Monitoreo de Asteroides — {today}**\n\n"
                    f"📡 La NASA rastrea **{total} objeto(s)** cercanos hoy.\n"
                    f"✅ **Ninguno es potencialmente peligroso** según la clasificación NASA.\n\n"
                    f"---\n"
                )

            # ── Detalle de los top 3 ──────────────────────────────
            detalles = []
            for i, neo in enumerate(top3, start=1):
                name = neo.get("name", "NEO Desconocido").replace("(", "").replace(")", "").strip()
                hazardous = neo.get("is_potentially_hazardous_asteroid", False)
                hazard_icon = "⚠️" if hazardous else "✅"

                diam_data = neo.get("estimated_diameter", {}).get("kilometers", {})
                diam_min  = diam_data.get("estimated_diameter_min", 0)
                diam_max  = diam_data.get("estimated_diameter_max", 0)

                approach_list = neo.get("close_approach_data") or [{}]
                approach      = approach_list[0] if approach_list else {}
                rel_velocity  = approach.get("relative_velocity") or {}
                miss_distance = approach.get("miss_distance") or {}
                vel_kmh    = float(rel_velocity.get("kilometers_per_hour", 0))
                miss_km    = float(miss_distance.get("kilometers", 0))
                miss_lunar = float(miss_distance.get("lunar", 0))

                detalles.append(
                    f"**{i}. {name}** {hazard_icon}\n"
                    f"   📏 Diámetro: {diam_min:.3f} – {diam_max:.3f} km\n"
                    f"   💨 Velocidad: {vel_kmh:,.0f} km/h\n"
                    f"   📍 Distancia mínima: {miss_km:,.0f} km ({miss_lunar:.1f} dist. lunares)\n"
                )

            message = (
                header
                + "\n".join(detalles)
                + f"\n_(Mostrando {len(top3)} de {total} objetos — ordenados por tamaño)_\n\n"
                + f"_{random.choice(NEO_CLOSINGS)}_"
            )
            dispatcher.utter_message(text=message)

        except requests.exceptions.Timeout:
            logger.error("Timeout al conectar con NASA NeoWs")
            dispatcher.utter_message(
                text="⏳ El radar espacial tardó demasiado. "
                     "Puede ser el límite de DEMO_KEY. Intentá en unos minutos."
            )

        except requests.exceptions.HTTPError as e:
            status = getattr(e.response, "status_code", "?")
            logger.error(f"HTTP Error en NASA NeoWs: {e}")
            if status == 429:
                dispatcher.utter_message(
                    text="😤 Límite de consultas DEMO_KEY alcanzado (30/hora). "
                         "Esperá unos minutos. 🕐"
                )
            else:
                dispatcher.utter_message(
                    text=f"🌀 El radar de la NASA devolvió un error {status}. "
                         f"Intentá de nuevo en unos momentos."
                )

        except requests.exceptions.ConnectionError:
            logger.error("Error de conexión con NASA NeoWs — usando datos offline")
            fallback = random.choice(NEO_FALLBACK)
            hazard_icon = "⚠️ Potencialmente peligroso" if fallback["hazardous"] else "✅ Sin peligro"
            dispatcher.utter_message(
                text=f"🔌 Sin conexión con la NASA. Del archivo histórico:\n\n"
                     f"☄️ **{fallback['name']}**\n"
                     f"   📏 Diámetro: {fallback['diameter_km']:.3f} km\n"
                     f"   💨 Velocidad: {fallback['velocity_kmh']:,} km/h\n"
                     f"   📍 Distancia mínima: {fallback['miss_distance_km']:,} km\n"
                     f"   🛡️ {hazard_icon}\n\n"
                     f"_{random.choice(NEO_CLOSINGS)}_"
            )

        except Exception as e:
            logger.error(f"Error inesperado en action_get_asteroids: {e}")
            dispatcher.utter_message(
                text="😵 Algo salió mal con el radar espacial. "
                     "Intentá de nuevo en unos momentos."
            )

        return []


# ================================================================
# ACCIÓN 3: Manejo de No-Input + Fallback (Requisito 2 del TP)
# ================================================================
class ActionHandleNoInput(Action):
    """
    Maneja dos casos bajo nlu_fallback:

    A) Mensaje VACÍO (no-input real):
       - 0 no-inputs previos → aviso (1er aviso)
       - 1+ no-inputs previos → despedida + ConversationPaused()

    B) Mensaje con texto pero baja confianza NLU:
       - Respuesta de fallback espacial sin incrementar el contador.
    """

    def name(self) -> Text:
        return "action_handle_no_input"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        last_message = tracker.latest_message.get("text", "").strip()

        # ── CASO B: Texto incomprensible (fallback) ──────────────
        if last_message:
            fallback_responses = [
                "📡 Señal no identificada. Probá con: *'foto del día'* o *'asteroides de hoy'*.",
                "🛰️ El sistema no decodificó eso. ¿Querés la foto del día de la NASA o datos de asteroides?",
                "🌀 Frecuencia desconocida. Comandos disponibles: *'foto del día'* o *'asteroides'*.",
                "😒 Control de misión no registra ese comando. Probá: *'APOD'* o *'NEO'*.",
            ]
            dispatcher.utter_message(text=random.choice(fallback_responses))
            return []

        # ── CASO A: Mensaje vacío (no-input real) ────────────────
        no_input_count = int(tracker.get_slot("no_input_count") or 0)

        if no_input_count == 0:
            avisos = [
                "📡 ¿Seguís ahí? El control de misión espera tu instrucción. 🛰️",
                "🛸 Silencio en la frecuencia... ¿Todo bien? Escribí *'foto del día'* o *'asteroides'*.",
                "🔭 Sin respuesta del operador. ¿Foto del día de la NASA o datos de asteroides?",
            ]
            dispatcher.utter_message(text=random.choice(avisos))
            return [SlotSet("no_input_count", 1)]

        else:
            despedidas = [
                "🚀 Sin respuesta del operador. Cerrando canal de comunicación. ¡Hasta la próxima! 🌌",
                "📡 Conexión cerrada por inactividad. Volvé cuando quieras explorar el cosmos. 🛰️",
                "👨‍🚀 Misión cancelada por silencio de radio. El universo sigue ahí cuando vuelvas. ✨",
            ]
            dispatcher.utter_message(text=random.choice(despedidas))
            return [
                SlotSet("no_input_count", 0),
                ConversationPaused()
            ]
