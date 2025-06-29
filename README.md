# Tutorial: Despliegue de una Aplicación MongoDB
Práctico de Mapeo Objeto-Documental para la materia, Bases de Datos de la carrera `Ingeniería en Sistemas` de la *`Universidad Tecnológica Nacional`* *`Facultad Regional Villa María`*.


![MongoDB 8.0.11](https://img.shields.io/badge/MongoDB%208.0.11-47A248?style=for-the-badge&logo=mongodb&logoColor=white)
![Python 3.13](https://img.shields.io/badge/Python%203.13-3776AB?style=for-the-badge&logo=python&logoColor=white)

**Referencia Rápida**

**Mantenido Por:** Grupo 8

## **Descargo de Responsabilidad:**
El código proporcionado se ofrece "tal cual", sin garantía de ningún tipo, expresa o implícita. En ningún caso los autores o titulares de derechos de autor serán responsables de cualquier reclamo, daño u otra responsabilidad.


## Introducción
Este tutorial te guiará paso a paso en la creación y despliegue de una aplicación Python con MongoEngine conectada a una base de datos MongoDB utilizando Docker y Docker Compose. El objetivo es levantar un entorno de desarrollo profesional, portable y fácil de mantener, ideal tanto para pruebas como para producción.

---


## Enunciado
Una empresa de transporte desea crear una base de datos para gestionar la información de sus operaciones logísticas. La empresa cuenta con varias sucursales, cada una identificada por un código, nombre, dirección y ciudad. En cada sucursal trabajan varios empleados, de los cuales se desea almacenar el número de empleado, nombre completo, puesto y fecha de contratación.

La empresa realiza envíos a través de diferentes vehículos, cada uno con un número de placa, tipo (camión, furgoneta, moto), capacidad de carga y el empleado que lo conduce habitualmente. Los clientes solicitan envíos proporcionando su número de identificación, nombre, dirección y número de contacto.

Cada envío se registra con un código único, fecha, origen, destino, estado del envío y el vehículo asignado. Además, cada envío puede contener uno o varios paquetes, con detalles como número de paquete, peso, dimensiones y descripción del contenido.

---

## 1. Estructura del Proyecto
Crea una carpeta para tu proyecto. En este ejemplo, la llamaremos `transporte`.

**Puedes copiar todo este bloque y pegarlo directamente en tu terminal o archivo correspondiente. Aqui clonaremos directamente el proyecto que desplegamos en Django, de esa forma solo realizaremos los cambios necesarios para el despliegue en MongoDB**
```sh
mkdir transporte_mongoDB
cd transporte_mongoDB/
git clone https://github.com/aldanaamante/Transporte
```

---

## 2. Configuración de `settings.py`
Edita el archivo `settings.py` para agregar tu app y configurar la base de datos usando las variables de entorno. A diferencia del settings.py de Django, aqui comentaremos aquellas lineas que hagan referencia a la base de datos relacional anteriormente usada y realizaremos la conexion directa a MongoDB con MongoEngine.

> **Puedes copiar todo este bloque y pegarlo directamente en tu archivo ./src/app/settings.py.**
```python
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-7pjgn=u0o+#12$%xoau+82^u1i9ur=@3g$+0jgq$9b3btw*-7k'

DEBUG = True
ALLOWED_HOSTS = [os.environ.get("ALLOWED_HOSTS", "*")]


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'transporte',  
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'app.wsgi.application'

# DESACTIVADO: BASE DE DATOS RELACIONAL
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# También queda anulada la opción condicional de PostgreSQL
# if USE_POSTGRES:
#     DATABASES = {...}
# else:
#     DATABASES = {...}

# CONEXIÓN A MONGODB CON MONGOENGINE
from mongoengine import connect

MONGODB_NAME = os.environ.get("MONGODB_NAME", "transporte")
MONGODB_HOST = os.environ.get("MONGODB_HOST", "localhost")
MONGODB_PORT = int(os.environ.get("MONGODB_PORT", 27017))

connect(
    db=MONGODB_NAME,
    host=MONGODB_HOST,
    port=MONGODB_PORT
)

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
```

## 3. Modelado de la Aplicación
Ahora debemos convertir el models.py de Django a MongoEngine, se recomienda crear una copia del models de Django (models.py) y ponerle otro nombre, en nuestro caso se llama models_mongoengine.py.

### Ejemplo de `models_mongoengine.py`
Incluye modelos bien documentados y estructurados para una gestión profesional de tus datos.

> **Puedes copiar todo este bloque y pegarlo directamente en tu archivo ./src/transporte/models_mongoengine.py.**
```python
from mongoengine import (
    Document, EmbeddedDocument, StringField, IntField, DecimalField,
    DateField, DateTimeField, ReferenceField, CASCADE, PULL, NULLIFY,
    ListField, EmbeddedDocumentField, SequenceField
)
from datetime import date
from django.utils.translation import gettext_lazy as _

class NombreAbstract(Document):
    id = SequenceField(primary_key=True)
    meta = {
        'abstract': True,
        'ordering': ['nombre']
    }
    nombre = StringField(max_length=50, required=True, help_text=_('Nombre descriptivo'))

    def clean(self):
        if self.nombre:
            self.nombre = self.nombre.upper()

    def __str__(self):
        return f"{self.nombre} (ID: {self.id})"

class Provincia(NombreAbstract):
    pass

class Ciudad(NombreAbstract):
    provincia = ReferenceField(Provincia, reverse_delete_rule=CASCADE, required=True)

class Direccion(Document):
    id = SequenceField(primary_key=True)
    calle = StringField(max_length=50, required=True)
    numero = IntField(required=True, min_value=0)
    ciudad = ReferenceField(Ciudad, reverse_delete_rule=CASCADE, required=True)

    def __str__(self):
        return f"{self.calle} {self.numero}, {self.ciudad.nombre} (ID: {self.id})"

    meta = {
        'ordering': ['ciudad.nombre', 'calle']
    }

class TipoDocumento(NombreAbstract):
    pass

class Sucursal(NombreAbstract):
    direccion = ReferenceField(Direccion, reverse_delete_rule=CASCADE, required=True)

class Empleado(Document):
    id = SequenceField(primary_key=True)
    nombre = StringField(max_length=50, required=True)
    apellido = StringField(max_length=50, required=True)
    nro_documento = IntField(unique=True, required=True)
    fecha_contratacion = DateField(required=True)
    direccion = ReferenceField(Direccion, reverse_delete_rule=CASCADE, required=True)
    sucursal = ReferenceField(Sucursal, reverse_delete_rule=CASCADE, required=True)
    tipo_documento = ReferenceField(TipoDocumento, reverse_delete_rule=NULLIFY, required=True)

    def antiguedad(self):
        if self.fecha_contratacion:
            hoy = date.today()
            diferencia = hoy.year - self.fecha_contratacion.year
            if (hoy.month, hoy.day) < (self.fecha_contratacion.month, self.fecha_contratacion.day):
                diferencia -= 1
            return f"{diferencia} años"
        return "0 años"

    def __str__(self):
        return f"{self.nombre} {self.apellido} (ID: {self.id}, Sucursal: {self.sucursal.nombre})"

    meta = {
        'ordering': ['apellido', 'nombre']
    }

class TipoVehiculo(NombreAbstract):
    pass

class Cliente(Document):
    id = SequenceField(primary_key=True)
    nombre = StringField(max_length=50, required=True)
    apellido = StringField(max_length=50, required=True)
    telefono = StringField(max_length=20, null=True)
    nro_documento = IntField(unique=True, required=True)
    tipo_documento = ReferenceField(TipoDocumento, reverse_delete_rule=NULLIFY, required=True)
    direccion = ReferenceField(Direccion, reverse_delete_rule=CASCADE, required=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido} (ID: {self.id})"

    meta = {
        'ordering': ['apellido', 'nombre'],
        'indexes': [
            {'fields': ['nro_documento']}
        ]
    }

class Vehiculo(Document):
    id = SequenceField(primary_key=True)
    patente = StringField(max_length=10, required=True, unique=True)
    capacidad_carga = DecimalField(precision=2, required=True)
    empleado = ReferenceField(Empleado, reverse_delete_rule=CASCADE, required=True)
    tipo_vehiculo = ReferenceField(TipoVehiculo, reverse_delete_rule=NULLIFY, required=True)

    def capacidad_restante(self):
        from models_mongoengine import Envio, Paquete
        envios_en_camino = Envio.objects(vehiculo=self, estado=Envio.EstadoEnvio.EN_CAMINO)
        carga_total = sum([
            p.peso for p in Paquete.objects(envio__in=envios_en_camino)
        ])
        return self.capacidad_carga - carga_total

    def __str__(self):
        return f"{self.patente} (ID: {self.id}) - {self.tipo_vehiculo.nombre}"

    meta = {
        'ordering': ['patente']
    }

class Envio(Document):
    id = SequenceField(primary_key=True)
    fecha_envio = DateTimeField(required=True)
    sucursal = ReferenceField(Sucursal, reverse_delete_rule=CASCADE, required=True)
    cliente = ReferenceField(Cliente, reverse_delete_rule=CASCADE, required=True)

    class EstadoEnvio:
        EN_CAMINO = 'EN_CAMINO'
        ENTREGADO = 'ENTREGADO'
        choices = [EN_CAMINO, ENTREGADO]

    estado = StringField(choices=EstadoEnvio.choices, default=EstadoEnvio.EN_CAMINO)
    vehiculo = ReferenceField(Vehiculo, reverse_delete_rule=CASCADE, required=True)

    def __str__(self):
        return f"Envío #{self.id} - {self.cliente} ({self.estado})"

    meta = {
        'ordering': ['-fecha_envio']
    }

class Paquete(Document):
    id = SequenceField(primary_key=True)
    peso = DecimalField(precision=2, required=True)
    ancho = DecimalField(precision=2, required=True)
    alto = DecimalField(precision=2, required=True)
    longitud = DecimalField(precision=2, required=True)
    descripcion = StringField(max_length=250, required=True)
    envio = ReferenceField(Envio, reverse_delete_rule=CASCADE, required=True)

    def dimensiones(self):
        if self.ancho and self.alto and self.longitud:
            dimensiones = self.ancho * self.alto * self.longitud
            return f"{dimensiones:.2f} cm³"
        return "0.00 cm³"

    def __str__(self):
        return f"Paquete #{self.id} del Envío #{self.envio.id}"

    meta = {
        'ordering': ['descripcion']
    }
```

---

## 4.Carga de Datos Iniciales

Cargar la base de datos con datos iniciales usando un script (Carga_Inicial.py). Para poder usar este script debemos tener, tanto el inital_data.json que usamos para Django como el archivo models_mongoengine,py en la misma ruta. De esta forma el script puede realizar los import necesarios para poder ejecutarse. 

> **Puedes copiar todo este bloque y pegarlo directamente en tu archivo Carga_inicial.py.**
```python
import json
from mongoengine import connect
from models_mongoengine import (
    Provincia, Ciudad, Direccion, TipoDocumento,
    Sucursal, Empleado, Cliente, TipoVehiculo,
    Vehiculo, Envio, Paquete
)

# Conexión a la base de datos MongoDB
connect(db="transporte", host="localhost", port=27017)

# Cargar datos desde el archivo JSON
with open('initial_data.json', encoding='utf-8') as f:
    data = json.load(f)

# Diccionarios para mapear IDs relacionales
prov_map = {}
ciudad_map = {}
dir_map = {}
tipo_doc_map = {}
sucursal_map = {}
empleado_map = {}
cliente_map = {}
tipo_vehiculo_map = {}
vehiculo_map = {}
envio_map = {}

for obj in data:
    model = obj["model"].split(".")[-1]
    pk = obj["pk"]
    fields = obj["fields"]

    if model == "Provincia":
        doc = Provincia(nombre=fields["nombre"])
        doc.save()
        prov_map[pk] = doc

    elif model == "Ciudad":
        doc = Ciudad(nombre=fields["nombre"], provincia=prov_map[fields["provincia"]])
        doc.save()
        ciudad_map[pk] = doc

    elif model == "Direccion":
        doc = Direccion(calle=fields["calle"], numero=fields["numero"], ciudad=ciudad_map[fields["ciudad"]])
        doc.save()
        dir_map[pk] = doc

    elif model == "TipoDocumento":
        doc = TipoDocumento(nombre=fields["nombre"])
        doc.save()
        tipo_doc_map[pk] = doc

    elif model == "Sucursal":
        doc = Sucursal(nombre=fields["nombre"], direccion=dir_map[fields["direccion"]])
        doc.save()
        sucursal_map[pk] = doc

    elif model == "TipoVehiculo":
        doc = TipoVehiculo(nombre=fields["nombre"])
        doc.save()
        tipo_vehiculo_map[pk] = doc

    elif model == "Empleado":
        doc = Empleado(
            nombre=fields["nombre"],
            apellido=fields["apellido"],
            nro_documento=fields["nro_documento"],
            fecha_contratacion=fields["fecha_contratacion"],
            direccion=dir_map[fields["direccion"]],
            sucursal=sucursal_map[fields["sucursal"]],
            tipo_documento=tipo_doc_map[fields["tipo_documento"]]
        )
        doc.save()
        empleado_map[pk] = doc

    elif model == "Cliente":
        doc = Cliente(
            nombre=fields["nombre"],
            apellido=fields["apellido"],
            telefono=fields.get("telefono"),
            nro_documento=fields["nro_documento"],
            tipo_documento=tipo_doc_map[fields["tipo_documento"]],
            direccion=dir_map[fields["direccion"]]
        )
        doc.save()
        cliente_map[pk] = doc

    elif model == "Vehiculo":
        doc = Vehiculo(
            patente=pk,
            capacidad_carga=float(fields["capacidad_carga"]),
            empleado=empleado_map[fields["empleado"]],
            tipo_vehiculo=tipo_vehiculo_map[fields["tipo_vehiculo"]]
        )
        doc.save()
        vehiculo_map[pk] = doc

    elif model == "Envio":
        doc = Envio(
            fecha_envio=fields["fecha_envio"],
            sucursal=sucursal_map[fields["sucursal"]],
            cliente=cliente_map[fields["cliente"]],
            estado=fields["estado"],
            vehiculo=vehiculo_map[fields["vehiculo"]]
        )
        doc.save()
        envio_map[pk] = doc

    elif model == "Paquete":
        doc = Paquete(
            peso=float(fields["peso"]),
            ancho=float(fields["ancho"]),
            alto=float(fields["alto"]),
            longitud=float(fields["longitud"]),
            descripcion=fields["descripcion"],
            envio=envio_map[fields["envio"]]
        )
        doc.save()

print("Se realizo la carga de datos correctamente :D")

```
> **Puedes copiar todo este bloque y pegarlo directamente en tu terminal. Este comando cargara directamente los datos a la base de datos y tambien realizara la conexion automaticamente a la base de datos.**
```sh
python Carga_inicial.py
```
---
### Visualizacion de Metodos en Python

MongoDB Compass no muestra funciones ni métodos definidos en los modelos de los ODMs como mongoengine porque Compass solo visualiza los datos almacenados realmente en la base de datos MongoDB. Compass NO muestra lógica de Python, ni modelos, ni métodos, ni validaciones, ni clases, ni funciones del backend. 
Las funciones como .antiguedad(), .dimensiones(), .capacidad_restante(), solo existen en Python.

#### Ejemplo de `funciones_mongoengine.py`

> **Puedes copiar todo este bloque y pegarlo directamente en tu archivo funciones_mongoengine.py.**
```python
from mongoengine import connect
from models_mongoengine import Empleado, Paquete, Vehiculo

connect(db='transporte', host='localhost', port=27017)

print("=== Empleados y su antigüedad ===")
for empleado in Empleado.objects:
    print(f"{empleado.nombre} {empleado.apellido}: {empleado.antiguedad()}")

print("\n=== Paquetes y sus dimensiones ===")
for paquete in Paquete.objects:
    print(f"Paquete #{paquete.id} - {paquete.descripcion}: {paquete.dimensiones()}")

print("\n=== Vehículos y su capacidad restante ===")
for vehiculo in Vehiculo.objects:
    try:
        restante = vehiculo.capacidad_restante()
    except Exception as e:
        restante = f"Error: {e}"
    print(f"{vehiculo.patente}: {restante}")
```
---

## 5. Accede a la administración de MongoDB donde ya se van a ver los cambios realizados en la app con datos pre cargados.

'''
> Es posible tambien ingresar elementos mediante la terminal de la siguiente forma. (Recordar estar parado en la misma ruta en la que este el archivo que usamos para crear los modelos.)
```python

python

from mongoengine import connect
from models_mongoengine import Provincia

connect(db="transporte", host="localhost", port=27017)

# Crear una nueva provincia
prov = Provincia(nombre="SAN JUAN")
prov.save()

# Verificar
print(prov)

#El elemento podra visualizarse tambien en Compass al actualizar la Base de datos.

```


---

## Conclusión
Con estos pasos, tendrás un entorno MongoDB profesional, portable y listo para desarrollo o producción. Recuerda consultar la documentación oficial de MongoDB para profundizar en cada tema. ¡Éxitos en tu proyecto!

---
