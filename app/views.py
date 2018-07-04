# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import print_function
from __future__ import unicode_literals

# Create your views here.
import os

from datetime import timedelta
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render
from django.template.defaulttags import now
from django.utils.datetime_safe import datetime, date, time
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.settings import api_settings

from .serializerPagados import PagadoSerializer
from .serializerVentaCompleto import VentaSerializerCompleto
from .serializerVentaTaquilla import VentaSerializerTaquilla
from permisoSerializer import PermisoSerializer
from serializerEstadoSistema import EstadoSistemaSerializer
from serializerGrupo import GrupoSerializer
from models import Grupo, Taquilla, Rifa, RifaLista, Sorteo, EstadoSistema, SorteoHora, Venta, VentaDetalle, \
    Permisos, PermisoUsuario
from serializerPermisoUsuario import PermisoUsuarioSerializer
from serializerRifaDetalle import RifaListaSerializer
from serializerRifa import RifaSerializer
from serializerTaquilla import TaquillaSerializer
from serializerUser import UserSerializer
from serializerVenta import VentaSerializer
from serializerVentaDetalle import VentaDetalleSerializer
from sorteoHoraSerializer import SorteoHoraSerializer
from sorteoSerializer import SorteoSerializer
from tasks import crear_sorteos, set_number_sorteo

import uuid

# LIB CRIPTOGRAFIA
import base64
import os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from django.http import HttpResponse, HttpResponseBadRequest

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
jwt_decode_handler = api_settings.JWT_DECODE_HANDLER


@csrf_exempt
def setSignature(request):
    print(request)
    if request.method == 'GET':
        message = request.GET.get('request')
    else:
        message = request.POST.get('request')

    if message == '' or message == None:
        return HttpResponseBadRequest("Signing request needs 'request' parameter")

    mykey = os.path.join(os.path.dirname(__file__), "qz-key/private-key.pem")
    mypass = ''  # mypass = ''  #

    # Load the private key
    key = serialization.load_pem_private_key(
        open(mykey).read(), password=None, backend=default_backend()
    )

    # Create the signature
    signature = key.sign(message.encode('utf-8'), padding.PKCS1v15(), hashes.SHA1())

    # Echo the signature
    return HttpResponse(base64.b64encode(signature), content_type="text/plain")


def Index(request):
    d = datetime.now()
    if d.minute >= 55:
        t = time(d.hour + 1, 0, 0)
    else:
        t = time(d.hour, d.minute + 5, 0)
    # t = time(d.hour, d.minute, 0)
    try:
        ultimo_sorteo = Sorteo.objects.filter(fecha_sorteo=d.date(), sorteoHoras__hora_sorteo__lte=t).order_by(
            '-sorteoHoras__hora_sorteo')

        if len(ultimo_sorteo) != 0:
            rifas = Rifa.objects.all()
            listResultados = []
            for rifa in rifas:
                sorteo_dia = Sorteo.objects.filter(fecha_sorteo=d.date(), rifa__id=rifa.id).order_by(
                    'sorteoHoras__hora_sorteo')
                result = {
                    'rifa': rifa.nombre_rifa,
                    'elementos': sorteo_dia
                }
                listResultados.append(result)

            listaSorteos = [ultimo_sorteo[0], ultimo_sorteo[1], ultimo_sorteo[2]]

            animaloto_sorteo = ""
            animaloto_imagen_result = ""
            parranda_sorteo = ""
            parranda_imagen_result = ""
            liga_sorteo = ""
            liga_imagen_result = ""

            for s in listaSorteos:
                if s.rifa.id == 8:
                    animaloto_sorteo = s
                    animaloto_imagen_result = RifaLista.objects.filter(rifa__id=s.rifa.id, posicion=s.numero_ganador)
                elif s.rifa.id == 9:
                    parranda_sorteo = s
                    parranda_imagen_result = RifaLista.objects.filter(rifa__id=s.rifa.id, posicion=s.numero_ganador)
                elif s.rifa.id == 10:
                    liga_sorteo = s
                    liga_imagen_result = RifaLista.objects.filter(rifa__id=s.rifa.id, posicion=s.numero_ganador)

            data = {
                'ultimo_sorteo_animaloto': animaloto_sorteo,
                'ultimo_sorteo_parranda': parranda_sorteo,
                'ultimo_sorteo_liga': liga_sorteo,
                'imagen_animalto': animaloto_imagen_result[0],
                'imagen_parranda': parranda_imagen_result[0],
                'imagen_liga': liga_imagen_result[0],
                'sorteo_dia': listResultados,
                'fecha': d.date(),
                'hora': d.time()
            }
        else:
            rifas = Rifa.objects.all()
            listResultados = []
            for rifa in rifas:
                sorteo_dia = Sorteo.objects.filter(fecha_sorteo=d.date(), rifa__id=rifa.id).order_by(
                    'sorteoHoras__hora_sorteo')
                result = {
                    'rifa': rifa.nombre_rifa,
                    'elementos': sorteo_dia
                }
                listResultados.append(result)
            data = {
                'hora': d.time(),
                'fecha': d.date(),
                'ultimo_sorteo': None,
                'sorteo_dia': listResultados
            }
        return render(request, 'index.html', data)
    except Exception as e:
        rifas = Rifa.objects.all()
        listResultados = []
        for rifa in rifas:
            sorteo_dia = Sorteo.objects.filter(fecha_sorteo=d.date(), rifa__id=rifa.id).order_by(
                'sorteoHoras__hora_sorteo')
            result = {
                'rifa': rifa.nombre_rifa,
                'elementos': sorteo_dia
            }
            listResultados.append(result)
        data = {
            'hora': d.time(),
            'fecha': d.date(),
            'ultimo_sorteo': None,
            'sorteo_dia': listResultados
        }
        '''
        fecha = datetime.today()
        sorteos = Sorteo.objects.filter(fecha_sorteo=fecha.date())
        '''
        return render(request, 'index.html', data)


class UltimoSorteoApiView(APIView):
    def get(self, request, format=None):
        d = datetime.now()
        if d.minute >= 55:
            t = time(d.hour + 1, 0, 0)
        else:
            t = time(d.hour, d.minute + 5, 0)

        try:
            ultimo_sorteo = Sorteo.objects.filter(fecha_sorteo=d.date(), sorteoHoras__hora_sorteo__lte=t).order_by(
                '-sorteoHoras__hora_sorteo')
            sorteo = ultimo_sorteo[0]
            imagen_result = RifaLista.objects.get(rifa__id=sorteo.rifa.id, posicion=sorteo.numero_ganador)
            sorteo_serializer = SorteoSerializer(sorteo, many=False)
            rifaserializer = RifaListaSerializer(imagen_result, many=False)
            response = {
                'message': '',
                'isOk': False,
                'isError': True,
                'content': sorteo_serializer.data,
                'imagen_ganadora': rifaserializer.data
            }
            return Response(response, status=status.HTTP_201_CREATED)

        except Exception as e:
            response = {
                'message': str(e),
                'isOk': False,
                'isError': True,
                'content': []
            }
            return Response(response, status=status.HTTP_201_CREATED)


class LoginApiView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                payload = jwt_payload_handler(user)
                token = jwt_encode_handler(payload)
                data = {
                    'id_user': user.id,
                    'active': user.is_active,
                    'token': token,
                }
                response = {
                    'message': '',
                    'isOk': True,
                    'isError': False,
                    'content': data
                }
        else:
            response = {
                'message': 'Credeciales inválidas',
                'isOk': False,
                'isError': True,
                'content': []
            }
        return Response(response, status=status.HTTP_201_CREATED)


class LoginTaquillaApiView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        global response
        usrname = request.data.get('username')
        usrpsw = request.data.get('password')

        try:
            taquillero = Taquilla.objects.get(usuario__username=usrname)
            if taquillero.grupo.estado == 'ACTIVO':
                user = authenticate(username=usrname, password=usrpsw)
                if user is not None:
                    if user.is_active:
                        payload = jwt_payload_handler(user)
                        token = jwt_encode_handler(payload)
                        data = {
                            'taquila_id': taquillero.id,
                            'id_user': user.id,
                            'active': user.is_active,
                            'username': user.username,
                            'token': token,
                        }
                        response = {
                            'message': '',
                            'isOk': True,
                            'isError': False,
                            'content': data
                        }
                else:
                    response = {
                        'message': 'Credeciales inválidas',
                        'isOk': False,
                        'isError': True,
                        'content': []
                    }
            else:
                response = {
                    'message': 'Grupo inactivo',
                    'isOk': False,
                    'isError': True,
                    'content': []
                }

        except:
            response = {
                'message': 'Usuario no encontrado',
                'isOk': False,
                'isError': True,
                'content': []
            }

        return Response(response, status=status.HTTP_201_CREATED)


class UsuarioApiView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, id=None, format=None):
        if id is not None:
            try:
                usuario = User.objects.get(id=id)
                serializer = UserSerializer(usuario, many=False)
                response = {
                    'message': '',
                    'isOk': True,
                    'isError': False,
                    'content': serializer.data
                }
                return Response(response, status=status.HTTP_201_CREATED)
            except:
                response = {
                    'message': 'Usuario no encontrado',
                    'isOk': False,
                    'isError': True,
                    'content': []
                }
                return Response(response, status=status.HTTP_201_CREATED)
        else:
            usuario = User.objects.all()
            serializer = UserSerializer(usuario, many=True)
            response = {
                'message': '',
                'isOk': True,
                'isError': False,
                'content': serializer.data
            }
            return Response(response, status=status.HTTP_201_CREATED)


class GrupoApiView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, format=None):
        listaGrupos = Grupo.objects.all()
        serializer = GrupoSerializer(listaGrupos, many=True)
        response = {
            'message': '',
            'isOk': True,
            'isError': False,
            'content': serializer.data
        }
        return Response(response, status=status.HTTP_201_CREATED)

    def post(self, request, format=None):
        nombre_grupo = request.data.get('nombreGrupo')
        nombre_grupo_up = nombre_grupo.upper()
        propietariosReq = request.data.get('propietarios')
        estadoReq = request.data.get('estado')
        try:
            Grupo.objects.get(nombreGrupo=nombre_grupo_up)
            response = {
                'message': 'Ya existe un grupo asociado con este nombre',
                'isOk': False,
                'isError': True,
                'content': []
            }
            return Response(response, status=status.HTTP_201_CREATED)
        except:
            grupo = Grupo.objects.create(nombreGrupo=nombre_grupo_up, propietarios=propietariosReq.upper(),
                                         estado=estadoReq)
            grupo.save()
            grupo_serializer = GrupoSerializer(Grupo.objects.get(nombreGrupo=nombre_grupo_up))
            response = {
                'message': '',
                'isOk': True,
                'isError': False,
                'content': grupo_serializer.data
            }
            return Response(response, status=status.HTTP_201_CREATED)

    def put(self, request, pk, format=None):
        grupo = Grupo.objects.get(id=pk)
        nombre_grupo = request.data.get('nombreGrupo')
        nombre_grupo_up = nombre_grupo.upper()
        propietariosReq = request.data.get('propietarios')
        estadoReq = request.data.get('estado')

        if grupo.nombreGrupo == nombre_grupo_up:
            grupo.estado = estadoReq
            grupo.propietarios = propietariosReq.upper()
            grupo.save()
            grupos = Grupo.objects.all()
            grupo_serializer = GrupoSerializer(grupos, many=True)

            response = {
                'message': '',
                'isOk': True,
                'isError': False,
                'content': grupo_serializer.data
            }

            return Response(response, status=status.HTTP_201_CREATED)
        else:
            try:
                Grupo.objects.get(nombreGrupo=nombre_grupo_up)
                grupos = Grupo.objects.all()
                grupo_serializer = GrupoSerializer(grupos, many=True)
                response = {
                    'message': 'Ya existe un grupo asociado con este nombre',
                    'isOk': False,
                    'isError': True,
                    'content': grupo_serializer.data
                }
                return Response(response, status=status.HTTP_201_CREATED)
            except:
                grupo.estado = estadoReq
                grupo.propietarios = propietariosReq.upper()
                grupo.nombreGrupo = nombre_grupo_up
                grupo.save()
                grupos = Grupo.objects.all()
                grupo_serializer = GrupoSerializer(grupos, many=True)

                response = {
                    'message': '',
                    'isOk': True,
                    'isError': False,
                    'content': grupo_serializer.data
                }

                return Response(response, status=status.HTTP_201_CREATED)


class TaquillaApiView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, format=None):
        listaTaquillas = Taquilla.objects.all()
        serializer = TaquillaSerializer(listaTaquillas, many=True)
        response = {
            'message': '',
            'isOk': True,
            'isError': False,
            'content': serializer.data
        }
        return Response(response, status=status.HTTP_201_CREATED)

    def post(self, request, format=None):
        grupoId = request.data.get('grupoId')
        usuarios = request.data.get('usuarios')
        arrayUsuarios = []
        grupo = Grupo.objects.get(id=grupoId)

        for usr in usuarios:
            try:
                User.objects.get(username=usr.get('username'))
                response = {
                    'message': '%s ya se encuentra registrado' % (usr.get('username')),
                    'isOk': False,
                    'isError': True,
                    'content': []
                }
                return Response(response, status=status.HTTP_201_CREATED)
            except:
                usr = User.objects.create_user(username=usr.get('username'), password=usr.get('password'),
                                               is_active=True)
                arrayUsuarios.append(usr)

        for usr in arrayUsuarios:
            usr.save()
            taquilla = Taquilla(usuario=usr, grupo=grupo)
            taquilla.save()

        response = {
            'message': 'Taquillas registrada correctamente',
            'isOk': True,
            'isError': False,
            'content': []
        }
        return Response(response, status=status.HTTP_201_CREATED)

    def put(self, request, pk, format=None):
        password = request.data.get('password')
        estado = request.data.get('estado')
        taquillero = Taquilla.objects.get(id=pk)
        usuario = User.objects.get(username=taquillero.usuario.username)

        if str(password) != '':
            usuario.set_password(password)
            usuario.save()

            response = {
                'message': 'Contraseña cambiada correctamente',
                'isOk': True,
                'isError': False,
                'content': []
            }
        else:
            usuario.is_active = estado
            usuario.save()

            response = {
                'message': '%s ha cambiado de estado' % usuario.username,
                'isOk': True,
                'isError': False,
                'content': []
            }

        return Response(response, status=status.HTTP_201_CREATED)


class RifaApiView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, id=None, format=None):
        if id is not None:
            try:
                rifa = Rifa.objects.get(id=id)
                serializer = RifaSerializer(rifa, many=False)
                response = {
                    'message': '',
                    'isOk': True,
                    'isError': False,
                    'content': serializer.data
                }
            except:
                rifa = Rifa.objects.order_by('id').first()
                serializer = RifaSerializer(rifa, many=False)
                response = {
                    'message': '',
                    'isOk': True,
                    'isError': False,
                    'content': serializer.data
                }
        else:
            listaRifas = Rifa.objects.all().order_by('nombre_rifa')
            serializer = RifaSerializer(listaRifas, many=True)
            response = {
                'message': '',
                'isOk': True,
                'isError': False,
                'content': serializer.data
            }

        return Response(response, status=status.HTTP_201_CREATED)

    def post(self, request, format=None):
        rifa_nombre = request.data.get('nombre_rifa')
        try:
            rifa = Rifa.objects.get(nombre_rifa=rifa_nombre)
            rifa_serializer = RifaSerializer(rifa, many=False)
            response = {
                'message': 'Ya existe una rifa registrada con este nombre.',
                'isOk': False,
                'isError': True,
                'content': rifa_serializer.data
            }
            return Response(response, status=status.HTTP_201_CREATED)
        except:
            rifa = Rifa.objects.create(nombre_rifa=rifa_nombre)
            rifa.save()
            rifa = Rifa.objects.get(nombre_rifa=rifa_nombre)
            rifa_serializer = RifaSerializer(rifa, many=False)
            response = {
                'message': '',
                'isOk': True,
                'isError': False,
                'content': rifa_serializer.data
            }
            return Response(response, status=status.HTTP_201_CREATED)


class RifaDetalleApiView(APIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = RifaListaSerializer

    def get(self, request, id=None, format=None):
        if id is not None:
            # print(id)
            rifaDetalles = RifaLista.objects.filter(rifa__id=id).order_by('posicion')
            # print(rifaDetalles)
            serializer = RifaListaSerializer(rifaDetalles, many=True)
            response = {
                'message': '',
                'isOk': True,
                'isError': False,
                'content': serializer.data
            }
            return Response(response, status=status.HTTP_201_CREATED)

    def post(self, request, format=None):
        posicion = request.data.get('posicion')
        nombre_img = request.data.get('nombre_imagen')
        rifa_id = request.data.get('rifa')
        img = request.FILES['image']
        try:
            try:
                rifaDetalle = RifaLista.objects.get(rifa__id=rifa_id, posicion=posicion)
                rifaDetalle.image.save(img.name, img)
                rifaDetalle.save()

                response = {
                    'message': 'Imagen guardada correctamente',
                    'isOk': True,
                    'isError': False,
                    'content': []
                }
            except:
                rifa = Rifa.objects.get(id=rifa_id)
                rifaDetalle = RifaLista.objects.create(posicion=posicion, nombre_imagen=nombre_img, rifa=rifa)
                rifaDetalle.image.save(img.name, img)
                rifaDetalle.save()
                response = {
                    'message': 'Imagen guardada correctamente',
                    'isOk': True,
                    'isError': False,
                    'content': []
                }
            return Response(response, status=status.HTTP_201_CREATED)
        except:
            response = {
                'message': 'Error al guardar imagen',
                'isOk': False,
                'isError': True,
                'content': []
            }
            return Response(response, status=status.HTTP_201_CREATED)


class SorteosApiView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, year=None, month=None, day=None, format=None):
        if year is not None and month is not None and day is not None:
            dateRequest = date(int(year), int(month), int(day))
            listaSorteos = Sorteo.objects.filter(fecha_sorteo=dateRequest).order_by('sorteoHoras__hora_sorteo')
            serializer = SorteoSerializer(listaSorteos, many=True)
            response = {
                'message': '',
                'isOk': True,
                'isError': False,
                'content': serializer.data
            }
        else:
            listaSorteos = Sorteo.objects.filter(fecha_sorteo=datetime.now().date()).order_by(
                'sorteoHoras__hora_sorteo')
            # print(listaSorteos)
            serializer = SorteoSerializer(listaSorteos, many=True)
            response = {
                'message': '',
                'isOk': True,
                'isError': False,
                'content': serializer.data
            }
        return Response(response, status=status.HTTP_201_CREATED)

    def post(self, request, format=None):
        rifaId = request.data.get('rifaId')
        fechaSorteo = request.data.get('fecha_sorteo')
        horaSorteo = request.data.get('hora_sorteo')
        numero = request.data.get('numero_ganador')

        try:
            rifa = Rifa.objects.get(id=rifaId)
            time_split = horaSorteo.split(':')
            t = time(int(time_split[0]), int(time_split[1]), 0)
            try:
                sorteo = Sorteo.objects.get(fecha_sorteo=fechaSorteo, sorteoHoras_hora_sorteo=t, rifa=rifa)
                response = {
                    'message': 'Ya existe un sorteo registrado para %s a las %s .' % (fechaSorteo, horaSorteo),
                    'isOk': False,
                    'isError': True,
                    'content': []
                }
                return Response(response, status=status.HTTP_201_CREATED)
            except:
                sorteo_hora = SorteoHora.objects.create(hora_sorteo=t, rifa=rifa)
                sorteo = Sorteo.objects.create(rifa=rifa, fecha_sorteo=fechaSorteo, sorteoHoras=sorteo_hora,
                                               numero_ganador=numero)
                sorteo.save()
                response = {
                    'message': 'Sorteo creado satisfatoriamente',
                    'isOk': True,
                    'isError': False,
                    'content': []
                }
                return Response(response, status=status.HTTP_201_CREATED)
        except Exception as e:
            response = {
                'message': e.message,
                'isOk': False,
                'isError': True,
                'content': []
            }
            return Response(response, status=status.HTTP_201_CREATED)


class SorteoHoraApiView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, id=None, format=None):
        d = datetime.now()
        try:
            if id is not None:
                if d.minute >= 55:
                    t = time(d.hour + 1, 0, 0)
                else:
                    t = time(d.hour, d.minute + 5, 0)
                # t = time(d.hour, d.minute+5, 0)
                rifaHoraList = SorteoHora.objects.filter(hora_sorteo__gt=t, rifa__id=id).order_by('hora_sorteo')
                serializer = SorteoHoraSerializer(rifaHoraList, many=True)
                response = {
                    'message': '',
                    'isOk': True,
                    'isError': False,
                    'content': serializer.data
                }
                return Response(response, status=status.HTTP_200_OK)
        except:
            response = {
                'message': 'Sorteos no encontrados',
                'isOk': True,
                'isError': False,
                'content': []
            }
            return Response(response, status=status.HTTP_200_OK)


class VentaApiView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, format=None):
        pass

    def post(self, request, format=None):
        estado_sistema = EstadoSistema.objects.get(nombre='activar venta')
        if estado_sistema.estado:
            d = timezone.now()
            array_items = request.data.get('detalles')
            id_usuario = request.data.get('taquilla')
            total_apostado = request.data.get('monto_total')
            serial = random_string(8)
            try:
                taquilla = Taquilla.objects.get(usuario__id=id_usuario)
                if taquilla.grupo.estado == 'ACTIVO':
                    if taquilla.usuario.is_active:
                        venta = Venta()
                        sum = sum_montos(array_items)
                        valid_tiket = validar_venta(array_items, d.date())
                        if valid_tiket:
                            # Datos requeridos
                            hora = time(d.hour - 5, d.minute, d.second)

                            # Generar venta
                            if sum == total_apostado:
                                venta.taquilla = taquilla
                                venta.total_apostado = total_apostado
                                venta.serial_cobro = serial
                                venta.fecha = d.date()
                                venta.time = hora
                                venta.save()

                                if venta.id is not None:

                                    # Lista de items
                                    for item in array_items:
                                        ###########
                                        detalle_venta = VentaDetalle()

                                        ###########
                                        rifaDetalle = RifaLista.objects.get(id=item.get('id'))
                                        sorteo = Sorteo.objects.get(rifa__id=item.get('rifa'),
                                                                    sorteoHoras__id=item.get('sorteo_hora_id'),
                                                                    fecha_sorteo=d.date())
                                        monto = item.get('monto')

                                        ###########
                                        detalle_venta.venta = venta
                                        detalle_venta.sorteo = sorteo
                                        detalle_venta.detalle_rifa = rifaDetalle
                                        detalle_venta.valor_apuesta = monto
                                        detalle_venta.save()

                                    # list_detalle = VentaDetalle.objects.filter(venta__id=venta.id)
                                    # lista_serializer = VentaDetalleSerializer(list_detalle, many=True)
                                    venta_serializer = VentaSerializerCompleto(venta, many=False)

                                    response = {
                                        'message': 'Apuesta guardada correctamente',
                                        'isOk': True,
                                        'isError': False,
                                        'content': venta_serializer.data
                                    }

                                    return Response(response, status=status.HTTP_201_CREATED)
                                else:
                                    response = {
                                        'message': 'Error al guardar, intente nuevamnete',
                                        'isOk': False,
                                        'isError': True,
                                        'content': []
                                    }
                                    return Response(response, status=status.HTTP_201_CREATED)
                            else:
                                response = {
                                    'message': 'El monto total no coincide con la suma de todos los montos, por favor verifique e '
                                               'intente nuevamente',
                                    'isOk': False,
                                    'isError': True,
                                    'content': []
                                }
                                return Response(response, status=status.HTTP_201_CREATED)
                        else:
                            response = {
                                'message': 'Uno o mas sorteos ya han sido jugados, por favor verifique e intente nuevamente',
                                'isOk': False,
                                'isError': True,
                                'content': []
                            }
                            return Response(response, status=status.HTTP_201_CREATED)
                    else:
                        response = {
                            'message': 'Usuario inactivo',
                            'isOk': False,
                            'isError': True,
                            'content': []
                        }
                        return Response(response, status=status.HTTP_201_CREATED)
                else:
                    response = {
                        'message': 'Grupo inactivo',
                        'isOk': False,
                        'isError': True,
                        'content': []
                    }
                    return Response(response, status=status.HTTP_201_CREATED)
            except Exception as e:
                response = {
                    'message': e.message,
                    'isOk': False,
                    'isError': True,
                    'content': []
                }
                return Response(response, status=status.HTTP_201_CREATED)
        else:
            response = {
                'message': 'Sorteo en proceso, por favor intente, nuevamente',
                'isOk': False,
                'isError': True,
                'content': []
            }
            return Response(response, status=status.HTTP_201_CREATED)


# ############################ NUEVA IMPLEMENTACION ################################
class VentaMultipleItemsApiView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        # print(request.data)
        estado_sistema = EstadoSistema.objects.get(nombre='activar venta')
        if estado_sistema.estado:
            d = datetime.now()
            date_now = d.date()
            array_items = request.data.get('detalles')
            id_usuario = request.data.get('taquilla')
            total_apostado = request.data.get('monto_total')
            serial = random_string(8)
            try:
                taquilla = Taquilla.objects.get(usuario__id=id_usuario)
                if taquilla.grupo.estado == 'ACTIVO':
                    if taquilla.usuario.is_active:
                        venta = Venta()
                        sum = sum_montos(array_items)
                        valid_tiket = validar_venta(array_items, d.date())
                        if valid_tiket:
                            # Datos requeridos
                            hora = time(d.hour, d.minute, d.second)

                            # Generar venta
                            if sum == total_apostado:
                                venta.taquilla = taquilla
                                venta.total_apostado = total_apostado
                                venta.serial_cobro = serial
                                venta.fecha = d.date()
                                venta.time = hora
                                venta.save()

                                if venta.id is not None:

                                    # Lista de items
                                    for item in array_items:
                                        ###########
                                        detalle_venta = VentaDetalle()
                                        sorteo = Sorteo.objects.get(sorteoHoras__id=item.get('id_sorteo'),
                                                                    fecha_sorteo=date_now)
                                        detalle_venta.venta = venta
                                        detalle_venta.sorteo = sorteo
                                        detalle_venta.numeros = item.get('numeros')
                                        detalle_venta.tipo_apuesta = item.get('tipo')
                                        detalle_venta.valor_apuesta = item.get('monto')
                                        detalle_venta.ganancia = calculateProfit(item.get('monto'), item.get('tipo'))

                                        detalle_venta.save()
                                        ###########
                                        # rifaDetalle = RifaLista.objects.get(id=item.get('id'))
                                        '''
                                        sorteo = Sorteo.objects.get(rifa__id=item.get('rifa'),
                                                                    sorteoHoras__id=item.get('sorteo_hora_id'),
                                                                    fecha_sorteo=d.date())
                                        '''
                                        # monto = item.get('monto')

                                        ###########
                                        # detalle_venta.venta = venta
                                        # detalle_venta.sorteo = sorteo
                                        # print (item.get('numeros'))
                                        # detalle_venta.numeros = item.get('numeros')
                                        # detalle_venta.valor_apuesta = monto
                                        # detalle_venta.save()

                                    # list_detalle = VentaDetalle.objects.filter(venta__id=venta.id)
                                    # lista_serializer = VentaDetalleSerializer(list_detalle, many=True)
                                    venta_serializer = VentaSerializerCompleto(venta, many=False)
                                    # list_detalle = VentaDetalle.objects.filter(venta__id=venta.id)
                                    # lista_serializer = VentaDetalleSerializer(list_detalle, many=True)
                                    # venta_serializer = VentaSerializerCompleto(venta, many=False)

                                    response = {
                                        'message': 'Apuesta guardada correctamente',
                                        'isOk': True,
                                        'isError': False,
                                        'content': venta_serializer.data
                                    }
                                else:
                                    response = {
                                        'message': 'Error al guardar, intente nuevamnete',
                                        'isOk': False,
                                        'isError': True,
                                        'content': []
                                    }
                            else:
                                response = {
                                    'message': 'El monto total no coincide con la suma de todos los montos, por favor '
                                               'verifique e '
                                               'intente nuevamente',
                                    'isOk': False,
                                    'isError': True,
                                    'content': []
                                }
                        else:
                            response = {
                                'message': 'Uno o mas sorteos ya han sido jugados, por favor verifique e intente nuevamente',
                                'isOk': False,
                                'isError': True,
                                'content': []
                            }
                    else:
                        response = {
                            'message': 'Usuario inactivo',
                            'isOk': False,
                            'isError': True,
                            'content': []
                        }
                else:
                    response = {
                        'message': 'Grupo inactivo',
                        'isOk': False,
                        'isError': True,
                        'content': []
                    }
                return Response(response, status=status.HTTP_201_CREATED)
            except Exception as e:
                response = {
                    'message': e.message,
                    'isOk': False,
                    'isError': True,
                    'content': []
                }
                return Response(response, status=status.HTTP_201_CREATED)
        else:
            response = {
                'message': 'Sorteo en proceso, por favor intente, nuevamente',
                'isOk': False,
                'isError': True,
                'content': []
            }
            return Response(response, status=status.HTTP_201_CREATED)


# ############################ NUEVA IMPLEMENTACION ################################


class VentaReporteApiView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        grupoId = request.data.get('grupo')
        de = request.data.get('fecha')
        hasta = request.data.get('fechaHasta')

        try:
            if grupoId != "-1":
                grupo = Grupo.objects.get(id=grupoId)
                venta = Venta.objects.filter(taquilla__grupo=grupo, fecha__gte=de, fecha__lte=hasta).order_by(
                    'time')
                venta_serializer = VentaSerializer(venta, many=True)
                response = {
                    'message': '',
                    'isOk': True,
                    'isError': False,
                    'content': venta_serializer.data
                }
            else:
                venta = Venta.objects.filter(fecha__gte=de, fecha__lte=hasta).order_by('id')
                venta_serializer = VentaSerializer(venta, many=True)
                response = {
                    'message': '',
                    'isOk': True,
                    'isError': False,
                    'content': venta_serializer.data
                }
            return Response(response, status=status.HTTP_201_CREATED)
        except Exception as e:
            response = {
                'message': e.message,
                'isOk': False,
                'isError': True,
                'content': []
            }
            return Response(response, status=status.HTTP_201_CREATED)


class VentaReporteTaquillaApiView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        taquillaId = request.data.get('taquilla')
        de = request.data.get('taquilla_fecha')
        hasta = request.data.get('taquilla_fecha_hasta')

        try:
            if taquillaId != "-1":
                taquillaId = Taquilla.objects.get(id=taquillaId)
                venta = Venta.objects.filter(taquilla=taquillaId, fecha__gte=de, fecha__lte=hasta).order_by(
                    'time')
                venta_serializer = VentaSerializer(venta, many=True)
                response = {
                    'message': '',
                    'isOk': True,
                    'isError': False,
                    'content': venta_serializer.data
                }
            else:
                venta = Venta.objects.filter(fecha__gte=de, fecha__lte=hasta).order_by('id')
                venta_serializer = VentaSerializer(venta, many=True)
                response = {
                    'message': '',
                    'isOk': True,
                    'isError': False,
                    'content': venta_serializer.data
                }
            return Response(response, status=status.HTTP_201_CREATED)
        except Exception as e:
            response = {
                'message': e.message,
                'isOk': False,
                'isError': True,
                'content': []
            }
            return Response(response, status=status.HTTP_201_CREATED)


class VentaDetalleApiView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, id=None, format=None):
        if id is not None:
            venta_detalle = VentaDetalle.objects.filter(venta__id=id)
            if venta_detalle != 0:
                venta_detalle_serializer = VentaDetalleSerializer(venta_detalle, many=True)
                response = {
                    'message': '',
                    'isOk': True,
                    'isError': False,
                    'content': venta_detalle_serializer.data
                }
                return Response(response, status=status.HTTP_201_CREATED)
            else:
                response = {
                    'message': '',
                    'isOk': True,
                    'isError': False,
                    'content': []
                }
                return Response(response, status=status.HTTP_201_CREATED)
        else:
            return Response({}, status=status.HTTP_201_CREATED)


class EstadosSistemaApiView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, format=None):
        listaEstados = EstadoSistema.objects.all()
        serializer = EstadoSistemaSerializer(listaEstados, many=True)
        response = {
            'message': '',
            'isOk': True,
            'isError': False,
            'content': serializer.data
        }
        return Response(response, status=status.HTTP_201_CREATED)

    def post(self, request, format=None):
        content = request.META.get('HTTP_AUTHORIZATION')
        if content is not None:
            idEstado = request.data.get('id')
            estadoBool = request.data.get('estado')
            try:
                estadoObj = EstadoSistema.objects.get(id=idEstado)
                estadoObj.estado = estadoBool
                estadoObj.save()
                response = {
                    'message': '% s ha cambiado de estado' % estadoObj.nombre,
                    'isOk': True,
                    'isError': False,
                    'content': []
                }
                # print(response)
                return Response(response, status=status.HTTP_201_CREATED)
            except:
                response = {
                    'message': 'Objeto no encontrado',
                    'isOk': False,
                    'isError': True,
                    'content': []
                }
                return Response(response, status=status.HTTP_201_CREATED)
        else:
            response = {
                'message': '',
                'isOk': False,
                'isError': False,
                'content': []
            }
            return Response(response, status=status.HTTP_201_CREATED)


class PermisoApiView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, id=None, format=None):
        if id is not None:
            pass
        else:
            permiso = Permisos.objects.all()
            permiso_serializer = PermisoSerializer(permiso, many=True)
            response = {
                'message': '',
                'isOk': True,
                'isError': False,
                'content': permiso_serializer.data
            }
            return Response(response, status=status.HTTP_201_CREATED)

    def post(self, request, format=None):
        permiso = request.data.get('permiso_name')
        uri = request.data.get('permiso_uri')

        permiso_request = Permisos.objects.filter(Q(permiso_name=permiso) | Q(permiso_uri=uri))

        if len(permiso_request) > 0:
            response = {
                'message': 'Permiso ya existe',
                'isOk': False,
                'isError': True,
                'content': []
            }
            return Response(response, status=status.HTTP_201_CREATED)
        else:
            permiso = Permisos.objects.create(permiso_name=permiso, permiso_uri=uri)
            permiso.save()
            response = {
                'message': 'Permiso creado exitosamente',
                'isOk': True,
                'isError': True,
                'content': []
            }
            return Response(response, status=status.HTTP_201_CREATED)


class PermisosUsuarioApi(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, id=None, format=None):
        if id is not None:
            permisos_usuario = PermisoUsuario.objects.filter(usuario__id=id).order_by('permiso__permiso_name')
            permisos_serializer = PermisoUsuarioSerializer(permisos_usuario, many=True)
            response = {
                'message': '',
                'isOk': True,
                'isError': False,
                'content': permisos_serializer.data
            }
            return Response(response, status=status.HTTP_201_CREATED)

    def post(self, request, format=None):
        usuario = request.data.get('usuario')
        lista_permisos = request.data.get('lista_permiso')
        try:
            usr = User.objects.get(id=usuario)
            # permisoList = []
            for obj in lista_permisos:
                permiso_usuario = PermisoUsuario.objects.filter(permiso__id=obj.get('id'))
                if len(permiso_usuario) == 0:
                    permiso = Permisos.objects.get(id=obj.get('id'))
                    permiso_usuario = PermisoUsuario.objects.create(usuario=usr, permiso=permiso)
                    permiso_usuario.save()
            '''
            for obj in lista_permisos:
                permiso = Permisos.objects.get(id=obj.get('id'))
                permisoList.append(permiso)

            for permiso in permisoList:
                permiso_usuario = PermisoUsuario.objects.create(usuario=usr, permiso=permiso)
                permiso_usuario.save()
            '''

            response = {
                'message': '',
                'isOk': True,
                'isError': False,
                'content': []
            }
            return Response(response, status=status.HTTP_201_CREATED)

        except Exception as e:
            response = {
                'message': e.message,
                'isOk': False,
                'isError': True,
                'content': []
            }
            return Response(response, status=status.HTTP_201_CREATED)


class PagarTicketApiView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, serial=None, format=None):
        if serial is not None:
            try:
                tiket = Venta.objects.filter(serial_cobro=serial.upper())
                if len(tiket) > 0:
                    serializer = VentaSerializer(tiket, many=True)
                    response = {
                        'message': '',
                        'isOk': True,
                        'isError': False,
                        'content': serializer.data
                    }
                else:
                    response = {
                        'message': 'Tiket no encontrado',
                        'isOk': False,
                        'isError': False,
                        'content': []
                    }
                return Response(response, status=status.HTTP_201_CREATED)
            except Venta.DoesNotExist:
                response = {
                    'message': 'Tiket no encontrado, por favor el serial de cobro e intente nuevamente',
                    'isOk': False,
                    'isError': False,
                    'content': []
                }
                return Response(response, status=status.HTTP_201_CREATED)
            except Exception as e:
                response = {
                    'message': e.message,
                    'isOk': False,
                    'isError': False,
                    'content': []
                }
                return Response(response, status=status.HTTP_201_CREATED)

    def post(self, request, format=None):
        try:
            idVenta = request.data.get('idVenta')
            usrId = request.data.get('idUsuario')
            venta = Venta.objects.get(id=idVenta)
            usr = User.objects.get(id=usrId)

            d = datetime.now()
            a = date(d.year, d.month, d.day)
            b = date(venta.fecha.year, venta.fecha.month, venta.fecha.day)
            delta = a - b

            if delta.days < 6:
                if venta.estado == 'GANADO':
                    venta.estado = 'PAGADO'
                    venta.usuarioPagador = usr
                    venta.fecha_pago = datetime.now()
                    venta.save()

                    ventaResponse = Venta.objects.filter(id=venta.id)
                    serializer = VentaSerializer(ventaResponse, many=True)

                    response = {
                        'message': 'Pago realizado exitosamente',
                        'isOk': True,
                        'isError': False,
                        'content': serializer.data
                    }
                    return Response(response, status=status.HTTP_201_CREATED)
                else:
                    response = {
                        'message': 'Solo se puede realizar pagos de tikets ganados',
                        'isOk': False,
                        'isError': False,
                        'content': []
                    }
                    return Response(response, status=status.HTTP_201_CREATED)
            else:
                venta.estado = 'CADUCADO'
                venta.save()
                response = {
                    'message': 'Tiket caducado',
                    'isOk': False,
                    'isError': True,
                    'content': []
                }
                return Response(response, status=status.HTTP_201_CREATED)

        except Exception as e:
            response = {
                'message': e.message,
                'isOk': False,
                'isError': False,
                'content': []
            }
            return Response(response, status=status.HTTP_201_CREATED)


class PagarTiketTaquillaApiView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serial = request.data.get('serial')
        usr = request.data.get('usuario')
        try:
            usuario = User.objects.get(id=usr)
            permisos = PermisoUsuario.objects.filter(usuario=usuario, permiso__permiso_name='Pagar')
            if len(permisos) > 0:
                venta = Venta.objects.get(serial_cobro=serial.upper())

                d = datetime.now()
                a = date(d.year, d.month, d.day)
                b = date(venta.fecha.year, venta.fecha.month, venta.fecha.day)
                delta = a - b

                if delta.days < 6:
                    if venta.estado == 'GANADO':
                        venta.estado = 'PAGADO'
                        venta.usuarioPagador = usuario
                        venta.fecha_pago = datetime.now()
                        venta.save()

                        ventaResponse = Venta.objects.filter(id=venta.id)
                        serializer = VentaSerializer(ventaResponse, many=True)

                        response = {
                            'message': 'Operación realizada exitosamente, valor a pagar: %s ' % venta.total_ganancia,
                            'isOk': True,
                            'isError': False,
                            'content': serializer.data
                        }
                        return Response(response, status=status.HTTP_201_CREATED)
                    elif venta.estado == 'PAGADO':
                        response = {
                            'message': 'Este tiket ya se encuentra pago',
                            'isOk': False,
                            'isError': False,
                            'content': []
                        }
                        return Response(response, status=status.HTTP_201_CREATED)
                    else:
                        response = {
                            'message': 'Solo se pueden realizar pagos de tikets ganados',
                            'isOk': False,
                            'isError': False,
                            'content': []
                        }
                        return Response(response, status=status.HTTP_201_CREATED)
                else:
                    venta.estado = 'CADUCADO'
                    venta.save()
                    response = {
                        'message': 'Tiket caducado',
                        'isOk': False,
                        'isError': True,
                        'content': []
                    }
                    return Response(response, status=status.HTTP_201_CREATED)
            else:
                response = {
                    'message': 'El usuario no tiene permisos para realizar esta acción',
                    'isOk': False,
                    'isError': False,
                    'content': []
                }
                return Response(response, status=status.HTTP_201_CREATED)
        except Venta.DoesNotExist:
            response = {
                'message': 'Tiket no encontrado, por favor verifica el serial de cobro e intente nuevamente',
                'isOk': False,
                'isError': False,
                'content': []
            }
            return Response(response, status=status.HTTP_201_CREATED)
        except Exception as e:
            response = {
                'message': e.message,
                'isOk': False,
                'isError': False,
                'content': []
            }
            return Response(response, status=status.HTTP_201_CREATED)


class VentasTaquilla(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, id=None, format=None):
        d = datetime.now()
        if id is not None:
            ventas = Venta.objects.filter(taquilla__usuario__id=id, fecha=d.date()).order_by(
                'id')
            count_venta = len(ventas)
            count_pagados = 0
            sum_venta = 0
            sum_premios = 0
            list_serializer = VentaSerializerTaquilla(ventas, many=True)
            for item in ventas:
                sum_venta += item.total_apostado
                if item.estado == 'PAGADO':
                    sum_premios += item.total_ganancia
                    count_pagados += 1

            balance = sum_venta - sum_premios

            data = {
                'total_venta_tikets': count_venta,
                'total_pagados_tikets': count_pagados,
                'suma_ventas': sum_venta,
                'suma_premios': sum_premios,
                'balance': balance,
                'tikets': list_serializer.data
            }

            response = {
                'message': '',
                'isOk': True,
                'isError': False,
                'content': data
            }
            return Response(response, status=status.HTTP_201_CREATED)

    def post(self, request, format=None):
        taquillaId = request.data.get('taquilla')
        de = request.data.get('taquilla_fecha')
        hasta = request.data.get('taquilla_fecha_hasta')

        try:
            taquillaId = Taquilla.objects.get(usuario__id=taquillaId)
            venta = Venta.objects.filter(taquilla=taquillaId.id, fecha__gte=de, fecha__lte=hasta).order_by(
                'id')

            count_venta = len(venta)
            count_pagados = 0
            sum_venta = 0
            sum_premios = 0

            for item in venta:
                sum_venta += item.total_apostado
                if item.estado == 'PAGADO':
                    sum_premios += item.total_ganancia
                    count_pagados += 1

            balance = sum_venta - sum_premios

            venta_serializer = VentaSerializerTaquilla(venta, many=True)
            '''
            data = {
                'tikets': venta_serializer.data
            }
            '''

            data = {
                'total_venta_tikets': count_venta,
                'total_pagados_tikets': count_pagados,
                'suma_ventas': sum_venta,
                'suma_premios': sum_premios,
                'balance': balance,
                'tikets': venta_serializer.data
            }

            response = {
                'message': '',
                'isOk': True,
                'isError': False,
                'content': data
            }
            return Response(response, status=status.HTTP_201_CREATED)
        except Exception as e:
            response = {
                'message': e.message,
                'isOk': False,
                'isError': True,
                'content': []
            }
            return Response(response, status=status.HTTP_201_CREATED)


class TicketsPagados(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        de = request.data.get('fecha')
        hasta = request.data.get('fechaHasta')

        try:
            venta = Venta.objects.filter(fecha__gte=de, fecha__lte=hasta, estado='PAGADO')
            # venta_juego = Venta.objects.filter(fecha__gte=de, fecha__lte=hasta, estado='EN JUEGO').order_by('id')
            # venta = venta_ganados + venta_juego
            venta_serializer = PagadoSerializer(venta, many=True)
            response = {
                'message': '',
                'isOk': True,
                'isError': False,
                'content': venta_serializer.data
            }
            return Response(response, status=status.HTTP_201_CREATED)
        except Exception as e:
            response = {
                'message': e.message,
                'isOk': False,
                'isError': True,
                'content': []
            }
            return Response(response, status=status.HTTP_201_CREATED)


def createSorteos(request):
    # crear_sorteos()
    set_number_sorteo()
    html = "<html><body>It is now %s.</body></html>" % now
    return HttpResponse(html)


def random_string(string_length=10):
    """Returns a random string of length string_length."""
    random = str(uuid.uuid4())  # Convert UUID format to a Python string.
    random = random.upper()  # Make all characters uppercase.
    random = random.replace("-", "")  # Remove the UUID '-'.
    return random[0:string_length]  # Return the random string.


def sum_montos(listaItems):
    sum = 0
    for item in listaItems:
        '''
        rifaDetalle = RifaLista.objects.get(id=item.get('id'))
        sorteo = Sorteo.objects.get(rifa__id=item.get('rifa'),
                                    sorteoHoras__id=item.get('sorteo_hora_id'),
                                    fecha_sorteo=d.date())
        '''
        monto = item.get('monto')
        sum = sum + monto

    return sum


def validar_venta(array_items, fecha):
    d = datetime.now()
    if d.minute >= 55:
        t = time(d.hour + 1, 0, d.second)
    else:
        t = time(d.hour, d.minute + 5, d.second)
    valid = True
    for item in array_items:
        sorteo = Sorteo.objects.get(sorteoHoras__id=item.get('id_sorteo'), fecha_sorteo=fecha)
        ###########
        # detalle_venta = VentaDetalle()

        ###########
        # rifaDetalle = RifaLista.objects.get(id=item.get('id'))
        '''
        sorteo = Sorteo.objects.get(rifa__id=item.get('monto'),
                                    sorteoHoras__id=item.get('hora_sorteo'),
                                    fecha_sorteo=fecha)
        '''
        if t >= sorteo.sorteoHoras.hora_sorteo:
            valid = False
    return valid


def calculateProfit(amount, type):
    win = 0
    if type == 0:
        win = amount * 34
    elif type == 1 or type == 2 or type == 3 or type == 4:
        win = amount * 2
    elif type == 5 or type == 6 or type == 7:
        win = amount * 3
    return win
