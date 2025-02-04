# API Gestión de eventos
Bienvenido, para poder acceder a la API será necesario seguir esta serie de pasos para ejecutarlo correctamente, se recomienda ejecutarlo en un ambiente Windows y usar una terminal CMD

# Instalación
Por temas de seguridad el archivo cred.env no se puede subir al repositorio, este archivo es necesario, si no se coloca en la raiz del proyecto que es junto al app.py no funcionara correctamente, el archivo se puede descargar de este link:

https://drive.google.com/file/d/10ig0YdiCu-4D3s6DvBymlPjhSoCHTLJA/view

Ahora será necesario instalar un entorno virtual, por lo que se usará este comando:
py -m venv env (Para Python versión 3.12)
python -m venv env (Para Python versión 3.11)

Después acceder al entorno virtual:
env\Scripts\activate.bat

Después se instalan las dependencias:
pip install -r requirements.txt

Una vez se instalan las dependencias, se inicia el proyecto de Flask:
flask run --debug

Si ves esto en la terminal significa que ya está funcionando el proyecto correctamente:
Running on http://127.0.0.1:5000

# Consumir la API
Para consumir la API será necesario tener Postman instalado en el sistema, ahí en el programa se importa el proyecto de postman llamado: Prueba_coordinadora.postman_collection

Una vez ahí será necesario loguearse para poder consumir la app, en el siguiente video podrás ver mejor como consumir la API:

# Acceso a video:
https://drive.google.com/file/d/17Amja2kR4Aa7Gb4etVvdjp8Pqdw_w98S/view

# Documentación de la API
Puedes acceder a la documentación de la API:
https://app.swaggerhub.com/templates-docs/BRANDONVASQUEZBARRET/Coordinadora/1.0.0-oas3.1#/

# Base de datos
La base de datos está en la nube de AWS por el servicio de RDS, por lo que no es necesario construirla para la ejecución de este proyecto

# Servicio de notificación
Como no se solicitó un endpoint para este servicio, entonces se implementó que las notificaciones fueran enviadas cada vez que se inicie el proyecto de Flask, los correos se pueden registrar en el endpoint de registrar asistentes

# Estructuras DDL y DML
En el repositorio verán dos archivos .sql los cuales contienen la estructura de la base de datos del proyecto

# Tiempos de respuesta de la API
Veremos unos tiempos de respuesta de la API, en el video se podrán ver los tiempos aquí descritos

Inicio de sesión: 964ms

Crear evento: 829ms

Listar todos los eventos: 848ms

Listar evento específico: 893ms

Actualizar evento: 962ms

Eliminar evento: 915ms

Registrar asistentes: 935ms

Obtener dirección y puntos de referencia: 985ms
