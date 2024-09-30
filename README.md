# Sistema de Conteo y Clasificación de Flujo Vehicular y Peatonal (SICOFVE) y Sistema de Visualización de Tránsito Vehicular (SIVIT)

### Descripción: 
Este repositorio es el resultado de investigación y puesta en práctica del proyecto SICOFVE, relacionado al Programa de Infraestructura Resilente y Movilidad Sostenible (PIREMOS) y el Centro de Investigación en Vivienda y Construcción (CIVCO), del Instituto Tecnológico de Costa Rica (TEC).

Este proyecto es totalmente sin fines de lucro y se realiza con el objetivo de tener el conteo de todo tipo de tránsito vehicular de algunas zonas específicas de Costa Rica, para así tener el respaldo específico para toma de decisiones en aspectos de Seguridad Vial en nuestras carreteras.

Desarrollado por Carlos Cerdas Mora en conjunto con el profesor Dr. Irving Pizarro Marchena.
### Contactos:

Correo: cacerdasm@estudiantec.cr o carlosadriancerdas28@gmail.com
Correo: ipizarro@itcr.ac.cr




## Agradecimientos
Este repositorio está basado en un modelo preentrenado de detección de vehículos en general, el cual se adaptó a los objetivos del proyecto de investigación.

### Enlace de referencia:
https://gitlab.com/Kazymov_006/traffic-flow-prediction

Thanks to the developer in charge of this project.

## Requisitos
Windows 10, python 3.10
Si tiene otro sistema operativo, es necesario cambiar la dirección de URL para el pytorch en el archivo de pyproject.toml 

## Estructura del proyecto:

***Sistema de Visión:*** Utiliza la cámara OpenMV que cuenta con un script que genera un `stream` dentro de la red WiFi más cercana, en el puerto `8080`. Busque esta programación en MicroPython en el directorio `./progra_camara/main.py`. Para más detalles visualice el `.README`

***Sistema de Clasificación, Conteo y Medición de Velocidad:*** Utiliza la librería de OpenCV y YOLO para la detección de vehículos y tránsito general. Esta sección se mantuvo del modelo previo. Esta ejecución se hace por medio de la aplicación `SICOFVE`

***Base de Datos:*** Utiliza una base de datos local por medio de PostgreSQL. Dentro de `main.py` se encuentran las siguientes líneas para la conexión a la misma. Esta ejecución se hace por medio de la aplicación `SICOFVE`.
```
# Configuración de la base de datos
conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres", password="1606", port="5432")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS camera (
    id SERIAL PRIMARY KEY,
    clase varchar(255),
    speed varchar(255),
    way varchar (255),
    fecha varchar(255),
    camara varchar(255)
);
""")
consulta = """INSERT INTO camera (clase, speed, way, fecha, camara) VALUES (%s, %s, %s, %s, %s);"""
```

Luego realiza la inserción de los datos justo cuando el algoritmo detecta el conteo.


***Sistema de Visualización de los Datos Procesados:***
Esta sección está a cargo del SIVIT, donde se puede observar los datos en función del registro del nombre de la cámara, la dirección de movimiento y la clasificación dada en conjunto con la fecha de registro. Cuando se realiza la consulta se obtiene un resumen del conteo y aspectos como velocidad máxima, mínima y promedio.



## Pasos de instalación de herramienta OpenMV:

Siga el siguiente tutorial para la instalación del entorno de programación en MicroPython `OpenMV`.

Documentación: https://docs.openmv.io/openmvcam/tutorial/index.html

Tutorial: https://www.youtube.com/watch?v=6xr5K1NalBQ&t=51s&pp=ygUMb3Blbm12IGluc3Rh


## Pasos de instalación para PostgreSQL:
Siga el siguiente tutorial para la instalación del `pgadmin`.

Link - https://www.pgadmin.org/download/
Tutorial - https://www.youtube.com/watch?v=0n41UTkOBb0&pp=ygUUcGdhZG1pbiBpbnN0YWxsYXRpb24%3D

## Pasos de instalación para SIVIT y SICOFVE
### SIVIT (Sistema de Visualización de Tránsito Vehicular)

- Para el funcionamiento de este sistema es imperativo que exista la aplicación de `Postgresql` en el computador. Cabe aclarar que de momento la base de datos es local dentro del computador, por lo que cada nuevo computador que se utilice para procesar, generará una base de datos local. 

Ubique el archivo de Python `SiViT.py` y ábralo en un estudio de programación. 

Ejecute en la terminal el siguiente comando:
```bash
pyinstaller --onefile --windowed .\SiViT.py
```

Este comando genera una carpeta llamada `dist` en el mismo directorio donde estamos trabajando y ahí se puede encontrar el archivo de la aplicación.

Abra la carpeta `dist` y cree un acceso directo al escritorio de este archivo.

- Es probable que al ejecutar la aplicación por primera vez no cuente con las librerías necesarias instaladas, por lo que se pueden instalar de la siguiente forma:
 ``` bash
 pip install tracker
 ```
`tracker` es un ejemplo de una de las librerias que puede no estar instalada.

Sí se encuentran otro tipo de errores relacionados a la base de datos o otro problema mayor, es preferible que se comunique al correo anclado.





### SICOFVE (Sistema de Conteo y Clasificación de Flujo Vehicular y Peatonal)
- Para el funcionamiento de este sistema es imperativo que exista la aplicación de `Postgresql` en el computador. Siga el  tutorial para la instalación del `pgadmin`. El sistema **crea** automáticamente la base de datos con todos los parámetros necesarios si no están definidos. Cabe aclarar que de momento la base de datos es local dentro del computador, por lo que cada nuevo computador que se utilice para procesar, generará una base de datos local. 

Para la instalación de este sistema es similar a la anterior pero este sistema utiliza tres modulos que funcionan en conjunto los cuales deben de encontrarse dentro del repositorio y sino se encuentran comuniquelo con el desarrollador. Los archivos son `main.py`, `vision.py` y `camera_dialog.py`. Ejecute el siguiente comando para la instalación del sistema.

```bash
pyinstaller --onefile --windowed --add-data ".\main.py;." --add-data ".\camera_dialog.py;." .\vision.py
```

Al igual que el anterior, este comando realiza la fusión de los tres archivos juntos y genera una carpeta llamada `dist`, por lo que para el correcto funcionamiento, acceda a la misma, copie y pegue el archivo `vision` dentro de la carpeta raíz, osea fuera de la carpeta de `dist`, ya que para el correcto funcionamiento del sistema el debe de tener en el mismo directorio los archivos de `main.py` y el `camera_dialog.py`.

Si desea puede cambiarle el nombre a la aplicación por `SICOFVE`. De igual forma genere un acceso directo al escritorio. 

Recordar que este archivo utiliza los requisitos previos de librerías por lo que si no están instaladas va a presentar un error.


### Tutorial de funcionamiento de los sistemas

Ubique en el repositorio el archivo PDF `Tutorial_de_Funcionamiento_SICOFVE_y_SIVIT.pdf`, este es el tutorial general de funcionamiento de los sistemas.










## Aspectos a Mejorar
- Conexión a Base de Datos remota para centralizar todos los datos procesados.
- Implementación de algoritmos de procesamiento digital de señales para mejorar la calidad del conteo y evitar errores de pérdida de frames.
- Diseño de la interfaz de usuario de ambos sistemas para una posible migración al acceso web.
- Centralizar los datos dentro de un servidor.
- Centralizar el procesamiento dentro de un servidor.
- Entrenamiento de un modelo en función de los aspectos técnicos de clasificación de AASHTO.
- Creación del algoritmo de detección, Automedición y autocalibración de las líneas de conteo mediante el uso de `April Tags` en el piso, para de esta forma tener un valor específico de las distancias.

