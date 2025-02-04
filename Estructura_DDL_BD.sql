CREATE TABLE usuarios(
	id SERIAL PRIMARY KEY,
	usuario VARCHAR(50),
	contraseña VARCHAR(200)
)


CREATE TABLE eventos(
	id SERIAL PRIMARY KEY,
	fecha TIMESTAMP,
	nombre VARCHAR(100),
	codigo VARCHAR(100),
	latitud REAL,
	longitud REAL,
	asistentes VARCHAR[]
)

TRUNCATE eventos RESTART IDENTITY CASCADE;