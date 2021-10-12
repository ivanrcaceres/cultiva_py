"""ayudapy URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

from conf import api_urls
from core import views as core_views
from org import views as org_views
from org.views import RestrictedView

urlpatterns = [
    path('admin/', include('admin_honeypot.urls', namespace='admin_honeypot')),
    # path('jara/', admin.site.urls),
    # home
    path('', core_views.home, name='home'),
    path('dar', TemplateView.as_view(template_name="giver/info.html")),
    path('legal', TemplateView.as_view(template_name="footer/legal.html"), name='legal'),
    path('voluntario/legal', TemplateView.as_view(template_name="volunteer/info.html"), name='voluntariolegal'),
    path('preguntas_frecuentes', core_views.view_faq, name='general_faq'),
    path('contacto', TemplateView.as_view(template_name="footer/contact_us.html"), name='contact_us'),
    # help requests
    path('recibir', TemplateView.as_view(template_name="help_request/info.html")),
    path('solicitar', core_views.request_form, name="request-form"),

    path('registar_user', core_views.user_form, name="user-form"),



    path('registar_user_comprador', core_views.user_form_comprador, name="user-form-comprador"),


    path('pedidos/<int:id>', core_views.view_request, name='pedidos-detail'),
    path('pedidos_comprador/<int:id>', core_views.view_request_comprador, name='pedidos-detail-comprador'),
    path('pedidos_ciudad/<slug:city>', core_views.list_by_city, name='pedidos-by-city'),
    path('pedidos', core_views.list_requests),
    path('pedidos_mios', core_views.requestsListView.as_view()),
    #path('pedidos', core_views.list_requests_mios),
    # donations
    path('ceder', org_views.donation_form, name="donation-form"),
    path('donar', RestrictedView.as_view()),
    path('donaciones', org_views.list_donation),
    path('donaciones_ciudad/<slug:city>', org_views.list_donation_by_city, name='donation-by-city'),
    path('donaciones/<int:id>', org_views.view_donation_center, name='donaciones-detail'),
    # volunteer
    path('voluntario', TemplateView.as_view(template_name="volunteer/form.html"), name='voluntario'),
    # stats
    path('stats', core_views.stats, name='stats'),
    # login/logout
    path('accounts/', include('django.contrib.auth.urls')),

    #cultivapy
    path(
        'login/',
        core_views.LoginUser.as_view(),
        name='user-login',
    ),
    path(
        'login-comprador/',
        core_views.LoginUserComprador.as_view(),
        name='login-comprador',
    ),

    path(
        'register/',
        core_views.UserRegisterView.as_view(),
        name='user-register',
    ),
    path(
        'user-verification/',
        core_views.CodeVerificationView.as_view(),
        name='user-verification',
    ),
    path(
        'user-pass',
        core_views.PassOlvidadaView.as_view(),
        name='user-pass',
    ),
    path(
        'user-perfil',
        core_views.PerfilView.as_view(),
        name='user-perfil',
    ),
    path(
        'perfil-user-detalle/<pk>',
        core_views.PerfilUserDetalleView.as_view(),
    ),
    path(
        'perfil-user-detalle-comprador/<pk>',
        core_views.PerfilUserCompradorDetalleView.as_view(),
    ),
    path(
        'reserva-detalle/<pk>',
        core_views.ReservaDetalleView.as_view(),
    ),
    path(
        'logout/',
        core_views.LogoutView.as_view(),
        name='user-logout',
    ),
    path(
        'delete-publicacion/<pk>',
        core_views.EliPubliDeleteView.as_view(),
        name='delete-publicacion',
    ),
    path(
        'update-publicacion/<pk>',
        core_views.ActuaPubliUpdateView.as_view(),
        name='update-publicacion',
    ),
    path(
        'create-reserva/<pk>/<user_id>',
        core_views.ReservaCreateView.as_view(),
        name='create-reserva',
    ),
    path(
        'update-reserva/<pk>',
        core_views.ActuaReserUpdateView.as_view(),
        name='update-reserva',
    ),
    path(
        'ver-reserva/<pk>',
        core_views.ActuaReserVerView.as_view(),
        name='ver-reserva',
    ),
    path(
        'delete-reserva/<pk>',
        core_views.EliReserDeleteView.as_view(),
        name='delete-reserva',
    ),

    path(
        'delete-reserva-productor/<pk>',
        core_views.EliReserProdDeleteView.as_view(),
        name='delete-reserva-productor',
    ),
    path('mis_reservas',
         core_views.ReservaListView.as_view()
    ),

    path(
        'update-user/<pk>',
        core_views.ActuaUserUpdateView.as_view(),
        name='update-publicacion',
    ),

    path(
        'update-user2/<pk>',
        core_views.ActuaUserUpdateView2.as_view(),
        name='update-publicacion',
    ),
    path(
        'user-edit-pro/<pk>',
        core_views.UserRegisterEditarView.as_view(),
        name='user-edit-pro',
    ),
    path(
        'user-ver-pro/<pk>',
        core_views.UserRegisterVerView.as_view(),
        name='user-ver-pro',
    ),
    path(
        'user-ver-com/<pk>',
        core_views.UserRegisterVerComView.as_view(),
        name='user-ver-com',
    ),
    path(
        'publ-edit-pro/<pk>',
        core_views.PublRegisterEditarView.as_view(),
        name='publ-edit-pro',
    ),

    path(
        'user-edit-com/<pk>',
        core_views.UserRegisterEditarComView.as_view(),
        name='user-edit-com',
    ),
    path(
        'autenticacion/<user>/<pass>',
        core_views.AcutenticacionLink.as_view(),
        name='autenticacion',
    ),
    path(
        'autenticacion_comprador/<user>/<pass>',
        core_views.AcutenticacionCompradorLink.as_view(),
        name='autenticacion',
    ),
    path(
        'login2/',
        core_views.inicio2.as_view(),
        name='login2',
    ),
    path(
        'login3/',
        core_views.inicio3.as_view(),
        name='login3',
    ),

]
urlpatterns += api_urls.urlpatterns
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
