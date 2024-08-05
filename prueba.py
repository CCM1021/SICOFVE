import psycopg2
import datetime

fecha_actual=datetime.datetime.now()
hora_actual = datetime.datetime.now().strftime("%H:%M:%S")
conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres", password="1606", port="5432")

cur = conn.cursor()


cur.execute("""CREATE TABLE IF NOT EXISTS camera (
    id SERIAL PRIMARY KEY,
    clase varchar(255),
    speed integer,
    way varchar (255),
    fecha varchar(255)
); """)


consulta = """INSERT INTO camera ( clase, speed, way, fecha) 
              VALUES ( %s, %s, %s, %s);"""

# Datos a insertar
datos = [
    ('Car', 45, 'going up', fecha_actual),
    ('Motorbike', 90, 'going down', fecha_actual),
    ('Truck', 30, 'going down', fecha_actual)
]

# Ejecutar la consulta para cada conjunto de datos
cur.executemany(consulta, datos)
conn.commit()



cur.close()
conn.close()