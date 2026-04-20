# 🚀 Chatbot NASA — Explorador Espacial con Rasa

> Chatbot conversacional con tono sarcástico conectado a las APIs reales de la NASA.
> Muestra la foto astronómica del día (APOD) y monitorea asteroides cercanos a la Tierra (NeoWs).

---

## ✨ Funcionalidades

| Requisito del TP | Descripción | API Usada |
|---|---|---|
| **API Externa #1** | Foto Astronómica del Día con título y descripción | [NASA APOD](https://api.nasa.gov/planetary/apod) |
| **API Externa #2** | Asteroides cercanos a la Tierra — top 3 por tamaño con datos reales | [NASA NeoWs](https://api.nasa.gov/neo/rest/v1/feed) |
| **Chit-Chat** | Responde a mensajes off-topic y redirige al usuario | — |
| **No-Input** | Detecta silencio y cierra la sesión tras 2 turnos sin respuesta | — |

---

## 📁 Estructura del Proyecto

```
Chatbot/
├── config.yml              # Pipeline NLU y políticas de diálogo
├── domain.yml              # Intents, slots, respuestas, acciones
├── endpoints.yml           # URL del servidor de acciones (localhost:5055)
├── credentials.yml         # Canal REST (para rasa shell y API HTTP)
├── .gitignore              # Excluye venv/, models/, .rasa/, __pycache__/
├── README.md               # Este archivo
├── data/
│   ├── nlu.yml             # Ejemplos de entrenamiento (~120 ejemplos, 8 intents)
│   ├── stories.yml         # Flujos de conversación multi-turno (9 historias)
│   └── rules.yml           # Reglas deterministas (6 reglas)
└── actions/
    ├── __init__.py         # Módulo Python
    └── actions.py          # Acciones personalizadas — NASA APOD + NeoWs + no-input
```

---

## ⚙️ Instalación

### Requisitos previos

- **Python 3.10**
- pip 23+
- Git

```bash
python --version  # Python 3.10.x
```

### Pasos de instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/facuuurz/Chatbot.git
cd Chatbot

# 2. Crear entorno virtual
python -m venv venv

# 3. Activar entorno virtual
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Fijar setuptools (necesario para Rasa 3.6 en Python 3.10)
pip install "setuptools<70" --force-reinstall

# 5. Instalar Rasa y dependencias
pip install rasa==3.6.20 rasa-sdk==3.6.2 requests
```

> **Nota:** El paso 4 es necesario porque setuptools 70+ rompe `pkg_resources`, que Rasa 3.6 usa internamente.

---

## 🚀 Uso

### 1. Entrenar el modelo

```bash
# Windows — setear encoding UTF-8 para evitar errores con emojis
$env:PYTHONIOENCODING="utf-8"
python -m rasa train
```

> Primera vez: puede tardar **5-10 minutos**. Genera el modelo en `models/` (no se sube al repositorio).

### 2. Iniciar el servidor de acciones — Terminal 1

```bash
.\venv\Scripts\activate
python -m rasa run actions
```

> Debe quedar corriendo en segundo plano. Escucha en `http://localhost:5055`.

### 3. Iniciar el chatbot — Terminal 2

```bash
.\venv\Scripts\activate
$env:PYTHONIOENCODING="utf-8"
python -m rasa shell
```

---

## 💬 Ejemplos de Conversación

```
Vos:  hola
Bot:  🚀 Bienvenido al Centro de Control Cósmico.
      ¿Foto del día de la NASA (APOD) o asteroides cercanos a la Tierra?

Vos:  foto del día
Bot:  📸 Foto Astronómica del Día — 2026-04-20
      🌌 Comet R3 PanSTARRS over a Himalayan Valley
      (© Basudeb Chakrabarti & Samit Saha)
      📖 The best way to see comet R3 PanSTARRS's long tail...
      🔭 Ver imagen: https://apod.nasa.gov/apod/image/...

Vos:  hay algo cerca de la tierra?
Bot:  ☄️ Monitoreo de Asteroides — 2026-04-20
      📡 La NASA rastrea 10 objeto(s) cercanos hoy.
      ✅ Ninguno es potencialmente peligroso.
      1. 2022 HE ✅ — Ø 0.095–0.212 km | 95,416 km/h | 34M km de distancia
      2. 2024 SQ4 ✅ — Ø 0.088–0.196 km | 68,691 km/h | 45M km
      3. 2026 GV2 ✅ — Ø 0.039–0.087 km | 28,586 km/h | 18M km

Vos:  estoy aburrido
Bot:  📡 El cosmos no tiene tiempo para eso. ¿Foto astronómica o asteroides?

Vos:  [silencio × 2]
Bot:  🚀 Sin respuesta del operador. Cerrando canal de comunicación. ¡Hasta la próxima! 🌌
```

---

## 🛠️ Tecnologías

| Componente | Versión | Rol |
|---|---|---|
| [Rasa Open Source](https://rasa.com/docs/rasa/) | 3.6.20 | Framework de chatbots |
| [Rasa SDK](https://rasa.com/docs/rasa/action-server/) | 3.6.2 | Servidor de acciones personalizadas |
| [NASA APOD API](https://api.nasa.gov/) | — | Foto astronómica del día |
| [NASA NeoWs API](https://api.nasa.gov/) | — | Asteroides cercanos a la Tierra |
| Python | 3.10 | Lenguaje base |
| TensorFlow | 2.12.0 | Motor de ML (DIET + TED classifier) |
| requests | 2.33.1 | Llamadas HTTP a las APIs de NASA |

### Pipeline NLU

```
WhitespaceTokenizer → RegexFeaturizer → LexicalSyntacticFeaturizer
→ CountVectorsFeaturizer (palabras) → CountVectorsFeaturizer (chars n-gram 1-4)
→ DIETClassifier (150 épocas) → EntitySynonymMapper
→ ResponseSelector → FallbackClassifier (threshold: 0.65)
```

### Políticas de Diálogo

- **MemoizationPolicy** — recuerda historias exactas del entrenamiento
- **RulePolicy** — ejecuta las 6 reglas deterministas
- **TEDPolicy** — aprende flujos complejos (max_history=6, 150 épocas)

---

## 📡 APIs de NASA — Detalles

### APOD (Astronomy Picture of the Day)
```
GET https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY
```
Devuelve la imagen o video astronómico del día con título, descripción y créditos del autor.
Si la API falla (503/timeout), el bot muestra una imagen histórica desde el archivo offline.

### NeoWs (Near Earth Object Web Service)
```
GET https://api.nasa.gov/neo/rest/v1/feed?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD&api_key=DEMO_KEY
```
Devuelve todos los asteroides que pasan cerca de la Tierra en el día consultado.
El bot muestra los **3 más grandes** con diámetro, velocidad y distancia mínima.

> **API Key:** El proyecto usa `DEMO_KEY` (30 req/hora, 50/día). Para producción, registrarse gratis en [https://api.nasa.gov/](https://api.nasa.gov/).

---

## ⚠️ Notas conocidas

- **DEMO_KEY rate limit:** Si pedís la foto del día varias veces seguidas, puede dar timeout. Esperá 1-2 minutos.
- **`venv/` y `models/` no están en el repositorio.** Hay que crearlos localmente siguiendo la guía de instalación.
- Los warnings de deprecación (`SQLAlchemy`, `pkg_resources`, `jax`) son esperables con esta combinación de versiones y no afectan el funcionamiento.

---

## 👤 Autor

Proyecto desarrollado para Trabajo Práctico Universitario.
