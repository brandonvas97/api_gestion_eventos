import psycopg2
import os
import json
from dotenv import load_dotenv
from os.path import join, dirname
from psycopg2.extras import RealDictCursor

ruta_archivo_env = join(dirname(__file__), 'cred.env')
load_dotenv(ruta_archivo_env)

host = os.getenv('HOST')
user = os.getenv('USER')
password = os.getenv('PASSWORD_BD')

class eventos:
    def __init__(self, fecha: str, nombre: str, longitud: float, latitud: float, codigo: str):
        self.fecha = fecha
        self.nombre = nombre
        self.longitud = longitud
        self.latitud = latitud
        self.codigo = codigo
        
        
    def acceder_evento(self):
        evento_dict = {
            "fecha" : self.fecha,
            "nombre" : self.nombre,
            "longitud" : self.longitud,
            "latitud" : self.latitud
        }
        return evento_dict
    
    def crear_evento(self, database):
        fecha = self.fecha
        nombre = self.nombre
        latitud = self.latitud
        longitud = self.longitud
        codigo = self.codigo
        conn = psycopg2.connect(host=host, database=database, user=user, password=password)
        sql = "INSERT INTO eventos(fecha, nombre, codigo, latitud, longitud, asistentes) VALUES %s"
        cur = conn.cursor()
        cur.execute("INSERT INTO eventos(fecha, nombre, codigo, latitud, longitud, asistentes) VALUES( %(x)s, %(y)s, %(z)s, %(i)s, %(j)s, %(k)s )", {'x':fecha, 'y':nombre, 'z':codigo, 'i':latitud, 'j':longitud, 'k':["Sin Asignar"]})
        conn.commit()
        return "Exitoso"

    def crear_tabla():
        pass
    
    def eliminar_tabla(database):
        conn = psycopg2.connect(host=host, database=database, user=user, password=password)
        sql = f"""TRUNCATE eventos RESTART IDENTITY CASCADE;"""
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        cur.close()
        return "Exitoso"

