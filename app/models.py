# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytz
from django.contrib.auth.models import User
from django.db import models

# Create your models here.

# class Index()
from django.utils.datetime_safe import datetime

_estado = (
    ('ACTIVO', ('ACTIVO')),
    ('INACTIVO', ('INACTIVO')),
)

_estado_tiquet = (
    ('1', ('EN JUEGO')),
    ('2', ('GANADO')),
    ('3', ('PERDIDO')),
    ('4', ('PAGADO')),
    ('5', ('CADUCADO')),
)


class Persona(models.Model):
    documento = models.IntegerField('Número de Cédula', unique=True)
    nombres = models.CharField('Nombre Taquillero', max_length=80, null=False)
    apellidos = models.CharField('Apellidos Taquillero', max_length=80, null=False)
    correo = models.EmailField('Correo Electronico', max_length=254, null=True, unique=True)

    def __unicode__(self):
        return "%s %s" % (self.nombres, self.apellidos)


class Grupo(models.Model):
    def get_count_taquillas(self):
        return Taquilla.objects.filter(grupo__id=self.id).count

    def get_taquillas(self):
        return Taquilla.objects.filter(grupo__id=self.id)

    def get_administrador(self):
        return Administrador.objects.filter(grupos__id=self.id).first()

    nombreGrupo = models.CharField('Nombre', max_length=100, unique=True)
    estado = models.CharField('Estado Grupo', choices=_estado, default='ACTIVO', max_length=10)
    propietarios = models.CharField('Propietarios', max_length=200, null=True)
    countTaquillas = property(get_count_taquillas)
    taquillas = property(get_taquillas)
    administrador = property(get_administrador)

    def save(self, force_insert=False, force_update=False, **kwargs):
        self.nombreGrupo = self.nombreGrupo.upper()
        super(Grupo, self).save(force_insert, force_update)

    def __unicode__(self):
        return self.nombreGrupo


class Taquilla(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='usuario', null=True)
    grupo = models.ForeignKey(Grupo, on_delete=models.CASCADE, related_name='grupo', null=True)

    def __unicode__(self):
        return self.usuario.username


class Administrador(models.Model):
    persona = models.OneToOneField(Persona, related_name='persona_administrador')
    usuario = models.OneToOneField(User, related_name='Usuario')
    grupos = models.ForeignKey(Grupo, related_name='Grupos')

    def __unicode__(self):
        return "%s %s" % (self.persona.nombres, self.persona.apellidos)


class Rifa(models.Model):
    def get_elements_count(self):
        return RifaLista.objects.filter(rifa__id=self.id).count

    def get_lista_elements(self):
        return RifaLista.objects.filter(rifa__id=self.id)

    nombre_rifa = models.CharField('Nombre Rifa', max_length=50, unique=True)
    elementos = property(get_elements_count)
    lista_elements = property(get_lista_elements)

    def __unicode__(self):
        return self.nombre_rifa


class RifaLista(models.Model):
    posicion = models.IntegerField('Posición')
    image = models.ImageField(upload_to='images/animales', max_length=100)
    nombre_imagen = models.CharField('Nombre Imagen', max_length=30)
    rifa = models.ForeignKey(Rifa, on_delete=models.CASCADE, related_name='rifa', null=True)

    def __unicode__(self):
        return '%s ---- %s ---- %s ' % (self.id, self.nombre_imagen, self.posicion)


class SorteoHora(models.Model):
    hora_sorteo = models.TimeField()
    rifa = models.ForeignKey(Rifa, on_delete=models.CASCADE, related_name='sorteo_horas', null=True)

    def __unicode__(self):
        return str(self.hora_sorteo)


class Sorteo(models.Model):
    rifa = models.ForeignKey(Rifa)
    sorteoHoras = models.ForeignKey(SorteoHora, on_delete=models.CASCADE, related_name='sorteo_horas', null=True)
    fecha_sorteo = models.DateField(null=True)
    numero_ganador = models.IntegerField()

    def __unicode__(self):
        return '%s / %s / %s' % (self.rifa.nombre_rifa, self.fecha_sorteo, self.sorteoHoras.hora_sorteo)


class Venta(models.Model):
    def get_detalles(self):
        return VentaDetalle.objects.filter(venta__id=self.id)

    taquilla = models.ForeignKey(Taquilla, on_delete=models.CASCADE, related_name='taquila')  # LISTO
    serial_cobro = models.CharField('Serial cobro', max_length=8, null=False)
    estado = models.CharField('Estado Venta', choices=_estado_tiquet, default='EN JUEGO', max_length=10)  # LISTO
    fecha = models.DateField('Fecha', null=True)  # LISTO
    time = models.TimeField('Hora', null=True)
    total_apostado = models.IntegerField(default=0)  # LISTO
    total_ganancia = models.IntegerField(default=0)
    list_detalles = property(get_detalles)
    fecha_pago = models.DateTimeField(null=True)
    usuarioPagador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='usuario_pagador', null=True)

    def __unicode__(self):
        return 'id: %s ---- fecha: %s ----- Hora: %s ---- Ganancia: %s' % (
            self.id, self.fecha, self.time, self.total_ganancia)


class VentaDetalle(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='venta')  # LISTO
    # detalle_rifa = models.ForeignKey(RifaLista, on_delete=models.CASCADE, related_name='detalle_rifa')  # LISTO
    sorteo = models.ForeignKey(Sorteo, on_delete=models.CASCADE, related_name='sorteo', null=True)  # LISTO
    valor_apuesta = models.IntegerField()  # LISTO
    estado = models.CharField('Estado Venta', choices=_estado_tiquet, default='EN JUEGO', max_length=10)  # LISTO
    tipo_apuesta = models.IntegerField(blank=True, null=True)
    numeros = models.CharField('Numeros apostados', null=True, blank=True, max_length=20)
    ganancia = models.IntegerField(null=True, blank=True)

    def __unicode__(self):
        return '%s ' % self.id


class EstadoSistema(models.Model):
    nombre = models.CharField('Nombre estado', max_length=100)
    estado = models.BooleanField('Estado')

    def __unicode__(self):
        return self.nombre


class Permisos(models.Model):
    permiso_name = models.CharField('Permiso', max_length=100, unique=True)
    permiso_uri = models.CharField('uri', max_length=30, blank=True, null=True, unique=True)
    tipo = models.CharField('Tipo Permiso', max_length=50, blank=True, null=True)

    def __unicode__(self):
        return self.permiso_name


class PermisoUsuario(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user', null=True)
    permiso = models.ForeignKey(Permisos, on_delete=models.CASCADE, related_name='permiso_usuario', null=True)

    def __unicode__(self):
        return self.usuario.username


class CronTabLog(models.Model):
    hora = models.TimeField()
    descripcion = models.CharField(max_length=150)

    def __unicode__(self):
        return str(self.hora)
