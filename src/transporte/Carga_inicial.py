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

print("Se realizo la carga de datos correctamente.")
