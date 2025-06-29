# MODELOS CONVERTIDOS A MONGOENGINE

from mongoengine import (
    Document, EmbeddedDocument, StringField, IntField, DecimalField,
    DateField, DateTimeField, ReferenceField, CASCADE, PULL, NULLIFY,
    ListField, EmbeddedDocumentField
)
from datetime import date
from django.utils.translation import gettext_lazy as _

# --------------------
# ABSTRACT BASE CLASS
# --------------------
class NombreAbstract(Document):
    meta = {
        'abstract': True,
        'ordering': ['nombre']
    }
    nombre = StringField(max_length=50, required=True, help_text=_('Nombre descriptivo'))

    def clean(self):
        if self.nombre:
            self.nombre = self.nombre.upper()

    def __str__(self):
        return self.nombre

# --------------------
# PROVINCIA
# --------------------
class Provincia(NombreAbstract):
    def clean(self):
        super().clean()
        if Provincia.objects(nombre=self.nombre, id__ne=self.id).first():
            raise ValueError(_('Ya existe una provincia con este nombre.'))

# --------------------
# CIUDAD
# --------------------
class Ciudad(NombreAbstract):
    provincia = ReferenceField(Provincia, reverse_delete_rule=CASCADE, required=True)

    def clean(self):
        super().clean()
        if Ciudad.objects(nombre=self.nombre, provincia=self.provincia, id__ne=self.id).first():
            raise ValueError(_('Ya existe una ciudad con este nombre en esta provincia.'))

# --------------------
# DIRECCION
# --------------------
class Direccion(Document):
    calle = StringField(max_length=50, required=True)
    numero = IntField(required=True, min_value=0)
    ciudad = ReferenceField(Ciudad, reverse_delete_rule=CASCADE, required=True)

    def __str__(self):
        return f"{self.calle} {self.numero}, {self.ciudad.nombre}"

    meta = {
        'ordering': ['ciudad.nombre', 'calle']
    }

# --------------------
# TIPO DE DOCUMENTO
# --------------------
class TipoDocumento(NombreAbstract):
    def clean(self):
        super().clean()
        if TipoDocumento.objects(nombre=self.nombre, id__ne=self.id).first():
            raise ValueError(_('Ya existe un tipo de documento con este nombre.'))

# --------------------
# SUCURSAL
# --------------------
class Sucursal(NombreAbstract):
    direccion = ReferenceField(Direccion, reverse_delete_rule=CASCADE, required=True)

    def clean(self):
        super().clean()
        if Sucursal.objects(nombre=self.nombre, id__ne=self.id).first():
            raise ValueError(_('Ya existe una sucursal con este nombre.'))

# --------------------
# EMPLEADO
# --------------------
class Empleado(Document):
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
        return f"{self.nombre} {self.apellido} (Sucursal: {self.sucursal.nombre})"

    meta = {
        'ordering': ['apellido', 'nombre']
    }

# --------------------
# TIPO VEHICULO
# --------------------
class TipoVehiculo(NombreAbstract):
    def clean(self):
        super().clean()
        if TipoVehiculo.objects(nombre=self.nombre, id__ne=self.id).first():
            raise ValueError(_('Ya existe un tipo de vehículo con este nombre.'))

# --------------------
# CLIENTE
# --------------------
class Cliente(Document):
    nombre = StringField(max_length=50, required=True)
    apellido = StringField(max_length=50, required=True)
    telefono = StringField(max_length=20, null=True)
    nro_documento = IntField(unique=True, required=True)
    tipo_documento = ReferenceField(TipoDocumento, reverse_delete_rule=NULLIFY, required=True)
    direccion = ReferenceField(Direccion, reverse_delete_rule=CASCADE, required=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    meta = {
        'ordering': ['apellido', 'nombre'],
        'indexes': [
            {'fields': ['nro_documento']}
        ]
    }

# --------------------
# VEHICULO
# --------------------
class Vehiculo(Document):
    patente = StringField(max_length=10, primary_key=True)
    capacidad_carga = DecimalField(precision=2, required=True)
    empleado = ReferenceField(Empleado, reverse_delete_rule=CASCADE, required=True)
    tipo_vehiculo = ReferenceField(TipoVehiculo, reverse_delete_rule=NULLIFY, required=True)

    def capacidad_restante(self):
        carga_total = sum([
            p.peso for p in Paquete.objects(envio__vehiculo=self, envio__estado=Envio.EstadoEnvio.EN_CAMINO)
        ])
        return self.capacidad_carga - carga_total

    def __str__(self):
        return f"{self.patente} - {self.tipo_vehiculo.nombre}"

    meta = {
        'ordering': ['patente']
    }

# --------------------
# ENVIO
# --------------------
class Envio(Document):
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

# --------------------
# PAQUETE
# --------------------
class Paquete(Document):
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
