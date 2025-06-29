from django.contrib import admin

from .models_mongoengine import (
    Provincia, Ciudad, Direccion, TipoDocumento, Sucursal,
    Empleado, TipoVehiculo, Cliente, Vehiculo, Envio, Paquete
)
from .forms import ProvinciaForm, CiudadForm, SucursalForm, TipoDocumentoForm, TipoVehiculoForm

@admin.register(Provincia)
class ProvinciaAdmin(admin.ModelAdmin):
    form = ProvinciaForm
    list_display = ("id", "nombre")
    search_fields = ("nombre",)

@admin.register(Ciudad)
class CiudadAdmin(admin.ModelAdmin):
    form = CiudadForm
    list_display = ("id", "nombre", "provincia")
    list_filter = ("provincia",)
    search_fields = ("nombre", "provincia__nombre")

@admin.register(Direccion)
class DireccionAdmin(admin.ModelAdmin):
    list_display = ("id", "calle", "numero", "ciudad")
    list_filter = ("ciudad",)
    search_fields = ("calle", "ciudad__nombre")

@admin.register(TipoDocumento)
class TipoDocumentoAdmin(admin.ModelAdmin):
    form = TipoDocumentoForm
    list_display = ("id", "nombre")
    search_fields = ("nombre",)

@admin.register(Sucursal)
class SucursalAdmin(admin.ModelAdmin):
    form = SucursalForm
    list_display = ("id", "nombre", "direccion", "ciudad", "provincia")
    search_fields = ("nombre", "direccion__calle", "direccion__ciudad__provincia__nombre")

    def ciudad(self, obj):
        return obj.direccion.ciudad
    ciudad.short_description = "Ciudad"
    
    def provincia(self, obj):
        return obj.direccion.ciudad.provincia
    provincia.short_description = "Provincia"

@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "apellido", "nro_documento","tipo_documento", "sucursal", "fecha_contratacion" ,"antiguedad")
    list_filter = ("sucursal", "tipo_documento")
    search_fields = ("nombre", "apellido", "nro_documento")

@admin.register(TipoVehiculo)
class TipoVehiculoAdmin(admin.ModelAdmin):
    form = TipoVehiculoForm
    list_display = ("id", "nombre")
    search_fields = ("nombre",)

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "apellido", "telefono", "nro_documento", "direccion")
    list_filter = ("tipo_documento",)  # <-- corregido, ahora es tupla
    search_fields = ("nombre", "apellido", "nro_documento", "telefono")

@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ("patente", "tipo_vehiculo", "empleado", "capacidad_carga", "capacidad_restante")
    list_filter = ("tipo_vehiculo", "empleado")
    search_fields = ("patente", "empleado__nombre", "empleado__apellido")

@admin.register(Envio)
class EnvioAdmin(admin.ModelAdmin):
    list_display = ("id", "fecha_envio", "estado", "cliente", "sucursal", "vehiculo")
    list_filter = ("estado", "sucursal", "fecha_envio")
    search_fields = ("cliente__nombre", "cliente__apellido", "cliente__nro_documento")

@admin.register(Paquete)
class PaqueteAdmin(admin.ModelAdmin):
    list_display = ("id", "descripcion","dimensiones","peso", "ancho", "alto", "longitud", "envio")
    list_filter = ("envio",)
    search_fields = ("envio__cliente__nombre", "envio__cliente__apellido")

    def cliente(self, obj):
        return obj.envio.cliente
    cliente.short_description = "Cliente"