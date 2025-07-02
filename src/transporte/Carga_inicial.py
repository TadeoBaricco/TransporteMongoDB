import json
from mongoengine import connect
from mongoengine.errors import NotUniqueError
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

def get_or_create(model, fields, pk, id_map):
    """
    Función auxiliar para crear un objeto o recuperarlo si ya existe.
    Esto es útil para campos con la restricción 'unique'.
    """
    try:
        # Intenta crear y guardar el nuevo documento.
        # El método clean se llamará automáticamente antes de guardar.
        doc = model(**fields)
        doc.save()
        print(f"Creado: {model.__name__} con nombre '{doc.nombre}'")
    except NotUniqueError:
        # Si falla por ser un duplicado, busca el existente.
        # Usamos el nombre en mayúsculas para la búsqueda, igual que en el 'clean'.
        doc = model.objects(nombre=fields["nombre"].upper()).first()
        print(f"Encontrado (ya existía): {model.__name__} con nombre '{doc.nombre}'")
    except Exception as e:
        print(f"Error inesperado creando {model.__name__} con datos {fields}: {e}")
        return
        
    id_map[pk] = doc


for obj in data:
    model_name = obj["model"].split(".")[-1]
    pk = obj["pk"]
    fields = obj["fields"]

    if model_name == "Provincia":
        get_or_create(Provincia, {"nombre": fields["nombre"]}, pk, prov_map)

    elif model_name == "Ciudad":
        fields['provincia'] = prov_map[fields["provincia"]]
        get_or_create(Ciudad, fields, pk, ciudad_map)
        
    elif model_name == "Direccion":
        doc = Direccion(
            calle=fields["calle"], 
            numero=fields["numero"], 
            ciudad=ciudad_map[fields["ciudad"]]
        )
        doc.save()
        dir_map[pk] = doc

    elif model_name == "TipoDocumento":
        get_or_create(TipoDocumento, {"nombre": fields["nombre"]}, pk, tipo_doc_map)

    elif model_name == "Sucursal":
        fields['direccion'] = dir_map[fields["direccion"]]
        get_or_create(Sucursal, fields, pk, sucursal_map)

    elif model_name == "TipoVehiculo":
        get_or_create(TipoVehiculo, {"nombre": fields["nombre"]}, pk, tipo_vehiculo_map)

    elif model_name == "Empleado":
        # Los campos nro_documento y otros pueden ser únicos también
        try:
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
        except NotUniqueError:
            print(f"Empleado con DNI {fields['nro_documento']} ya existe. Omitiendo.")

    elif model_name == "Cliente":
        try:
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
        except NotUniqueError:
            print(f"Cliente con DNI {fields['nro_documento']} ya existe. Omitiendo.")

    elif model_name == "Vehiculo":
        try:
            doc = Vehiculo(
                patente=pk,
                capacidad_carga=float(fields["capacidad_carga"]),
                empleado=empleado_map[fields["empleado"]],
                tipo_vehiculo=tipo_vehiculo_map[fields["tipo_vehiculo"]]
            )
            doc.save()
            vehiculo_map[pk] = doc
        except NotUniqueError:
            print(f"Vehículo con patente {pk} ya existe. Omitiendo.")

    elif model_name == "Envio":
        doc = Envio(
            fecha_envio=fields["fecha_envio"],
            sucursal=sucursal_map[fields["sucursal"]],
            cliente=cliente_map[fields["cliente"]],
            estado=fields["estado"],
            vehiculo=vehiculo_map[fields["vehiculo"]]
        )
        doc.save()
        envio_map[pk] = doc

    elif model_name == "Paquete":
        doc = Paquete(
            peso=float(fields["peso"]),
            ancho=float(fields["ancho"]),
            alto=float(fields["alto"]),
            longitud=float(fields["longitud"]),
            descripcion=fields["descripcion"],
            envio=envio_map[fields["envio"]]
        )
        doc.save()

print("\nSe completó la carga de datos.")