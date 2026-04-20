# 🔮 Gurú Astrológico — Chatbot con Rasa

> Chatbot con personalidad mística y sarcástica, construido con Rasa Open Source.
> Consulta tu horóscopo diario y tiradas de tarot usando APIs gratuitas reales.

---

## ✨ Funcionalidades

| Requisito | Descripción | API Usada |
|---|---|---|
| **API Externa** | Horóscopo del día por signo | [Aztro API](https://aztro.sameerkumar.website/) (POST) |
| **API Externa** | Carta de tarot aleatoria | [RWS Cards API](https://rws-cards-api.herokuapp.com/) (GET) |
| **Chit-Chat** | Responde a mensajes off-topic con frases místicas | — |
| **No-Input** | Detecta silencio y cierra la sesión tras 2 turnos | — |

---

## 📁 Estructura del Proyecto

```
Chatbot/
├── config.yml              # Pipeline NLU y políticas de diálogo
├── domain.yml              # Intents, slots, respuestas, acciones
├── endpoints.yml           # URL del servidor de acciones
├── credentials.yml         # Canales de comunicación (REST)
├── README.md               # Este archivo
├── data/
│   ├── nlu.yml             # Ejemplos de entrenamiento NLU (~100 ejemplos)
│   ├── stories.yml         # Flujos de conversación multi-turno
│   └── rules.yml           # Reglas deterministas (chit-chat, no-input)
└── actions/
    ├── __init__.py         # Módulo Python
    └── actions.py          # Acciones personalizadas con llamadas a APIs
```

---

## ⚙️ Instalación

### Requisitos previos

- **Python 3.9** (obligatorio — Rasa 3.x no es compatible con 3.10+)
- pip 23+

```bash
# Verificar versión de Python
python --version  # Debe mostrar Python 3.9.x
```

### Pasos de instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/TU_USUARIO/guru-astrologico.git
cd guru-astrologico

# 2. Crear entorno virtual
python -m venv venv

# 3. Activar entorno virtual
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Actualizar pip
python -m pip install --upgrade pip wheel setuptools

# 5. Instalar Rasa y dependencias
pip install rasa==3.6.20 rasa-sdk==3.6.2 requests
```

---

## 🚀 Uso

### 1. Entrenar el modelo

```bash
rasa train
```

> Primera vez: puede tardar 5-10 minutos. Genera un modelo en `models/`.

### 2. Iniciar el servidor de acciones (Terminal 1)

```bash
rasa run actions
```

> Debe estar corriendo para que funcionen las APIs de horóscopo y tarot.

### 3. Iniciar el chatbot (Terminal 2)

```bash
rasa shell
```

---

## 💬 Ejemplos de Conversación

```
Vos: hola
Bot: 🔮 Las estrellas te esperaban... ¿Horóscopo o tarot?

Vos: quiero mi horóscopo
Bot: ⭐ ¿Cuál es tu signo del zodíaco?

Vos: soy escorpio
Bot: 🔮 Los astros han hablado...
     ♏ ESCORPIO — [descripción del día, compatibilidad, color, número]
     "Mercurio retrógrado no ayuda, pero bueno. 🪐"

Vos: desaprobé un final
Bot: "Las cartas ya lo sabían... ¿Consultamos el tarot?"

Vos: [silencio × 2]
Bot: "Los astros no esperan eternamente... Volvé cuando quieras. 🔮"
```

---

## 🛠️ Tecnologías

- [Rasa Open Source 3.6](https://rasa.com/docs/rasa/) — Framework de chatbots
- [Aztro API](https://aztro.sameerkumar.website/) — Horóscopo diario gratuito
- [RWS Cards API](https://rws-cards-api.herokuapp.com/api/v1/cards/random) — Cartas de tarot
- Python 3.9 + requests

---

## 👤 Autor

Proyecto desarrollado para Trabajo Práctico Universitario.
