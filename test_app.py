import os
import unittest
import json
from flask import Flask
from flask_testing import TestCase
from app import app, jwt
from modelos import eventos
from dotenv import load_dotenv
from os.path import join, dirname
from datetime import datetime
from flask_jwt_extended import create_access_token
from googleplaces import GooglePlaces

ruta_archivo_env = join(dirname(__file__), 'cred.env')
load_dotenv(ruta_archivo_env)

class MainTestCase(TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        return app

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_crear_token(self):
        print("==========Comienzo pruebas unitarias==========")
        usuario = 'test'
        contraseña = '12345'
        response = self.client.post(
            '/iniciarSesion',
            data=json.dumps(dict(usuario=usuario, contraseña=contraseña)),
            content_type='application/json'
        )
        data = json.loads(response.data.decode())
        self.assertIn('token', data)
        self.assertIn('id_usuario', data)

    def test_crear_evento(self):
        fecha = '2023-01-01 00:00'
        nombre = 'Nombre del evento'
        longitud = -74.0772952
        latitud = 4.6491577
        response = self.client.post(
            '/crearEvento',
            data=json.dumps(dict(fecha=fecha, nombre=nombre, longitud=longitud, latitud=latitud)),
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {create_access_token("testuser")}')
        )
        data = json.loads(response.data.decode())
        self.assertIn('respuesta', data)
        self.assertEqual(data['respuesta'], 'Evento creado')

    def test_listar_eventos(self):
        response = self.client.get(
            '/listarEventos',
            headers=dict(Authorization=f'Bearer {create_access_token("testuser")}')
        )
        data = json.loads(response.data.decode())
        self.assertIn('data', data)
        self.assertIsInstance(data['data'], list)

    def test_listar_evento_especifico(self):
        codigo = app.config["CODIGO_TEST"]
        fecha = '2023-01-01 00:00'
        response = self.client.get(
            f'/listarEventoEspecifico?codigo={codigo}',
            headers=dict(Authorization=f'Bearer {create_access_token("testuser")}')
        )
        data = json.loads(response.data.decode())
        self.assertIn('data', data)
        self.assertIsInstance(data['data'], list)
        response = self.client.get(
            f'/listarEventoEspecifico?fecha={fecha}',
            headers=dict(Authorization=f'Bearer {create_access_token("testuser")}')
        )
        data = json.loads(response.data.decode())
        self.assertIn('data', data)
        self.assertIsInstance(data['data'], list)

    def test_n_actualizar_evento(self):
        print("test_update_evento")
        codigo = app.config["CODIGO_TEST"]
        fecha = '2023-01-01 00:00'
        nombre = 'Nombre del evento Actualizado'
        longitud = -74.0772952
        latitud = 4.6491577
        response = self.client.put(
            f'/actualizarEvento',
            data=json.dumps(dict(codigo=codigo, fecha=fecha, nombre=nombre, longitud=longitud, latitud=latitud)),
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {create_access_token("testuser")}')
        )
        data = json.loads(response.data.decode())
        self.assertIn('respuesta', data)
        self.assertEqual(data['respuesta'], 'Evento Actualizado')

    def test_s_eliminar_evento(self):
        print("test_y_eliminar_evento")
        codigo = app.config["CODIGO_TEST"]
        response = self.client.delete(
            f'/eliminarEvento',
            data=json.dumps(dict(codigo=codigo)),
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {create_access_token("testuser")}')
        )
        data = json.loads(response.data.decode())
        self.assertIn('respuesta', data)
        self.assertEqual(data['respuesta'], 'Evento Eliminado')

    def test_obtener_direccion_puntos_referencia(self):
        codigo = app.config["CODIGO_TEST"]
        radio = 5
        response = self.client.post(
            f'/obtenerDireccion',
            data=json.dumps(dict(codigo=codigo, radio=radio)),
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {create_access_token("testuser")}')
        )
        data = json.loads(response.data.decode())
        self.assertIn('Direccion', data)
        self.assertIn('Puntos_de_referencia', data)
        self.assertIsInstance(data['Direccion'], str)
        self.assertIsInstance(data['Puntos_de_referencia'], list)
    
    def test_registrar_asistentes(self):
        codigo = app.config["CODIGO_TEST"]
        asistentes = ['Asistente 1', 'Asistente 2']
        response = self.client.post(
            f'/registrarAsistentes',
            data=json.dumps(dict(codigo=codigo, asistentes=asistentes)),
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {create_access_token("testuser")}')
        )
        data = json.loads(response.data.decode())
        self.assertIn('respuesta', data)
        self.assertEqual(data['respuesta'], 'Asistentes registrados')
    
    def test_z_finalizar(self):
        print("tearDown")
        database = os.getenv('TEST_DATABASE')
        print("tearDown: ", database)
        eventos.eliminar_tabla(database)
        print("==========Final pruebas unitarias==========")

if __name__ == '__main__':
    unittest.main()