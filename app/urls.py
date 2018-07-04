from django.conf.urls import url
from django.conf.urls.static import static
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token
from .views import LoginApiView, GrupoApiView, Index, UsuarioApiView, TaquillaApiView, RifaApiView, \
    RifaDetalleApiView, createSorteos, SorteosApiView, EstadosSistemaApiView, LoginTaquillaApiView, SorteoHoraApiView, \
    VentaApiView, VentaReporteApiView, VentaDetalleApiView, PermisoApiView, PermisosUsuarioApi, \
    PagarTicketApiView, PagarTiketTaquillaApiView, VentasTaquilla, TicketsPagados, VentaReporteTaquillaApiView, \
    setSignature, VentaMultipleItemsApiView, UltimoSorteoApiView
from myproject import settings

urlpatterns = [
    url(r'^$', Index),
    url(r'^api-token-auth/', obtain_jwt_token),
    url(r'^api-token-refresh/', refresh_jwt_token),
    url(r'^api-rest/login/$', LoginApiView.as_view()),
    url(r'^api-rest/login/taquilla/$', LoginTaquillaApiView.as_view()),
    url(r'^api-rest/usuario/$', UsuarioApiView.as_view()),
    url(r'^api-rest/usuario/(?P<id>\d+)/$', UsuarioApiView.as_view()),
    url(r'^api-rest/grupos/$', GrupoApiView.as_view()),
    url(r'^api-rest/grupos/(?P<pk>[0-9]+)/$', GrupoApiView.as_view()),
    url(r'^api-rest/taquillas/$', TaquillaApiView.as_view()),
    url(r'^api-rest/taquillas/(?P<pk>[0-9]+)/$', TaquillaApiView.as_view()),
    url(r'^api-rest/rifa/$', RifaApiView.as_view()),
    url(r'^api-rest/rifa/(?P<id>[0-9]+)/$', RifaApiView.as_view()),
    url(r'^api-rest/rifa/detalle/$', RifaDetalleApiView.as_view()),
    url(r'^api-rest/rifa/detalle/(?P<id>\d+)/$', RifaDetalleApiView.as_view()),
    url(r'^api-rest/sorteo/$', SorteosApiView.as_view()),
    url(r'^api-rest/sorteo/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/(?P<day>[0-9]{2})/$', SorteosApiView.as_view()),
    url(r'^api-rest/venta/$', VentaApiView.as_view()),
    url(r'^api-rest/venta/reporte/$', VentaReporteApiView.as_view()),
    url(r'^api-rest/venta/reporte/taquilla/$', VentaReporteTaquillaApiView.as_view()),
    url(r'^api-rest/venta/taquilla/$', VentasTaquilla.as_view()),
    url(r'^api-rest/venta/taquilla/(?P<id>[0-9]+)/$', VentasTaquilla.as_view()),
    url(r'^api-rest/venta/detalle/(?P<id>[0-9]+)/$', VentaDetalleApiView.as_view()),
    url(r'^api-rest/permisos/$', PermisoApiView.as_view()),
    url(r'^api-rest/permisos/usuario/$', PermisosUsuarioApi.as_view()),
    url(r'^api-rest/permisos/usuario/(?P<id>[0-9]+)/$', PermisosUsuarioApi.as_view()),
    url(r'^api-rest/sorteo/horas/$', SorteoHoraApiView.as_view()),
    url(r'^api-rest/sorteo/horas/(?P<id>[0-9]+)/$', SorteoHoraApiView.as_view()),
    url(r'^api-rest/venta/pagar/$', PagarTicketApiView.as_view()),
    url(r'^api-rest/venta/pagar/(?P<serial>[\w\.-]+)/$', PagarTicketApiView.as_view()),
    url(r'^api-rest/venta/taquilla/pagar/$', PagarTiketTaquillaApiView.as_view()),
    url(r'^api-rest/venta/pagos/$', TicketsPagados.as_view()),
    url(r'^api-rest/estados/$', EstadosSistemaApiView.as_view()),
    url(r'^api-rest/ultimo-sorteo/$', UltimoSorteoApiView.as_view()),
    url(r'^qz/signature/$', setSignature),
    ##### NUEVA IMPLEMENTACION ######
    url(r'^api-rest/venta/nueva/$', VentaMultipleItemsApiView.as_view()),
    ##### NUEVA IMPLEMENTACION ######
    url(r'^create-sorteo/$', createSorteos),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
