from django import forms
from .models_mongoengine import Provincia, Ciudad, Sucursal, TipoDocumento, TipoVehiculo

class ProvinciaForm(forms.ModelForm):
    class Meta:
        model = Provincia
        fields = "__all__"

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre'].upper()
        if Provincia.objects.exclude(pk=self.instance.pk).filter(nombre=nombre).exists():
            raise forms.ValidationError('Ya existe una provincia con este nombre.')
        return nombre

class CiudadForm(forms.ModelForm):
    class Meta:
        model = Ciudad
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        nombre = cleaned_data.get('nombre')
        provincia = cleaned_data.get('provincia')
        if nombre and provincia:
            nombre = nombre.upper()
            if Ciudad.objects.exclude(pk=self.instance.pk).filter(nombre=nombre, provincia=provincia).exists():
                raise forms.ValidationError({'nombre': 'Ya existe una ciudad con este nombre en esta provincia.'})
            cleaned_data['nombre'] = nombre
        return cleaned_data

class SucursalForm(forms.ModelForm):
    class Meta:
        model = Sucursal
        fields = "__all__"

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre'].upper()
        if Sucursal.objects.exclude(pk=self.instance.pk).filter(nombre=nombre).exists():
            raise forms.ValidationError('Ya existe una sucursal con este nombre.')
        return nombre

class TipoDocumentoForm(forms.ModelForm):
    class Meta:
        model = TipoDocumento
        fields = "__all__"

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre'].upper()
        if TipoDocumento.objects.exclude(pk=self.instance.pk).filter(nombre=nombre).exists():
            raise forms.ValidationError('Ya existe un tipo de documento con este nombre.')
        return nombre

class TipoVehiculoForm(forms.ModelForm):
    class Meta:
        model = TipoVehiculo
        fields = "__all__"

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre'].upper()
        if TipoVehiculo.objects.exclude(pk=self.instance.pk).filter(nombre=nombre).exists():
            raise forms.ValidationError('Ya existe un tipo de vehículo con este nombre.')
        return nombre