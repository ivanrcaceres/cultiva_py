from django import forms
from django.forms import HiddenInput
from leaflet.forms.fields import PointField
from django.core.exceptions import NON_FIELD_ERRORS
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from .models import HelpRequest, Reserva, UserDatosExtras, LoginUserCom, PassOlvidada

from django.contrib.auth.models import User


class HelpRequestForm(forms.ModelForm):
    location = PointField(
        label="Ubicación",
        # XXX Move all HTML to the corresponding templates
        error_messages={'required': mark_safe('{}\n<br>{} <a href="#" class="is-link modal-button" data-target="#myModal" aria-haspopup="true">{}</a></p><p id="div_direccion" style="font-size: 10px; margin-bottom: 5px;"></p>'.format(
            _("Olvidaste marcar tu ubicación en el mapa"),
            _("Si tiene problemas con este paso"),
            _("Mira esta ayuda"),
            ))},
        help_text=mark_safe('<p style="margin-bottom:5px;font-size:10px;">{}.<br>{} <a href="#" class="is-link modal-button" data-target="#myModal" aria-haspopup="true">{}</a></p><p id="div_direccion" style="font-size: 10px; margin-bottom: 5px;"></p>'.format(
            _("Seleccione su ubicación para que la gente pueda encontrarlo."),
            _("Si tiene problemas con este paso"),
            _("Mira esta ayuda"),
            )),
        )

    # UNIDAD_CHOICES = (
    #     ('1', 'KILOGRAMOS'),
    #     ('2', 'LITROS'),
    #     ('3', 'UNIDAD'),
    #     ('4', 'DOCENA'),
    # )
    UNIDAD_CHOICES = (
        ('KILOGRAMOS', 'KILOGRAMOS'),
        ('LITROS', 'LITROS'),
        ('UNIDAD', 'UNIDAD'),
        ('DOCENA', 'DOCENA'),
    )

    class Meta:
        model = HelpRequest
        fields = (
            "title",
            "name",
            "name2",
            "cant_disponible",
            "unidad_medida",
            "precio",
            "fecha",
            "delivery",
            "buscar",
            #"categories",

            "phone",
            "location",
            "address",
            "picture",
            "user_id"
        )
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "input",
                    "placeholder": _("Ejemplo: Zapallo"),
                }
            ),
            "name2": forms.TextInput(
                attrs={
                    "class": "input",
                }
            ),

            "fecha": forms.TextInput(attrs={"class": "input",'type': 'date'}),
            "cant_disponible": forms.TextInput(attrs={"class": "input","placeholder": _("Ejemplo: 5000 (solo numero)")}),
            "precio": forms.TextInput(attrs={"class": "input","placeholder": _("Ejemplo: 10.000 por kilogramos")}),
            "name": forms.TextInput(attrs={"class": "input"}),
            "user_id": forms.TextInput(attrs={'readonly':'',"class": "input"}),
            "phone": forms.TextInput(attrs={"class": "input", "type": "tel"}),
            "address": forms.TextInput(attrs={"class": "input"}),
            # 'unidad_medida': forms.SelectField()
        }
        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': _("Registration already entered, cannot duplicate the same request."),
            }
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('userr')
        print('gogogogogogo')
        print(user)

        super(HelpRequestForm, self).__init__(*args, **kwargs)
        self.fields['phone'].initial = '1234569999'
        a = User.objects.get(id=user)
        print('print(a)')
        print(a)
        # aqui pongo en el formulario el user y lo oculto
        self.fields['user_id'].initial = a
        self.fields['user_id'].widget = HiddenInput()

    # def save(self, *args, **kwargs):
    #     user = kwargs.pop('userr')
    #     print('del metodo save')
    #     print(user)
    #     super(HelpRequestForm, self).save(*args, **kwargs)

    # def save(self, *args, **kwargs):
    #     user = kwargs.pop('userr')
    #     print('del metodo save')
    #     print(user)
    #     super().save(*args, **kwargs)




''' aca abajo va lo de cultiva  '''

from django.contrib.auth import authenticate

class LoginForm(forms.ModelForm):
    class Meta:
        model = LoginUserCom
        fields = (
            "user",
            "password"
        )
        widgets = {
            "user": forms.TextInput(
                attrs={
                    "class": "input",
                }
            ),
            "password": forms.PasswordInput(
                attrs={
                    "class": "input",
                }
            )


        }
    # username = forms.CharField(
    #     label='username',
    #     required=True,
    #     widget=forms.TextInput(
    #         attrs={
    #             'placeholder': 'usernmae',
    #         }
    #     )
    # )
    # password = forms.CharField(
    #     label='Contraseña',
    #     required=True,
    #     widget=forms.PasswordInput(
    #         attrs={
    #             'placeholder': 'contraseña'
    #         }
    #     )
    # )
    #
    def clean(self):
        cleaned_data = super(LoginForm, self).clean()
        username = self.cleaned_data['user']
        password = self.cleaned_data['password']

        if not authenticate(username=username, password=password):
            raise forms.ValidationError('Los datos de usuario no son correctos')

        return self.cleaned_data

from .models import UserAux, UserAux2
class UserRegisterForm(forms.ModelForm):
    # password1 = forms.CharField(
    #     label='Contraseña',
    #     required=True,
    #     widget=forms.PasswordInput(
    #         attrs={
    #             'placeholder': 'Contraseña'
    #         }
    #     )
    # )
    # password2 = forms.CharField(
    #     label='Contraseña',
    #     required=True,
    #     widget=forms.PasswordInput(
    #         attrs={
    #             'placeholder': 'Repetir Contraseña'
    #         }
    #     )
    # )

    class Meta:
        """Meta definition for Userform."""

        model = UserAux
        fields = (
            'username',
            'nombre',
            'apellido',
            'email',
            'telefono',
            'foto',
            'upload',
            'password_form1',
            'password_form2'
        )
        widgets = {
            "username": forms.TextInput(
                attrs={
                    "class": "input",
                }
            ),
            "nombre": forms.TextInput(
                attrs={
                    "class": "input",
                }
            ),
            "apellido": forms.TextInput(
                attrs={
                    "class": "input",
                }
            ),
            "email": forms.TextInput(
                attrs={
                    "class": "input",
                }
            ),
            "telefono": forms.TextInput(
                attrs={
                    "class": "input",
                }
            ),
            "password_form1": forms.PasswordInput(
                attrs={
                    "class": "input",
                }
            ),
            "password_form2": forms.PasswordInput(
                attrs={
                    "class": "input",
                }
            ),


        }

    def clean_password_form2(self):
        print(self.cleaned_data['password_form1'])
        if self.cleaned_data['password_form1'] != self.cleaned_data['password_form1']:
            self.add_error('password_form1', 'Las contraseñas no son iguales')

class UserRegisterEditarForm(forms.ModelForm):
    class Meta:
        """Meta definition for Userform."""

        model = UserAux2
        fields = (
            # 'username',
            'nombre',
            'apellido',
            'email',
            'foto',
            'upload',
            'bandera_upload',
            'bandera_foto',
        )
        widgets = {
            "nombre": forms.TextInput(
                attrs={
                    "class": "input",
                    "placeholder": _("Ejemplo: Zapallo"),
                }
            ),
            "apellido": forms.TextInput(
                attrs={
                    "class": "input",
                }
            ),
            "email": forms.TextInput(
                attrs={"class": "input", "placeholder": _("Ejemplo: 5000 (solo numero)")}),
            "precio": forms.TextInput(attrs={"class": "input", "placeholder": _("Ejemplo: 10.000 por kilogramos")}),
            "name": forms.TextInput(attrs={"class": "input"}),
            "user_id": forms.TextInput(attrs={'readonly': '', "class": "input"}),
            "phone": forms.TextInput(attrs={"class": "input", "type": "tel"}),
            "address": forms.TextInput(attrs={"class": "input"}),
            # 'categories': forms.SelectMultiple(attrs={"style": "display:none;"}),
        }
    def __init__(self, pk, *args, **kwargs):
        print(pk)
        print('#############')
        a = UserAux.objects.get(pk=pk)
        super(UserRegisterEditarForm, self).__init__(*args, **kwargs)
        self.fields['nombre'].initial = a.nombre
        self.fields['apellido'].initial = a.apellido
        self.fields['email'].initial = a.email
        if a.foto:
            self.fields['bandera_foto'].initial = 'si'
        else:
            self.fields['bandera_foto'].initial = ''
        if a.upload:
            self.fields['bandera_upload'].initial = 'si'
        else:
            self.fields['bandera_upload'].initial = ''

        self.fields['bandera_foto'].widget = HiddenInput()
        self.fields['bandera_upload'].widget = HiddenInput()
        # self.fields['username'].widget = HiddenInput()
        # self.fields['nombre'].widget = HiddenInput()
        # self.fields['apellido'].widget = HiddenInput()
        # self.fields['email'].widget = HiddenInput()

class UserRegisterVerForm(forms.ModelForm):
    class Meta:
        """Meta definition for Userform."""

        model = UserAux2
        fields = (
            # 'username',
            'nombre',
            'apellido',
            'email',
            'foto',
            'upload',
            'bandera_upload',
            'bandera_foto',
        )
        widgets = {
            "nombre": forms.TextInput(
                attrs={
                    "class": "input",
                    "placeholder": _("Ejemplo: Zapallo"), 'readonly': 'readonly',
                }
            ),
            "apellido": forms.TextInput(
                attrs={
                    "class": "input", 'readonly': 'readonly',
                }
            ),
            "email": forms.TextInput(
                attrs={"class": "input" , 'readonly': 'readonly',}),
            "precio": forms.TextInput(attrs={"class": "input", "placeholder": _("Ejemplo: 10.000 por kilogramos")}),
            "name": forms.TextInput(attrs={"class": "input"}),
            "user_id": forms.TextInput(attrs={'readonly': '', "class": "input"}),
            "phone": forms.TextInput(attrs={"class": "input", "type": "tel"}),
            "address": forms.TextInput(attrs={"class": "input"}),
            # 'categories': forms.SelectMultiple(attrs={"style": "display:none;"}),
        }
    def __init__(self, pk, *args, **kwargs):
        print(pk)
        print('#############')
        a = UserAux.objects.get(pk=pk)
        super(UserRegisterVerForm, self).__init__(*args, **kwargs)
        self.fields['nombre'].initial = a.nombre
        self.fields['apellido'].initial = a.apellido
        self.fields['email'].initial = a.email
        if a.foto:
            self.fields['bandera_foto'].initial = 'si'
        else:
            self.fields['bandera_foto'].initial = ''
        if a.upload:
            self.fields['bandera_upload'].initial = 'si'
        else:
            self.fields['bandera_upload'].initial = ''

        self.fields['bandera_foto'].widget = HiddenInput()
        self.fields['bandera_upload'].widget = HiddenInput()
        # self.fields['username'].widget = HiddenInput()
        # self.fields['nombre'].widget = HiddenInput()
        # self.fields['apellido'].widget = HiddenInput()
        # self.fields['email'].widget = HiddenInput()






class UserRegisterComprForm(forms.ModelForm):
    # password1 = forms.CharField(
    #     label='Contraseña',
    #     required=True,
    #     widget=forms.PasswordInput(
    #         attrs={
    #             'placeholder': 'Contraseña'
    #         }
    #     )
    # )
    # password2 = forms.CharField(
    #     label='Contraseña',
    #     required=True,
    #     widget=forms.PasswordInput(
    #         attrs={
    #             'placeholder': 'Repetir Contraseña'
    #         }
    #     )
    # )

    class Meta:
        """Meta definition for Userform."""

        model = UserAux
        fields = (
            'username',
            'nombre',
            'apellido',
            'email',
            'password_form1',
            'password_form2'
        )
        widgets = {
            "username": forms.TextInput(
                attrs={
                    "class": "input",
                }
            ),
            "nombre": forms.TextInput(
                attrs={
                    "class": "input",
                }
            ),
            "apellido": forms.TextInput(
                attrs={
                    "class": "input",
                }
            ),
            "email": forms.TextInput(
                attrs={
                    "class": "input",
                }
            ),
            "telefono": forms.TextInput(
                attrs={
                    "class": "input",
                }
            ),
            "password_form1": forms.PasswordInput(
                attrs={
                    "class": "input",
                }
            ),
            "password_form2": forms.PasswordInput(
                attrs={
                    "class": "input",
                }
            ),

        }

    def clean_password_form2(self):
        print(self.cleaned_data['password_form1'])
        if self.cleaned_data['password_form1'] != self.cleaned_data['password_form1']:
            self.add_error('password_form1', 'Las contraseñas no son iguales')


class UserRegisterForm2(forms.ModelForm):
    class Meta:
        """Meta definition for Userform."""

        model = UserAux
        fields = (
            'username',
            'nombre',
            'apellido',
            'email',
            'foto',
            'upload',
        )


class UserRegisterForm3(forms.ModelForm):
    class Meta:
        """Meta definition for Userform."""

        model = UserAux
        fields = (
            'username',
            'nombre',
            'apellido',
            'email',
            'foto',
            'upload',
        )



class VerificationForm(forms.Form):
    codregistro = forms.CharField(required=True)
    username = forms.CharField(required=True)

    def clean(self):
        res = super(VerificationForm, self).clean()
        codigo = self.cleaned_data['codregistro']
        username2 = self.cleaned_data['username']
        idDeUser = 0
        a = UserAux.objects.filter(username=username2)
        if len(codigo) == 6:
            print(a[0].codigo)
            print(a[0].id)
            print('uuu')
            if(a[0].codigo == codigo):
                aaa = User.objects.filter(username=username2).update(is_active=True)
            else:
                raise forms.ValidationError('el codigo es incorrecto')
        else:
            raise forms.ValidationError('el codigo es incorrecto')

        return res
from django.core.mail import send_mail
from .functions import code_generator
class PassOlvidadaForm(forms.ModelForm):
    class Meta:
        model = PassOlvidada
        fields = (
            "email",
            "username"
        )
        widgets = {
            "email": forms.TextInput(
                attrs={
                    "class": "input",
                }
            ),
            "username": forms.TextInput(
                attrs={
                    "class": "input",
                }
            )


        }

    def clean(self):
        res = super(PassOlvidadaForm, self).clean()
        emails = []
        mail01 = self.cleaned_data['email']
        username01 = self.cleaned_data['username']
        emails.append(mail01)
        user = User.objects.filter(username=username01, email=mail01)
        print(user)
        if user:
            print('mail esta por se enviado 01')
            print(user[0].email)
            print(user[0].username)

            user2 = User()
            user2 = user[0]
            contra = code_generator()
            print(contra)
            user2.set_password(contra)
            user2.save()
            asunto = 'Nueva Contrasena'
            mensaje = 'Las nuevas credenciales son: ' + user2.username + " " + user2.email + " " + contra
            email_remitente = 'ivancaceres17@fpuna.edu.py'
            print('mail esta por se enviado')
            send_mail(asunto, mensaje, email_remitente, emails)
        if not user:
            print("chau")
        return res


class PerfilForm(forms.ModelForm):
    class Meta:
        """Meta definition for Userform."""

        model = User
        fields = '__all__'


class PerfilUserForm(forms.ModelForm):
    class Meta:
        """Meta definition for Userform."""

        model = User
        fields = '__all__'

class HelpRequestForm2(forms.ModelForm):
    location = PointField(
        label="Ubicación",
        # XXX Move all HTML to the corresponding templates
        error_messages={'required': mark_safe('{}\n<br>{} <a href="#" class="is-link modal-button" data-target="#myModal" aria-haspopup="true">{}</a></p><p id="div_direccion" style="font-size: 10px; margin-bottom: 5px;"></p>'.format(
            _("You forgot to mark your location on the map"),
            _("If you have problems with this step"),
            _("Check out this help"),
            ))},
        help_text=mark_safe('<p style="margin-bottom:5px;font-size:10px;">{}.<br>{} <a href="#" class="is-link modal-button" data-target="#myModal" aria-haspopup="true">{}</a></p><p id="div_direccion" style="font-size: 10px; margin-bottom: 5px;"></p>'.format(
            _("Select your location so that people can find you, if you do not want to mark your home a good option may be the nearest police station or some other nearby public place."),
            _("If you have problems with this step"),
            _("Check out this help"),
            )),
        )

    UNIDAD_CHOICES = (
        ('1', 'KILOGRAMOS'),
        ('2', 'LITROS'),
        ('3', 'UNIDAD'),
        ('4', 'DOCENA'),
    )

    class Meta:
        model = HelpRequest
        fields = (
            "title",
            # "message",
            "name",
            "cant_disponible",
            "unidad_medida",
            "precio",
            "fecha",
            "delivery",
            "buscar",
            #"categories",
            "name2",
            "phone",
            "location",
            "address",
            "picture",
            "user_id",
            "id"
        )
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "input",
                    "placeholder": _("Ejemplo: Zapallo"),
                }
            ),

            "name2": forms.TextInput(
                attrs={
                    "class": "input",
                }
            ),

            # "message": forms.Textarea(
            #     attrs={
            #         "class": "textarea",
            #         "rows": 4,
            #         "placeholder": _("Example: Due to the current situation I am in need of masks and cleaning products, any help, even a minimal one, will help me. Thank you so much!"),
            #     }
            # ),

            "fecha": forms.TextInput(attrs={"class": "input",'type': 'date'}),
            "cant_disponible": forms.TextInput(attrs={"class": "input","placeholder": _("Ejemplo: 5000 (solo numero)")}),
            "precio": forms.TextInput(attrs={"class": "input","placeholder": _("Ejemplo: 10.000 por kilogramos")}),
            "name": forms.TextInput(attrs={"class": "input"}),
            "user_id": forms.TextInput(attrs={'readonly':'',"class": "input"}),
            "phone": forms.TextInput(attrs={"class": "input", "type": "tel"}),
            "address": forms.TextInput(attrs={"class": "input"}),
            #'categories': forms.SelectMultiple(attrs={"style": "display:none;"}),
        }
        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': _("Registration already entered, cannot duplicate the same request."),
            }
        }

    def __init__(self, *args, **kwargs):
        #self.location = ''
        super(HelpRequestForm2, self).__init__(*args, **kwargs)
        # aqui pongo en el formulario el user y lo oculto
        self.fields['user_id'].widget = HiddenInput()
        # self.fields['pk'].widget = HiddenInput()


class ReservaForm(forms.ModelForm):

    class Meta:
        """Meta definition for ReservaForm."""

        model = Reserva
        fields = (
            "publicacion",
            "cantidad",
            "detalle",
            "user",
            "producto"
        )

        widgets = {
            "publicacion": forms.TextInput(attrs={"class": "input"}),
            "detalle": forms.TextInput(attrs={"class": "input"}),
            "producto": forms.TextInput(attrs={"class": "input", 'readonly': 'readonly'}),
            "cantidad": forms.NumberInput(
                attrs={
                    "class": "input",
                }
            ),


        }

    def __init__(self, pk,user_id, *args, **kwargs):
        a = HelpRequest.objects.get(pk=pk)
        print(a.user_id.id)
        u = User.objects.get(pk=user_id)

        super(ReservaForm, self).__init__(*args, **kwargs)
        self.fields['publicacion'].initial = a
        self.fields['publicacion'].widget = HiddenInput()

        self.fields['user'].initial = u
        self.fields['user'].widget = HiddenInput()


        self.fields['producto'].initial = a.title
        # self.fields['producto'].widget = Readonly()

class ReservaForm2(forms.ModelForm):

    class Meta:
        """Meta definition for ReservaForm."""

        model = Reserva
        fields = (
            "publicacion",
            "cantidad",
            "detalle",
            "producto",
            "user"
        )
        widgets = {
            "publicacion": forms.TextInput(attrs={"class": "input"}),
            "detalle": forms.TextInput(attrs={"class": "input"}),
            "producto": forms.TextInput(attrs={"class": "input", 'readonly': 'readonly'}),
            "cantidad": forms.NumberInput(
                attrs={
                    "class": "input",
                }
            ),

        }

    # widgets = {
    #     'producto': forms.TextInput(attrs={'readonly':'', 'class':'input'})
    # }

    def __init__(self, *args, **kwargs):
        # print(pk)
        # a = Reserva.objects.get(pk=pk)
        # print(a.title)
        # u = User.objects.get(pk=a.user_id.id)

        super(ReservaForm2, self).__init__(*args, **kwargs)
        # self.fields['publicacion'].initial = a
        self.fields['publicacion'].widget = HiddenInput()

        # self.fields['user'].initial = u
        self.fields['user'].widget = HiddenInput()

        # self.fields['producto'].widget = HiddenInput()

        # self.fields['producto'].initial = a.title

class ReservaVerForm(forms.ModelForm):

    class Meta:
        """Meta definition for ReservaForm."""

        model = Reserva
        fields = (
            "publicacion",
            "cantidad",
            "detalle",
            "producto",
            "user"
        )
        widgets = {
            "publicacion": forms.TextInput(attrs={"class": "input"}),
            "detalle": forms.TextInput(attrs={"class": "input", 'readonly': 'readonly'}),
            "producto": forms.TextInput(attrs={"class": "input", 'readonly': 'readonly'}),
            "cantidad": forms.NumberInput(
                attrs={
                    "class": "input", 'readonly': 'readonly'
                }
            ),

        }

    # widgets = {
    #     'producto': forms.TextInput(attrs={'readonly':'', 'class':'input'})
    # }

    def __init__(self, *args, **kwargs):
        # print(pk)
        # a = Reserva.objects.get(pk=pk)
        # print(a.title)
        # u = User.objects.get(pk=a.user_id.id)

        super(ReservaVerForm, self).__init__(*args, **kwargs)
        # self.fields['publicacion'].initial = a
        self.fields['publicacion'].widget = HiddenInput()

        # self.fields['user'].initial = u
        self.fields['user'].widget = HiddenInput()

        # self.fields['producto'].widget = HiddenInput()

        # self.fields['producto'].initial = a.title


class HelpRequestForm3(forms.ModelForm):
    location = PointField(
        label="Ubicación",
        # XXX Move all HTML to the corresponding templates
        error_messages={'required': mark_safe('{}\n<br>{} <a href="#" class="is-link modal-button" data-target="#myModal" aria-haspopup="true">{}</a></p><p id="div_direccion" style="font-size: 10px; margin-bottom: 5px;"></p>'.format(
            _("You forgot to mark your location on the map"),
            _("If you have problems with this step"),
            _("Check out this help"),
            ))},
        help_text=mark_safe('<p style="margin-bottom:5px;font-size:10px;">{}.<br>{} <a href="#" class="is-link modal-button" data-target="#myModal" aria-haspopup="true">{}</a></p><p id="div_direccion" style="font-size: 10px; margin-bottom: 5px;"></p>'.format(
            _("Seleccione su ubicación."),
            _("Si tiene problemas con este paso"),
            _("Mira esta ayuda  "),
            )),
        )

    UNIDAD_CHOICES = (
        ('1', 'KILOGRAMOS'),
        ('2', 'LITROS'),
        ('3', 'UNIDAD'),
        ('4', 'DOCENA'),
    )

    class Meta:
        model = HelpRequest
        fields = (
            "title",
            # "message",
            "name",
            "cant_disponible",
            "unidad_medida",
            "precio",
            "fecha",
            "delivery",
            "buscar",
            #"categories",
            "name2",
            "phone",
            "location",
            "address",
            "picture",
            "user_id",
            "id"
        )
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "input",
                    "placeholder": _("Ejemplo: Zapallo"),
                }
            ),

            "name2": forms.TextInput(
                attrs={
                    "class": "input",
                }
            ),

            # "message": forms.Textarea(
            #     attrs={
            #         "class": "textarea",
            #         "rows": 4,
            #         "placeholder": _("Example: Due to the current situation I am in need of masks and cleaning products, any help, even a minimal one, will help me. Thank you so much!"),
            #     }
            # ),

            "fecha": forms.TextInput(attrs={"class": "input",'type': 'date'}),
            "cant_disponible": forms.TextInput(attrs={"class": "input","placeholder": _("Ejemplo: 5000 (solo numero)")}),
            "precio": forms.TextInput(attrs={"class": "input","placeholder": _("Ejemplo: 10.000 por kilogramos")}),
            "name": forms.TextInput(attrs={"class": "input"}),
            "user_id": forms.TextInput(attrs={'readonly':'',"class": "input"}),
            "phone": forms.TextInput(attrs={"class": "input", "type": "tel"}),
            "address": forms.TextInput(attrs={"class": "input"}),
            #'categories': forms.SelectMultiple(attrs={"style": "display:none;"}),
        }
        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': _("Registration already entered, cannot duplicate the same request."),
            }
        }

    def __init__(self,pk, *args, **kwargs):
        #self.location = ''
        super(HelpRequestForm3, self).__init__(*args, **kwargs)
        # aqui pongo en el formulario el user y lo oculto
        self.fields['user_id'].widget = HiddenInput()
        respu = HelpRequest.objects.get(pk=pk)
        self.fields['title'].initial = respu.title
        # self.fields['message'].initial = respu.message
        self.fields['location'].initial = respu.location
        self.fields['name'].initial = respu.name
        self.fields['cant_disponible'].initial = respu.cant_disponible
        self.fields['unidad_medida'].initial = respu.unidad_medida
        self.fields['precio'].initial = respu.precio
        self.fields['fecha'].initial = respu.fecha
        self.fields['delivery'].initial = respu.delivery
        self.fields['buscar'].initial = respu.buscar
        self.fields['name2'].initial = respu.name2
        self.fields['phone'].initial = respu.phone
        self.fields['address'].initial = respu.address
        self.fields['user_id'].initial = respu.user_id
        # self.fields['picture'].initial = respu.picture
        # print(pk)
        # print(pk)
        # self.fields['pk'].widget = HiddenInput()

class UserRegisterEditarComForm(forms.ModelForm):
    class Meta:
        """Meta definition for Userform."""

        model = UserAux2
        fields = (
            # 'username',
            'nombre',
            'apellido',
            'email',
            'bandera_upload',
            'bandera_foto',
        )
        widgets = {
            "nombre": forms.TextInput(
                attrs={
                    "class": "input",
                    "placeholder": _("Ejemplo: Zapallo"),
                }
            ),
            "apellido": forms.TextInput(
                attrs={
                    "class": "input",
                }
            ),
            "email": forms.TextInput(
                attrs={"class": "input", "placeholder": _("Ejemplo: 5000 (solo numero)")}),
            "precio": forms.TextInput(attrs={"class": "input", "placeholder": _("Ejemplo: 10.000 por kilogramos")}),
            "name": forms.TextInput(attrs={"class": "input"}),
            "user_id": forms.TextInput(attrs={'readonly': '', "class": "input"}),
            "phone": forms.TextInput(attrs={"class": "input", "type": "tel"}),
            "address": forms.TextInput(attrs={"class": "input"}),
            # 'categories': forms.SelectMultiple(attrs={"style": "display:none;"}),
        }
    def __init__(self, pk, *args, **kwargs):
        print(pk)
        print('#############')
        a = UserAux.objects.get(pk=pk)
        super(UserRegisterEditarComForm, self).__init__(*args, **kwargs)
        self.fields['nombre'].initial = a.nombre
        self.fields['apellido'].initial = a.apellido
        self.fields['email'].initial = a.email
        if a.foto:
            self.fields['bandera_foto'].initial = 'si'
        else:
            self.fields['bandera_foto'].initial = ''
        if a.upload:
            self.fields['bandera_upload'].initial = 'si'
        else:
            self.fields['bandera_upload'].initial = ''

        self.fields['bandera_foto'].widget = HiddenInput()
        self.fields['bandera_upload'].widget = HiddenInput()
        # self.fields['username'].widget = HiddenInput()
        # self.fields['nombre'].widget = HiddenInput()
        # self.fields['apellido'].widget = HiddenInput()
        # self.fields['email'].widget = HiddenInput()