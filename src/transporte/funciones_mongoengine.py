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