import logging
from os import path

from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.postgres.search import SearchVectorField, SearchQuery, SearchRank
from django.db.models import F
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from geopy.geocoders import Nominatim
from simple_history.models import HistoricalRecords
from django.contrib.auth.models import User
from core.utils import create_thumbnail, rename_img, rename_img2


logger = logging.getLogger(__name__)
THUMBNAIL_BASEWIDTH = 500


class HelpRequestQuerySet(models.QuerySet):
    def filter_by_search_query(self, query):
        query = SearchQuery(query, config="spanish")
        rank = SearchRank(F("search_vector"), query)
        return self.filter(search_vector=query).annotate(rank=rank).order_by("-rank")

# Category: model ...

class Category(models.Model):
    name = models.CharField(max_length=30)
    code = models.CharField(max_length=30, primary_key=True)
    color = models.CharField(max_length=10, default="#000000")
    icon = models.CharField(max_length=30, null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

# FrequentAskedQuestion: model ...

class FrequentAskedQuestion(models.Model):
    """
    Frequent asked question model.
    Issue #6
    """

    # defines rendering order in template. Do not use IntegerField
    order = models.CharField("orden", max_length=3)
    question = models.CharField("Pregunta", max_length=200)
    answer = models.TextField("Respuesta", max_length=1000)

    active = models.BooleanField(default=True)

    class Meta:
        # table actual name
        db_table = "core_faq"

        # default "ORDER BY" statement
        ordering = ["order"]

    def __str__(self):
        return self.question

# HelpRequest: represents a ...

class HelpRequest(models.Model):
    title = models.CharField(
        _("Producto"),
        max_length=200,
        help_text=_("Producto que queres vender"),
        db_index=True,
    )
    #message = name (name=detalle)
    message = models.CharField(
        _("detalleparabusqueda"),
        max_length=200,
        null=True,
        db_index=True,
    )
    #name es descripcion
    name = models.CharField(_("Detalle"), max_length=200)
    #name2 es el nombre del productor
    name2 = models.CharField(_("Nombre completo"), max_length=200,null=True, blank=True,)
    phone = models.CharField(_("Telefono"), max_length=30)
    address = models.CharField(
        _("Direccion"),
        help_text=_("Su dirección, ciudad, barrio, referencias o cómo llegar para obtener ayuda."),
        max_length=400,
        blank=False,
        null=True,
    )
    location = models.PointField(
        _("Localizacion"),
        # XXX Get rid of all HTML out of the model
        help_text=mark_safe('<p style="margin-bottom:5px;font-size:10px;">{}<br>{} <a href="#" class="is-link modal-button" data-target="#myModal" aria-haspopup="true">{}</a></p><p id="div_direccion" style="font-size: 10px; margin-bottom: 5px;"></p>'.format(
        _("Seleccione su ubicación para que la gente pueda encontrarlo, si no desea marcar su casa una buena opción puede ser la estación de policía más cercana o algún otro lugar público cercano."),
        _("Si tiene problemas con este paso"),
        _("Mira esta ayuda")
        )),
        srid=4326,
    )
    picture = models.ImageField(
        _("Foto"),
        upload_to=rename_img,
        help_text=_("En caso de que lo desee puede adjuntar una foto."),
        null=True,
        blank=True,
    )
    resolved = models.BooleanField(default=False, db_index=True)
    active = models.BooleanField(default=True, db_index=True)
    added = models.DateTimeField(_("Added"), auto_now_add=True, null=True, blank=True, db_index=True)
    upvotes = models.IntegerField(default=0, blank=True)
    downvotes = models.IntegerField(default=0, blank=True)
    city = models.CharField(max_length=50, blank=True, default="", editable=False)
    city_code = models.CharField(max_length=50, blank=True, default="", editable=False)
    categories = models.ManyToManyField(Category, blank=True)
    search_vector = SearchVectorField()
    history = HistoricalRecords()
    objects = HelpRequestQuerySet.as_manager()
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    cant_disponible = models.IntegerField(_("Cantidad Disponible"), blank=True, null=True)

    cantidad_disponible = models.CharField(_("Cantidad Disponible"), max_length=100, blank=True, null=True)

    ano_dis = models.IntegerField(_("Año"),blank=True, null=True)

    MESES_CHOICES = (
        ('1', 'Enero'),
        ('2', 'Febrero'),
        ('3', 'Marzo'),
        ('4', 'Abril'),
        ('5', 'Mayo'),
        ('6', 'Junio'),
        ('7', 'Julio'),
        ('8', 'Agosto'),
        ('9', 'Septiembre'),
        ('10', 'Octubre'),
        ('11', 'Noviembre'),
        ('12', 'Diciembre'),
    )

    UNIDAD_CHOICES = (
        ('KILOGRAMOS', 'KILOGRAMOS'),
        ('LITROS', 'LITROS'),
        ('UNIDAD', 'UNIDAD'),
        ('DOCENA', 'DOCENA'),
    )
    unidad_medida = models.CharField(_("Unidad de medida de la cantidad disponible"), max_length=20, choices=UNIDAD_CHOICES, blank=True, null=True)

    mes_dis = models.IntegerField(_("Mes"),choices=MESES_CHOICES,blank=True, null=True)

    dia_dis = models.IntegerField(_("Dia"),blank=True, null=True)

    fecha = models.DateField(_("Fecha de disponibilidad"),blank=True, null=True)

    precio = models.CharField(_("Precio"),
                              help_text=_("Precio por unidad de medida."),
                              max_length=100,
                              default="",
                              blank=True,
                              null=True)
    delivery = models.BooleanField(_("Delivery disponible para entrega de producto"), default=True, blank=True, null=True)
    buscar = models.BooleanField(_("Debe venir a buscar"), default=True, blank=True, null=True)

    @property
    def thumb(self):
        filepath, extension = path.splitext(self.picture.url)
        return f"{filepath}_th{extension}"

    def _get_city(self):
        geolocator = Nominatim(user_agent="ayudapy")
        cordstr = "%s, %s" % self.location.coords[::-1]
        city = ''
        try:
            location = geolocator.reverse(cordstr, language='es')
            if location.raw.get('address'):
                if location.raw['address'].get('city'):
                    city = location.raw['address']['city']
                elif location.raw['address'].get('town'):
                    city = location.raw['address']['town']
                elif location.raw['address'].get('locality'):
                    city = location.raw['address']['locality']
        except Exception as e:
            logger.error(f"Geolocator unavailable: {repr(e)}")
        return city

    def _deactivate_duplicates(self):
        return HelpRequest.objects.filter(phone=self.phone)

    def save(self, *args, **kwargs):
        print(self.id)
        from unidecode import unidecode
        city = self._get_city()
        self.city = city
        self.city_code = unidecode(city).replace(" ", "_")
        self.phone = self.phone.replace(" ", "")
        self.message = self.name
        if not self.id:
            self._deactivate_duplicates()
        return super(HelpRequest, self).save(*args, **kwargs)



    def __str__(self):
        return f"Publicacion: #{self.id} - {self.title} - stock: {self.cant_disponible}"



@receiver(post_save, sender=HelpRequest)
def thumbnail(sender, instance, created, **kwargs):
    if instance.picture:
        try:
            create_thumbnail(
                settings.MEDIA_ROOT + str(instance.picture), THUMBNAIL_BASEWIDTH
            )
        except Exception as e:
            logger.error(f"Error creating thumbnail: {repr(e)}")


# Status: ...

class Status(models.Model):
    name = models.CharField(
        "Nombre del estado",
        max_length=40,
        help_text="Nombre del estado"
    )
    code = models.CharField(
        "Código del estado",
        max_length=10,
        help_text="Código del estado",
        primary_key=True,
    )
    active = models.BooleanField(default=True, db_index=True)


# Devices are going to be registered and identified by cookies (in browsers)
# or by any other thing

class Device(models.Model):
    device_iid = models.AutoField(
        primary_key=True
    )
    device_id = models.CharField(
        "Id Dispositivo",
        max_length=128,
        help_text="Identificador del Dispositivo",
        unique=True
    )
    ua_string = models.CharField(
        "User Agent",
        max_length=512,
        help_text="User Agent",
        null=True,
        blank=True
    )
    status = models.CharField(
        "Estado",
        max_length=32,
        help_text="Estado del Dispositivo",
        default="ACTIVE"
    )
    dev_brand = models.CharField(
        "Marca",
        max_length=128,
        help_text="Marca del Dispositivo",
        null=True,
        blank=True
    )
    dev_family = models.CharField(
        "Familia",
        max_length=128,
        help_text="Familia del Dispositivo",
        null=True,
        blank=True
    )
    dev_model = models.CharField(
        "Modelo",
        max_length=128,
        help_text="Modelo del Dispositivo",
        null=True,
        blank=True
    )
    os_family = models.CharField(
        "SO",
        max_length=128,
        help_text="Sistema Operativo",
        null=True,
        blank=True
    )
    os_version = models.CharField(
        "Version SO",
        max_length=32,
        help_text="Versión del Sistema Operativo",
        null=True,
        blank=True
    )
    browser_family = models.CharField(
        "Navegador",
        max_length=64,
        help_text="Navegador del User Agent",
        null=True,
        blank=True
    )
    browser_version = models.CharField(
        "Version Navegador",
        max_length=32,
        help_text="Versión del Navegador del User Agent",
        null=True,
        blank=True
    )
    created = models.DateTimeField(
        "Creado",
        help_text="Fecha de Creación del Dispositivo",
        auto_now=True
    )
    last_seen = models.DateTimeField(
        "Última Visita",
        help_text="Última Visita del Dispositivo",
        auto_now_add=True
    )
    created_ip_address = models.CharField(
        "IP de creación",
        help_text="Dirección IP desde la que fue creado",
        max_length=32,
        null=True,
        blank=True
    )
    push_notification_token = models.CharField(
        "Token de Notificación",
        help_text="Token de Notificación para envíos tipo PUSH",
        max_length=128,
        null=True,
        blank=True
    )


# User: to represent a user in ayudapy

class User(models.Model):
    user_iid = models.AutoField(
        primary_key=True
    )
    user_type = models.CharField(
        "Tipo",
        max_length=32,
        help_text="Tipo de usuario"
    )
    user_value = models.CharField(
        "Sujeto",
        max_length=128,
        help_text="Valor/Nombre de Usuario"
    )
    name = models.CharField(
        "Nombre Completo",
        max_length=512,
        help_text="Nombre Completo del Usuario",
        null=True,
        blank=True
    )
    email = models.CharField(
        "Correo Electrónico",
        max_length=256,
        help_text="Correo Electrónico del Usuario",
        null=True,
        blank=True
    )
    phone = models.CharField(
        "Teléfono",
        max_length=64,
        help_text="Número Telefónico del Usuario",
        null=True,
        blank=True
    )
    created = models.DateTimeField(
        "Creado",
        help_text="Fecha de Creación del Dispositivo",
        auto_now=True
    )
    last_seen = models.DateTimeField(
        "Última Visita",
        help_text="Última Visita del Dispositivo",
        auto_now_add=True
    )
    created_ip_address = models.CharField(
        "IP de creación",
        help_text="Dirección IP desde la que fue creado",
        max_length=32,
        null=True,
        blank=True
    )
    address = models.CharField(
        "Dirección",
        help_text="Dirección por defecto del Usuario",
        max_length=400,
        blank=True,
        null=True,
    )
    location = models.PointField(
        "Ubicación",
        help_text="Ubicación por defecto del Usuario",
        blank=True,
        null=True,
    )
    city = models.CharField(
        "Ciudad",
        max_length=30,
        help_text="Dirección por defecto del Usuario",
        blank=True,
        null=True
    )
    city_code = models.CharField(
        "Código Ciudad",
        max_length=50,
        help_text="Código de Ciudad por Defecto del Usuario",
        blank=True,
        null=True
    )
    password_hash = models.CharField(
        "Password",
        max_length=64,
        help_text="Contraseña del Usuario",
        blank=True,
        null=True
    )
    password_salt = models.CharField(
        "Password Salta",
        max_length=64,
        help_text="Salt de Contraseña del Usuario",
        blank=True,
        null=True
    )
    history = HistoricalRecords()


class HelpRequestOwner(models.Model):
    help_request = models.OneToOneField(
        HelpRequest,
        on_delete=models.CASCADE,
        primary_key=True
    )
    user_iid = models.ForeignKey(User, on_delete=models.CASCADE)

from .functions import *
from django.core.mail import send_mail
from django.contrib.auth.models import User
class UserAux(models.Model):
    username = models.CharField(unique=True, max_length=120)
    nombre = models.CharField(max_length=30, blank=True, null=True)
    apellido = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    password = models.CharField(max_length=120, blank=True, null=True)
    telefono = models.CharField(max_length=120, blank=True, null=True)
    password_form1 = models.CharField("Contraseña",max_length=120, blank=True, null=True)
    password_form2 = models.CharField("Contraseña",max_length=120, blank=True, null=True)
    codigo = models.CharField(max_length=6, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    foto = models.ImageField(
        _("Foto"),
        upload_to='pedidos/', blank=True,null=True)
    upload = models.FileField(_("Documento de algun gremio"),upload_to='pedidos/', blank=True,null=True)

    bandera_foto = models.CharField(max_length=120 , blank=True, null=True)
    bandera_upload = models.CharField(max_length=120, blank=True, null=True)


    def crearUserAux(self, username_, email_, password_,foto_,upload_,nombre_, apellido_):
        codigo = str(code_generator())

        emails = [email_]

        ua = UserAux()
        ua.username = username_
        ua.email = email_
        ua.password = password_
        ua.codigo = codigo
        ua.foto = foto_
        ua.upload = upload_
        ua.nombre = nombre_
        ua.apellido = apellido_
        ua.save()

        # enviar el codigo al email del user
        print('mail esta por se enviado 01')
        asunto = 'Confirmacion de email'
        mensaje = 'Codigo de verificacion: ' + codigo + " - Su User es: " + username_ + "y su pass: " + password_
        email_remitente = 'ivancaceres17@fpuna.edu.py'
        #
        print('mail esta por se enviado')
        send_mail(asunto, mensaje, email_remitente, emails)
        # redirigir a pantalla de valdiacion

class UserAux2(models.Model):
    username = models.CharField(max_length=120, blank=True, null=True)
    nombre = models.CharField(max_length=30, blank=True, null=True)
    apellido = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    password = models.CharField(max_length=120, blank=True, null=True)
    codigo = models.CharField(max_length=6, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    foto = models.ImageField(
        _("Foto"),
        upload_to='pedidos/', blank=True,null=True)
    upload = models.FileField(_("Documento de algun gremio"),upload_to='pedidos/', blank=True,null=True)

    bandera_foto = models.CharField(max_length=120 , blank=True, null=True)
    bandera_upload = models.CharField(max_length=120, blank=True, null=True)



class Reserva(models.Model):
    publicacion = models.ForeignKey(HelpRequest, on_delete=models.CASCADE, blank=True, null=True)
    cantidad = models.IntegerField()
    detalle = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    producto = models.CharField(max_length=120, blank=True, null=True)

    def __str__(self):
        return f"<Reserva: #{self.id} - {self.cantidad}>"

    def hola(self):
        print('hola2')
        return 'hola2'

class UserDatosExtras(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    foto = models.ImageField(
        _("Foto"),
        upload_to=rename_img,
        help_text=_(
            "In case you want you can attach a photo related to your request. It is optional but it can help people better understand your situation."),
        null=True,
        blank=True,
    )
    upload = models.FileField(upload_to='uploads/')
    telefono = models.CharField(max_length=30, blank=True, null=True)

    nombre = models.CharField(max_length=30, blank=True, null=True)
    apellido = models.CharField(max_length=150, blank=True, null=True)

    def nombreCompleto(self):
        return self.nombre + " " + self.apellido

class HelpRequest_2(models.Model):
    title = models.CharField(
        _("Producto"),
        max_length=200,
        help_text=_("Producto que queres vender"),
        db_index=True,
    )
    #message = name (name=detalle)
    message = models.CharField(
        _("detalleparabusqueda"),
        max_length=200,
        null=True,
        db_index=True,
    )
    #name es descripcion
    name = models.CharField(_("Detalle"), max_length=200)
    #name2 es el nombre del productor
    name2 = models.CharField(_("Nombre completo"), max_length=200,null=True, blank=True,)
    phone = models.CharField(_("Telephone contact"), max_length=30)
    address = models.CharField(
        _("Address"),
        help_text=_("Your address, city, neighborhood, references, or how to get there, to get help"),
        max_length=400,
        blank=False,
        null=True,
    )
    location = models.PointField(
        _("Location"),
        # XXX Get rid of all HTML out of the model
        help_text=mark_safe('<p style="margin-bottom:5px;font-size:10px;">{}<br>{} <a href="#" class="is-link modal-button" data-target="#myModal" aria-haspopup="true">{}</a></p><p id="div_direccion" style="font-size: 10px; margin-bottom: 5px;"></p>'.format(
        _("Select your location so that people can find you, if you do not want to mark your home a good option may be the nearest police station or some other nearby public place."),
        _("If you have problems with this step"),
        _("Check out this help")
        )),
        srid=4326,
    )
    picture = models.ImageField(
        _("Photo"),
        upload_to=rename_img,
        help_text=_("In case you want you can attach a photo related to your request. It is optional but it can help people better understand your situation."),
        null=True,
        blank=True,
    )
    resolved = models.BooleanField(default=False, db_index=True)
    active = models.BooleanField(default=True, db_index=True)
    added = models.DateTimeField(_("Added"), auto_now_add=True, null=True, blank=True, db_index=True)
    upvotes = models.IntegerField(default=0, blank=True)
    downvotes = models.IntegerField(default=0, blank=True)
    city = models.CharField(max_length=50, blank=True, default="", editable=False)
    city_code = models.CharField(max_length=50, blank=True, default="", editable=False)
    categories = models.ManyToManyField(Category, blank=True)
    search_vector = SearchVectorField()
    history = HistoricalRecords()
    objects = HelpRequestQuerySet.as_manager()
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    cant_disponible = models.IntegerField(_("Cantidad Disponible"), blank=True, null=True)

    cantidad_disponible = models.CharField(_("Cantidad Disponible"), max_length=100, blank=True, null=True)

    ano_dis = models.IntegerField(_("Año"),blank=True, null=True)

    MESES_CHOICES = (
        ('1', 'Enero'),
        ('2', 'Febrero'),
        ('3', 'Marzo'),
        ('4', 'Abril'),
        ('5', 'Mayo'),
        ('6', 'Junio'),
        ('7', 'Julio'),
        ('8', 'Agosto'),
        ('9', 'Septiembre'),
        ('10', 'Octubre'),
        ('11', 'Noviembre'),
        ('12', 'Diciembre'),
    )

    UNIDAD_CHOICES = (
        ('KILOGRAMOS', 'KILOGRAMOS'),
        ('LITROS', 'LITROS'),
        ('UNIDAD', 'UNIDAD'),
        ('DOCENA', 'DOCENA'),
    )
    unidad_medida = models.CharField(_("Unidad de medida de la cantidad disponible"), max_length=20, choices=UNIDAD_CHOICES, blank=True, null=True)

    mes_dis = models.IntegerField(_("Mes"),choices=MESES_CHOICES,blank=True, null=True)

    dia_dis = models.IntegerField(_("Dia"),blank=True, null=True)

    fecha = models.DateField(_("Fecha de disponibilidad"),blank=True, null=True)

    precio = models.CharField(_("Precio"),
                              help_text=_("Precio por unidad de medida."),
                              max_length=100,
                              default="",
                              blank=True,
                              null=True)
    delivery = models.BooleanField(_("Delivery disponible para entrega de producto"), default=True, blank=True, null=True)
    buscar = models.BooleanField(_("Debe venir a buscar"), default=True, blank=True, null=True)

    @property
    def thumb(self):
        filepath, extension = path.splitext(self.picture.url)
        return f"{filepath}_th{extension}"

    def _get_city(self):
        geolocator = Nominatim(user_agent="ayudapy")
        cordstr = "%s, %s" % self.location.coords[::-1]
        city = ''
        try:
            location = geolocator.reverse(cordstr, language='es')
            if location.raw.get('address'):
                if location.raw['address'].get('city'):
                    city = location.raw['address']['city']
                elif location.raw['address'].get('town'):
                    city = location.raw['address']['town']
                elif location.raw['address'].get('locality'):
                    city = location.raw['address']['locality']
        except Exception as e:
            logger.error(f"Geolocator unavailable: {repr(e)}")
        return city

    def _deactivate_duplicates(self):
        return HelpRequest.objects.filter(phone=self.phone)

    def save(self, *args, **kwargs):
        print(self.id)
        from unidecode import unidecode
        city = self._get_city()
        self.city = city
        self.city_code = unidecode(city).replace(" ", "_")
        self.phone = self.phone.replace(" ", "")
        self.message = self.name
        if not self.id:
            self._deactivate_duplicates()
        return super(HelpRequest, self).save(*args, **kwargs)



    def __str__(self):
        return f"Publicacion: #{self.id} - {self.title} - stock: {self.cant_disponible}"


class LoginUserCom(models.Model):
    user = models.CharField(_("Usuario"), max_length=50)
    password = models.CharField(_("Contraseña"), max_length=50)

class PassOlvidada(models.Model):
    email = models.EmailField(_("Email"), max_length=50)
    username = models.CharField(_("Usuario"), max_length=50)