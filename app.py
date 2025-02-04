import os
import json
import psycopg2
import hashlib
import requests
from psycopg2.extras import RealDictCursor
from modelos import eventos
from flask import Flask, jsonify, request, g
from dotenv import load_dotenv
from os.path import join, dirname
from datetime import datetime, timedelta
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from mailer import notificaciones

ruta_archivo_env = join(dirname(__file__), 'cred.env')
load_dotenv(ruta_archivo_env)

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = os.getenv('JWT_SECRET_KEY')
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=12)
jwt = JWTManager(app)

host = os.getenv('HOST')
user = os.getenv('USER')
password = os.getenv('PASSWORD_BD')

try:
    conn = psycopg2.connect(host=host, database=os.getenv('DATABASE'), user=user, password=password, cursor_factory=RealDictCursor)
    sql = f"""SELECT * FROM eventos"""
    cur = conn.cursor()
    cur.execute(sql)
    results = cur.fetchall()
    usuarios = []
    if len(results) > 0:
        cur.close()
        data = []
        for i in results:
            data.append(i)

        for i in data:
            for j in i["asistentes"]:
                usuarios.append(str(j))
    if len(usuarios) > 0:
        notificaciones(usuarios)
except Exception as err:
    print("Error en las notificaciones")

@app.route("/iniciarSesion", methods=["POST"])
def crear_token():
    content = request.json
    try:
        usuario = content["usuario"]
        contraseña = content["contraseña"]
    except Exception as err:
        response = {'respuesta': "Campos faltantes por enviar"}
        return jsonify(response)
    if app.config['TESTING'] is True:
        database = os.getenv('TEST_DATABASE')
    else:
        database = os.getenv('DATABASE')
    conn = psycopg2.connect(host=host, database=database, user=user, password=password, cursor_factory=RealDictCursor)
    sql = f"SELECT * FROM usuarios WHERE usuario = '{usuario}'"
    cur = conn.cursor()
    cur.execute(sql)
    results = cur.fetchall()
    cur.close()
    if len(results) == 0:
        response = {'respuesta': "Usuario no encontrado"}
        return jsonify(response)
    data = []
    for i in results:
        data.append(i)
    sha256_hash = hashlib.sha256(str(contraseña).encode())
    cadena_hexadecimal = sha256_hash.hexdigest()
    if cadena_hexadecimal == data[0]["contraseña"]:
        token = create_access_token(identity=data[0]["id"])
        return jsonify({ "token": token, "id_usuario": data[0]["id"] })
    else:
        return jsonify({"respuesta": "Contraseña incorrecta"})

@app.route('/crearEvento', methods=['POST'])
@jwt_required()
def crear_evento():
    content = request.json
    try:
        fecha = content["fecha"]
        nombre = content["nombre"]
        longitud = content["longitud"]
        latitud = content["latitud"]
    except Exception as err:
        response = {'respuesta': "Campos faltantes por enviar"}
        return jsonify(response)

    if fecha == "" or nombre == "" or longitud == "" or latitud == "":
        response = {'respuesta': "Algunos campos están en blanco"}
        return jsonify(response)

    if type(longitud) is not float or type(latitud) is not float:
        response = {"respuesta":"Formato erróneo en las coordenadas, ejemplo correcto: 4.34123 sin comillas"}
        return jsonify(response)
    try:
        validacion_fecha = datetime.strptime(fecha, f'%Y-%m-%d %H:%M')
    except Exception as err:
        response = {'respuesta': "Formato erróneo en la fecha, debe ser: YYYY-MM-DD HH:MM"}
        return jsonify(response)
    if app.config['TESTING'] is True:
        database = os.getenv('TEST_DATABASE')
    else:
        database = os.getenv('DATABASE')
    now = datetime.now()
    codigo = now.strftime("%Y%m%d%H%M%S")
    evento = eventos(fecha, nombre, longitud, latitud, codigo)
    eventoCreado = eventos.crear_evento(evento, database)
    response = {'respuesta': "Evento creado"}
    with open("eventos.json", "r") as jsonFile:
        data = json.load(jsonFile)

    data[codigo] = {"latitud": latitud, "longitud": longitud}

    with open("eventos.json", "w") as jsonFile:
        json.dump(data, jsonFile)
    app.config['CODIGO_TEST'] = codigo
    return jsonify(response)

@app.route('/listarEventos', methods=['GET'])
@jwt_required()
def listar_eventos():
    if app.config['TESTING'] is True:
        database = os.getenv('TEST_DATABASE')
    else:
        database = os.getenv('DATABASE')
    conn = psycopg2.connect(host=host, database=database, user=user, password=password, cursor_factory=RealDictCursor)
    sql = f"""SELECT * FROM eventos"""
    cur = conn.cursor()
    cur.execute(sql)
    results = cur.fetchall()
    cur.close()
    data = []
    for i in results:
        data.append(i)
    data_dict = json.dumps({"data":data}, indent=4, sort_keys=True, default=str)
    return jsonify(json.loads(data_dict))

@app.route('/listarEventoEspecifico', methods=['GET'])
@jwt_required()
def listar_evento_por_campo():
    codigo = request.args.get('codigo')
    fecha = request.args.get('fecha')
    if codigo is None and fecha is None:
        response = {'respuesta': "Ningún parámetro enviado"}
        return jsonify(response)
    if codigo and fecha:
        response = {'respuesta': "Solo envie un parámetro a la vez"}
        return jsonify(response)
    if app.config['TESTING'] is True:
        database = os.getenv('TEST_DATABASE')
    else:
        database = os.getenv('DATABASE')
    conn = psycopg2.connect(host=host, database=database, user=user, password=password, cursor_factory=RealDictCursor)
    if codigo:
        sql = f"SELECT * FROM eventos WHERE codigo = '{codigo}'"
    elif fecha:
        sql = f"SELECT * FROM eventos WHERE fecha <= '{fecha}'"
    cur = conn.cursor()
    cur.execute(sql)
    results = cur.fetchall()
    cur.close()
    data = []
    for i in results:
        data.append(i)
    data_dict = json.dumps({"data":data}, indent=4, sort_keys=True, default=str)
    return jsonify(json.loads(data_dict))

@app.route('/actualizarEvento', methods=['PUT'])
@jwt_required()
def actualizar_evento():
    content = request.json
    try:
        fecha = content["fecha"]
        nombre = content["nombre"]
        longitud = content["longitud"]
        latitud = content["latitud"]
        codigo = content["codigo"]
    except Exception as err:
        response = {'respuesta': "Campos faltantes por enviar"}
        return jsonify(response)

    if fecha == "" or nombre == "" or longitud == "" or latitud == "" or codigo == "":
        response = {'respuesta': "Algunos campos están en blanco"}
        return jsonify(response)

    if type(longitud) is not float or type(latitud) is not float:
        response = {"respuesta":"Formato erróneo en las coordenadas, ejemplo correcto: 4.34123 sin comillas"}
        return jsonify(response)
    try:
        validacion_fecha = datetime.strptime(fecha, f'%Y-%m-%d %H:%M')
    except Exception as err:
        response = {'respuesta': "Formato erróneo en la fecha, debe ser: YYYY-MM-DD HH:MM"}
        return jsonify(response)
    if app.config['TESTING'] is True:
        database = os.getenv('TEST_DATABASE')
    else:
        database = os.getenv('DATABASE')
    conn = psycopg2.connect(host=host, database=database, user=user, password=password, cursor_factory=RealDictCursor)
    cur = conn.cursor()
    cur.execute("UPDATE eventos SET fecha = %(x)s, nombre = %(y)s, latitud = %(i)s, longitud = %(j)s WHERE codigo = %(z)s", {'x':fecha, 'y':nombre, 'z':codigo, 'i':latitud, 'j':longitud})
    conn.commit()
    cuenta = cur.rowcount
    if cuenta == 0:
        response = {"respuesta":"Evento no encontrado"}
        return jsonify(response)
    with open("eventos.json", "r") as jsonFile:
        data = json.load(jsonFile)

    data[codigo] = {"latitud": latitud, "longitud": longitud}

    with open("eventos.json", "w") as jsonFile:
        json.dump(data, jsonFile)
    response = {"respuesta":"Evento Actualizado"}
    return jsonify(response)

@app.route('/eliminarEvento', methods=['DELETE'])
@jwt_required()
def eliminar_evento():
    content = request.json
    try:
        codigo = content["codigo"]
    except Exception as err:
        response = {'respuesta': "Se debe enviar el código del evento"}
        return jsonify(response)
    
    if app.config['TESTING'] is True:
        database = os.getenv('TEST_DATABASE')
    else:
        database = os.getenv('DATABASE')
    conn = psycopg2.connect(host=host, database=database, user=user, password=password)
    cur = conn.cursor()
    cur.execute("DELETE FROM eventos WHERE codigo = %(x)s", {'x':codigo})
    conn.commit()
    cuenta = cur.rowcount
    if cuenta == 0:
        response = {"respuesta":"Evento no encontrado"}
        return jsonify(response)
    cur.close()
    with open("eventos.json", "r") as jsonFile:
        data = json.load(jsonFile)

    del data[codigo]

    with open("eventos.json", "w") as jsonFile:
        json.dump(data, jsonFile)
    response = {"respuesta":"Evento Eliminado"}
    return jsonify(response)

@app.route('/obtenerDireccion', methods=['POST'])
@jwt_required()
def obtener_direccion():
    content = request.json
    try:
        codigo = content["codigo"]
        radio = int(content["radio"])
    except Exception as err:
        response = {'respuesta': "Campos faltantes por enviar"}
        return jsonify(response)

    if int(radio) < 1 or int(radio) > 50:
        response = {"respuesta":"El rango del radio debe estar entre 1 y 50"}
        return jsonify(response)
    
    with open("eventos.json", "r") as jsonFile:
        data = json.load(jsonFile)
    
    evento = data.get(codigo, None)
    if evento is None:
        response = {'respuesta': "Evento no encontrado"}
        return jsonify(response)
    api_key = os.getenv('API_KEY_GOOGLE')
    latitud = evento["latitud"]
    longitud = evento["longitud"]
    radio *= 1000
    nearby = requests.get(f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={latitud}%2C{longitud}&radius={radio}&key={api_key}")
    datos = json.loads(nearby.text)
    puntos_de_referencia = []
    for resultado in datos["results"]:
        for tipo in resultado["types"]:
            if tipo == "point_of_interest":
                dato ={
                    "nombre_lugar": resultado["name"],
                    "direccion": resultado["vicinity"],
                }
                puntos_de_referencia.append(dato)

    reverse_geocode_result = requests.get(f"https://maps.googleapis.com/maps/api/geocode/json?latlng={latitud},{longitud}&key={api_key}")
    datos = json.loads(reverse_geocode_result.text)
    localizado = False
    for resultado in datos["results"]:
        for tipo in resultado["types"]:
            if tipo == "point_of_interest":
                localizado = True
        if localizado is True:
            direccion = resultado["formatted_address"]
            break
    if localizado is False:
        response = {"respuesta":"No se encontraron puntos de referencia, actualizar las coordenadas del evento con más decimales o probar con otras"}
        return jsonify(response)
      
    response = {"Direccion":direccion, "Puntos_de_referencia":puntos_de_referencia}
    return jsonify(response)

@app.route('/registrarAsistentes', methods=['POST'])
@jwt_required()
def registrar_asistentes():
    content = request.json
    try:
        codigo = content["codigo"]
        asistentes = content["asistentes"]
    except Exception as err:
        response = {'respuesta': "Campos faltantes por enviar"}
        return jsonify(response)
    validacion = isinstance(asistentes, list)
    if validacion is False:
        response = {'respuesta': "El campo asistentes debe ser una lista o arreglos de correos, también de nombres, pero no recibiría notificación"}
        return jsonify(response)
    if app.config['TESTING'] is True:
        database = os.getenv('TEST_DATABASE')
    else:
        database = os.getenv('DATABASE')
    conn = psycopg2.connect(host=host, database=database, user=user, password=password)
    cur = conn.cursor()
    cur.execute("UPDATE eventos SET asistentes = %(x)s WHERE codigo = %(z)s", {'x':asistentes, 'z':codigo})
    conn.commit()
    cuenta = cur.rowcount
    print(cuenta)
    if cuenta == 0:
        response = {"respuesta":"Evento no encontrado"}
        return jsonify(response)
    cur.close()
    response = {"respuesta":"Asistentes registrados"}
    return jsonify(response)




