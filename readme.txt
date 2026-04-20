# Proyecto Rasa Chatbot del Clima

Este proyecto es un chatbot conversacional construido con Rasa, capaz de responder preguntas sobre el clima actual y pronósticos futuros, integrado a través de acciones personalizadas con la API de Open-Meteo. Cuenta además con una interfaz web amigable.

## Requisitos Previos

- Python 3.10 (Recomendado)
- Si acabas de clonar el proyecto, necesitarás instalar las dependencias básicas necesarias (Rasa y requests).

## Configuración e Instalación

Abre una terminal en la carpeta principal del proyecto y ejecuta:

1. Crea un entorno virtual (recomendado):
   python -m venv venv310

2. Activa el entorno virtual:
   - En Windows: .\venv310\Scripts\activate
   - En Mac/Linux: source venv310/bin/activate

3. Instala Rasa y las librerías necesarias:
   pip install rasa
   pip install requests

## ¿Cómo ejecutar el proyecto?

El proyecto requiere que se ejecuten dos servicios en paralelo para que tanto la lógica del bot como sus llamadas a internet funcionen. La interfaz web que está en la carpeta "frontend" se conectará automáticamente.

### 1. Iniciar el Servidor de Acciones (Terminal 1)
Rasa usa un servidor de acciones para ejecutar el código Python (actions.py) encargado de buscar la información del clima a través de las APIs externas.
En una terminal con el entorno virtual activado, ejecuta:

rasa run actions

(Debería indicar que el servidor está corriendo en el puerto 5055).

### 2. Iniciar el Servidor Principal de Rasa (Terminal 2)
Abre otra terminal, activa también el entorno virtual en esta ventana, e inicializa el modelo habilitando los endpoints de la API (esenciales para el frontend web):

rasa run --enable-api --cors "*"

(El bot se iniciará y quedará a la escucha en el puerto 5005).

### 3. Iniciar la Interfaz de Usuario
Con ambos servidores corriendo, navega en las carpetas de tu computadora hasta entrar en el directorio `frontend`. Haz doble clic sobre el archivo `index.html` para abrirlo en tu navegador favorito.
¡Listo! Ya puedes empezar a chatear e interactuar con el bot.
