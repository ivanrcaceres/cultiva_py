from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.sites import requests
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.serializers import serialize
from django.shortcuts import (
    redirect,
    render,
    get_object_or_404,
)

from conf import settings
from urllib.parse import quote_plus
import json
import datetime
import base64

from .api import StatsSummaryView
from .forms import HelpRequestForm,UserRegisterComprForm, ReservaVerForm, UserRegisterVerForm, UserRegisterEditarComForm, HelpRequestForm2, UserRegisterEditarForm, HelpRequestForm3
from .models import HelpRequest, HelpRequestOwner, FrequentAskedQuestion
from .utils import text_to_image, image_to_base64


def home(request):
    return render(request, "home.html")


def set_owner_and_update_values(request, new_help_request):
    if 'user' in request.ayuda_session and request.ayuda_session['user'] is not None:
        user = request.ayuda_session['user']
        help_request_owner = HelpRequestOwner()
        help_request_owner.help_request = new_help_request
        help_request_owner.user_iid = user
        help_request_owner.save()

        # try to update user values
        if user.name is None:
            user.name = help_request_owner.help_request.name
            user.city = help_request_owner.help_request.city
            user.city_code = help_request_owner.help_request.city_code
            user.phone = help_request_owner.help_request.phone
            user.address = help_request_owner.help_request.address
            user.location = help_request_owner.help_request.location
            user.save()


def request_form(request):
    if request.method == "POST":
        form = HelpRequestForm(request.POST, request.FILES, userr=request.user.id)
        if form.is_valid():
            new_help_request = form.save()
            try:
                set_owner_and_update_values(request, new_help_request)
            except Exception as e:
                # ignore if we can't set the help_request_ownser
                print(str(e))

            messages.success(request, "¡Se creó tu pedido exitosamente!")
            return redirect("pedidos-detail", id=new_help_request.id)
    else:
        usuario = request.user
        print(usuario)
        if usuario.is_anonymous:
            return redirect("/login/")
        else:
            print('else')
            form = HelpRequestForm(userr=request.user.id)



    selected_categories = []
    if form.is_bound:
        for field in form.visible_fields():
            if field.name == 'categories':
                for category in field.subwidgets:
                    if category.data['selected']:
                        selected_categories.append(category.data['value'])
                break

    context = {"form": form, 'selected_categories': selected_categories}

    return render(request, "help_request/create.html", context)

def user_form(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            a = form.save()
            codigo = str(code_generator())
            emails = [form.cleaned_data['email']]
            a.email = emails[0]
            a.codigo = codigo
            a.password = form.cleaned_data['password_form1']
            a.save()
            # enviar el codigo al email del user
            print('mail esta por se enviado 01')
            asunto = 'Confirmacion de email - CULTIVAPY'
            mensaje = 'Codigo de verificacion de Cultivapy: ' + codigo + " - Su User es: " + form.cleaned_data[
                'username'] + " y su pass: " + form.cleaned_data['password_form1'] \
                      + " link de autenticacion: " +settings.URL_BASE+"autenticacion/" + form.cleaned_data[
                          'username'] + "/"+ codigo

            email_remitente = 'ivancaceres17@fpuna.edu.py'
            #
            print('mail esta por se enviado')
            send_mail(asunto, mensaje, email_remitente, emails)
            # redirigir a pantalla de valdiacion

            userUsuario = User()
            userUsuarioAux = UserAux.objects.filter(username = form.cleaned_data['username'])
            userUsuario.username = userUsuarioAux[0].username
            userUsuario.email = userUsuarioAux[0].email
            userUsuario.set_password(userUsuarioAux[0].password)
            userUsuario.is_active = False
            userUsuario.save()

            UserAux.objects.filter(username=form.cleaned_data['username']).update(user=userUsuario)
            # userUsuarioAux[0].user = userUsuario
            # userUsuarioAux[0].save()

            # aaa = User()
            # aaa.username = a[0].username
            # aaa.email = a[0].email
            # aaa.set_password(a[0].password)
            # a = UserAux.objects.filter(username=username2)
            # b = User.objects.filter(username=username2)
            # a[0].user = b[0]
            # print(a[0])
            # a[0].save()



            messages.success(request, "¡Se creó tu pedido exitosamente!")
            return redirect("/")
    else:
        print('else')
        form = UserRegisterForm()

    context = {"form": form}

    return render(request, "help_request/create_user_.html", context)



def user_form_comprador(request):
    if request.method == "POST":
        form = UserRegisterComprForm(request.POST, request.FILES)
        if form.is_valid():
            a = form.save()

            print(a)
            print('a.id')


            codigo = str(code_generator())
            emails = [form.cleaned_data['email']]
            print(codigo)
            print(emails)

            a.email = emails[0]
            a.codigo = codigo
            a.user_id = request.user.id
            a.password = form.cleaned_data['password_form1']
            a.save()

            # enviar el codigo al email del user
            print('mail esta por se enviado 01')
            asunto = 'Confirmacion de email - CULTIVAPY'
            mensaje = 'Codigo de verificacion Cultivapy : ' + codigo + " - Su User es: " + form.cleaned_data[
                'username'] + " y su pass: " + form.cleaned_data['password_form1'] + " link de autenticacion: " +settings.URL_BASE+"autenticacion_comprador/" + form.cleaned_data[
                          'username'] + "/"+ codigo
            email_remitente = 'ivancaceres17@fpuna.edu.py'
            #
            print('mail esta por se enviado')
            send_mail(asunto, mensaje, email_remitente, emails)
            # redirigir a pantalla de valdiacion


            messages.success(request, "¡Se creó tu pedido exitosamente!")
            return redirect("/")
    else:
        print('else')
        form = UserRegisterComprForm()

    context = {"form": form}

    return render(request, "help_request/create_user_.html", context)


def view_request(request, id):
    help_request = get_object_or_404(HelpRequest, pk=id)
    active_requests = []
    if not help_request.active:
        active_requests = HelpRequest.objects.filter(phone=help_request.phone, active=True).order_by('-pk')
    vote_ctrl = {}
    vote_ctrl_cookie_key = 'votectrl'
    # cookie expiration
    dt = datetime.datetime(year=2067, month=12, day=31)
    lista_reserva = Reserva.objects.filter(publicacion=help_request.id)
    lista_query = list(lista_reserva.values())

    context = {
        "help_request": help_request,
        "name": help_request.name,
        "fecha": help_request.fecha,
        "thumbnail": help_request.thumb if help_request.picture else "/static/img/logo.jpg",
        "phone_number_img": image_to_base64(text_to_image(help_request.phone, 300, 50)),
        "whatsapp": '595'+help_request.phone[1:]+'?text=Hola+'+help_request.name
                    + ',+te+escribo+por+el+pedido+que+hiciste:+'+quote_plus(help_request.title)
                    + '+https:'+'/'+'/'+'ayudapy.org/pedidos/'+help_request.id.__str__(),
        "active_requests": active_requests,
        "lista_reserva": lista_query,
    }
    if request.POST:
        if request.POST['vote']:
            if vote_ctrl_cookie_key in request.COOKIES:
                try:
                    vote_ctrl = json.loads(base64.b64decode(request.COOKIES[vote_ctrl_cookie_key]))
                except:
                    pass

                try:
                    voteFlag = vote_ctrl["{id}".format(id=help_request.id)]
                except KeyError:
                    voteFlag = None

                if voteFlag is None:
                    if request.POST['vote'] == 'up':
                        help_request.upvotes += 1
                    elif request.POST['vote'] == 'down':
                        help_request.downvotes += 1
                    help_request.save()
                    vote_ctrl["{id}".format(id=help_request.id)] = True

    response = render(request, "help_request/details.html", context)

    if vote_ctrl_cookie_key not in request.COOKIES:
        # initialize control cookie
        if request.POST and request.POST['vote']:
            # set value in POST request if cookie not exists
            b = json.dumps({"{id}".format(id=help_request.id): True}).encode('utf-8')
        else:
            # set empty value in others requests
            b = json.dumps({}).encode('utf-8')
        value = base64.b64encode(b).decode('utf-8')
        response.set_cookie(vote_ctrl_cookie_key, value,
                            expires=dt)
    else:
        if request.POST:
            if request.POST['vote']:
                # update control cookie only in POST request
                b = json.dumps(vote_ctrl).encode('utf-8')
                value = base64.b64encode(b).decode('utf-8')
                response.set_cookie(vote_ctrl_cookie_key, value,
                                    expires=dt)
    return response


def view_request_comprador(request, id):
    help_request = get_object_or_404(HelpRequest, pk=id)
    active_requests = []
    if not help_request.active:
        active_requests = HelpRequest.objects.filter(phone=help_request.phone, active=True).order_by('-pk')
    vote_ctrl = {}
    vote_ctrl_cookie_key = 'votectrl'
    # cookie expiration
    dt = datetime.datetime(year=2067, month=12, day=31)

    ##datos prueba
    lista_p = [1,2,3,4]
    lista_reserva = Reserva.objects.filter(publicacion = help_request.id)
    mi_lista_reserva = Reserva.objects.filter(publicacion = help_request.id, user=request.user.id)
    print('mi lista reserva')
    print(mi_lista_reserva)
    print('lista reserva')
    print(lista_reserva)
    print(list(lista_reserva.values()))
    lista_query = list(lista_reserva.values())
    mi_lista_query = list(mi_lista_reserva.values())

    context = {
        "help_request": help_request,
        "name": help_request.name,
        "fecha": help_request.fecha,
        "thumbnail": help_request.thumb if help_request.picture else "/static/img/logo.jpg",
        "phone_number_img": image_to_base64(text_to_image(help_request.phone, 300, 50)),
        "whatsapp": '595'+help_request.phone[1:]+'?text=Hola+'+help_request.name
                    + ',+te+escribo+por+el+pedido+que+hiciste:+'+quote_plus(help_request.title)
                    + '+https:'+'/'+'/'+'ayudapy.org/pedidos/'+help_request.id.__str__(),
        "active_requests": active_requests,
        "lista_p01":lista_p,
        "lista_reserva":lista_query,
        "mi_lista_reserva": mi_lista_query,
    }
    if request.POST:
        if request.POST['vote']:
            if vote_ctrl_cookie_key in request.COOKIES:
                try:
                    vote_ctrl = json.loads(base64.b64decode(request.COOKIES[vote_ctrl_cookie_key]))
                except:
                    pass

                try:
                    voteFlag = vote_ctrl["{id}".format(id=help_request.id)]
                except KeyError:
                    voteFlag = None

                if voteFlag is None:
                    if request.POST['vote'] == 'up':
                        help_request.upvotes += 1
                    elif request.POST['vote'] == 'down':
                        help_request.downvotes += 1
                    help_request.save()
                    vote_ctrl["{id}".format(id=help_request.id)] = True

    response = render(request, "help_request/detailscomprador.html", context)

    if vote_ctrl_cookie_key not in request.COOKIES:
        # initialize control cookie
        if request.POST and request.POST['vote']:
            # set value in POST request if cookie not exists
            b = json.dumps({"{id}".format(id=help_request.id): True}).encode('utf-8')
        else:
            # set empty value in others requests
            b = json.dumps({}).encode('utf-8')
        value = base64.b64encode(b).decode('utf-8')
        response.set_cookie(vote_ctrl_cookie_key, value,
                            expires=dt)
    else:
        if request.POST:
            if request.POST['vote']:
                # update control cookie only in POST request
                b = json.dumps(vote_ctrl).encode('utf-8')
                value = base64.b64encode(b).decode('utf-8')
                response.set_cookie(vote_ctrl_cookie_key, value,
                                    expires=dt)
    return response


def view_faq(request):
    """ Frequent Asked Questions controller """
    try:
        faq_list = FrequentAskedQuestion.objects.filter(active=True)
    except:
        # no exception should break the flow.
        faq_list = []

    context = {
        'faq_list': faq_list
    }

    template = "footer/general_faq.html"

    return render(request, template, context)


def list_requests(request):
    cities = [(i['city'], i['city_code']) for i in HelpRequest.objects.filter(active=True, resolved=False).values(
        'city', 'city_code').distinct('city_code').order_by('city_code')]
    context = {"list_cities": cities}
    print(context)
    return render(request, "help_request/list.html", context)


def list_by_city(request, city):
    list_help_requests = HelpRequest.objects.filter(city_code=city, active=True, resolved=False).order_by("-added")  # TODO limit this
    city = list_help_requests[0].city

    page = request.GET.get('page', 1)
    paginate_by = 25
    paginator = Paginator(list_help_requests, paginate_by)
    try:
        list_paginated = paginator.page(page)
    except PageNotAnInteger:
        list_paginated = paginator.page(1)
    except EmptyPage:
        list_paginated = paginator.page(paginator.num_pages)

    context = {"list_help": list_help_requests, "city": city, "list_paginated": list_paginated}
    return render(request, "help_request/list_by_city.html", context)

@login_required
def stats(request):
    datos = StatsSummaryView(request)
    context = {"datos": json.loads(datos.content)}
    return render(request, "stats/dashboard.html", context)


'''
codigo para cultiva
'''
from django.urls import reverse_lazy, reverse
from django.views.generic.edit import (
    FormView
)
from django.views import generic
from .forms import (
    LoginForm,
)
from django.contrib.auth import authenticate, login, logout

class LoginUser(FormView):
    template_name = 'users/login_comprador.html'
    form_class = LoginForm
    success_url = '/'

    def form_valid(self, form):
        user = authenticate(
            username=form.cleaned_data['user'],
            password=form.cleaned_data['password']
        )
        login(self.request, user)
        return super(LoginUser, self).form_valid(form)

class LoginUserComprador(FormView):
    template_name = 'users/login_comprador2.html'
    form_class = LoginForm
    success_url = '/'

    def form_valid(self, form):
        user = authenticate(
            username=form.cleaned_data['user'],
            password=form.cleaned_data['password']
        )
        login(self.request, user)
        return super(LoginUserComprador, self).form_valid(form)


class requestsListView(generic.ListView):
    model = HelpRequest
    context_object_name = 'my_HelpRequest_list'   # your own name for the list as a template variable
    #queryset = HelpRequest.objects.filter(user_id=requests.user) # Get 5 books containing the title war
    template_name = 'help_request/list2.html'  # Specify you


    def get_queryset(self, *args, **kwargs):

        if self.request.user.is_anonymous:
            return None
        else:
            return HelpRequest.objects.filter(user_id=self.request.user,active=True, resolved=False)

from django.views.generic.edit import (
    FormView,
)

from django.views.generic import (
    DetailView,
    DeleteView,
    UpdateView,
)

from .forms import UserRegisterForm,UserRegisterForm2,UserRegisterForm3, VerificationForm, PassOlvidadaForm, PerfilForm,ReservaForm, ReservaForm2
from .functions import *
from .models import UserAux, Reserva, UserDatosExtras
from django.http import HttpResponseRedirect
from django.core.mail import send_mail
from .functions import *

class UserRegisterView(FormView):
    template_name = 'users/register.html'
    form_class = UserRegisterForm
    success_url = '/user-verification/'

    def form_valid(self, form):
        # generamos el codigo

        #
        # usuario = UserAux()

        # usuario.crearUserAux(
        #     form.cleaned_data['username'],
        #     form.cleaned_data['email'],
        #     form.cleaned_data['password1'],
        #     form.cleaned_data['foto'],
        #     form.cleaned_data['upload'],
        #     form.cleaned_data['nombre'],
        #     form.cleaned_data['apellido'],
        # )
        codigo = str(code_generator())
        emails = [form.cleaned_data['email']]

        usuario2 = UserAux()
        usuario2.username=form.cleaned_data['username']
        usuario2.email=form.cleaned_data['email']
        usuario2.password=form.cleaned_data['password1']
        usuario2.foto=form.cleaned_data['foto']
        usuario2.upload=form.cleaned_data['upload']
        usuario2.nombre=form.cleaned_data['nombre']
        usuario2.apellido=form.cleaned_data['apellido']
        usuario2.codigo = codigo
        usuario2.save()

        # enviar el codigo al email del user
        print('mail esta por se enviado 01')
        asunto = 'Confirmacion de email'
        mensaje = 'Codigo de verificacion: ' + codigo + " - Su User es: " + form.cleaned_data['username'] + "y su pass: " + form.cleaned_data['password1']
        email_remitente = 'ivancaceres17@fpuna.edu.py'
        #
        print('mail esta por se enviado')
        send_mail(asunto, mensaje, email_remitente, emails)
        # redirigir a pantalla de valdiacion


        return HttpResponseRedirect('/user-verification/')


class CodeVerificationView(FormView):
    template_name = 'users/verification.html'
    form_class = VerificationForm
    success_url = '/login/'

class PassOlvidadaView(FormView):
    template_name = 'help_request/recuperar_contra_user.html'
    form_class = PassOlvidadaForm
    success_url = '/login/'

class PerfilView(FormView):
    template_name = 'users/perfil.html'
    form_class = PerfilForm
    success_url = '/login/'


from django.contrib.auth.models import User
class PerfilUserDetalleView(DetailView):
    template_name = 'users/user_perfil.html'
    model = UserAux
    # def get_context_data(self, **kwargs):
    #     context = super(PerfilUserDetalleView,self).get_context_data(**kwargs)
    #     print(self.kwargs['pk'])
    #     a = UserAux.objects.get(pk=self.kwargs['pk'])
    #     # b = UserDatosExtras.objects.filter(user_id=self.kwargs['pk'])
    #     # print(b[0].id)
    #     # context['user_id'] = a.id
    #     # print('context[user_id] = a.user.id')
    #     print(context)
    #     return context
    #
    def get_queryset(self):
        a = UserAux.objects.filter(user=self.kwargs['pk'])
        # a = UserAux.objects.filter(user=1)
        return a


class PerfilUserCompradorDetalleView(DetailView):
    template_name = 'users/user_perfil_comprador.html'
    model = UserAux

    def get_queryset(self):
        a = UserAux.objects.filter(user=self.kwargs['pk'])
        # a = UserAux.objects.filter(user=1)
        return a





from django.views.generic import (
    View
)
class LogoutView(View):
    def get(self, request, *args, **kargs):
        logout(request)
        print('hola desde LogoutView')
        return HttpResponseRedirect(
                '/'
        )


class EliPubliDeleteView(DeleteView):
    model = HelpRequest
    template_name = 'help_request/eliminarpub.html'
    # success_url = '/pedidos_mios'

    def get_success_url(self):
        return '/pedidos_mios'


class ActuaPubliUpdateView(UpdateView):
    model = HelpRequest
    form_class = HelpRequestForm2
    template_name = 'help_request/updatepub.html'

    success_url = '/pedidos_mios'

    def get_context_data(self, *args, **kwargs):
        context = super(ActuaPubliUpdateView, self).get_context_data(**kwargs)
        #context['something'] = Book.objects.filter(pk=self.kwargs.get('pk'))
        # print(self.kwargs['pk'])
        # print(HelpRequest.objects.get(pk=self.kwargs['pk']))

        # HelpRequest.objects.get(pk=self.kwargs['pk']).delete()


        return context

class ActuaPubliUpdateView(UpdateView):
    model = HelpRequest
    form_class = HelpRequestForm3
    template_name = 'help_request/updatepub.html'

    success_url = '/pedidos_mios'

    def get_context_data(self, *args, **kwargs):
        context = super(ActuaPubliUpdateView, self).get_context_data(**kwargs)
        # context['something'] = Book.objects.filter(pk=self.kwargs.get('pk'))
        print(self.kwargs['pk'])
        print(HelpRequest.objects.get(pk=self.kwargs['pk']))

        # HelpRequest.objects.get(pk=self.kwargs['pk']).delete()

        return context

    def get_form_kwargs(self):
        kwargs = super(ActuaPubliUpdateView, self).get_form_kwargs()
        kwargs.update({
            'pk': self.kwargs['pk'],
        })
        print(self.kwargs['pk'])
        return kwargs

class ActuaUserUpdateView(UpdateView):
    model = UserAux
    form_class = UserRegisterForm2
    template_name = 'help_request/create_user_2.html'
    success_url = '/..'

    def get_context_data(self, *args, **kwargs):
        context = super(ActuaUserUpdateView, self).get_context_data(**kwargs)
        # foto = UserAux.objects.filter(pk=self.kwargs.get('pk'))
        # context['foto'] = foto[0].foto
        # context['archivo'] = foto[0].upload
        # context['archivo'] = foto[0].upload
        # print(self.kwargs['pk'])
        # print(UserAux.objects.get(pk=self.kwargs['pk']))
        return context

    # def get_queryset(self, *args, **kwargs):
    #     return UserAux()

class ActuaUserUpdateView2(UpdateView):
    model = UserAux
    form_class = UserRegisterForm3
    template_name = 'help_request/create_user_3.html'
    success_url = '/..'

    def get_context_data(self, *args, **kwargs):
        context = super(ActuaUserUpdateView2, self).get_context_data(**kwargs)
        # context['something'] = Book.objects.filter(pk=self.kwargs.get('pk'))
        print(self.kwargs['pk'])
        print(UserAux.objects.get(pk=self.kwargs['pk']))
        return context



from django.views.generic import CreateView, TemplateView
from django.urls import reverse
class ReservaCreateView(CreateView):
    model = Reserva
    form_class = ReservaForm
    template_name = 'help_request/create_reserva_comprador.html'


    def get_success_url(self):
        pk = self.kwargs["pk"]
        return '/pedidos_comprador/'+pk



    # def get_context_data(self, *args, **kwargs):
    #     context = super(ReservaCreateView, self).get_context_data(**kwargs)
    #     #context['something'] = Book.objects.filter(pk=self.kwargs.get('pk'))
    #     print(self.kwargs['pk'])
    #     print(HelpRequest.objects.get(pk=self.kwargs['pk']))

    def get_form_kwargs(self):
        kwargs = super(ReservaCreateView, self).get_form_kwargs()

        kwargs.update({
            'pk': self.kwargs['pk'],
            'user_id':self.kwargs['user_id'],
        })
        return kwargs

class ActuaReserUpdateView(UpdateView):
    model = Reserva
    form_class = ReservaForm2
    # template_name = 'help_request/updatepub2.html'
    template_name = 'help_request/edit_reserva_comprador.html'

    def get_success_url(self):
        pk = self.kwargs["pk"]
        aux = Reserva.objects.get(pk=pk)
        print(aux.publicacion.id)
        return '/pedidos_comprador/' + str(aux.publicacion.id)

    def get_context_data(self, *args, **kwargs):
        context = super(ActuaReserUpdateView, self).get_context_data(**kwargs)
        #context['something'] = Book.objects.filter(pk=self.kwargs.get('pk'))
        # print(self.kwargs['pk'])
        # print(HelpRequest.objects.get(pk=self.kwargs['pk']))

        # HelpRequest.objects.get(pk=self.kwargs['pk']).delete()

        context['pkpk'] = self.kwargs['pk']
        return context

class ActuaReserVerView(UpdateView):
    model = Reserva
    form_class = ReservaVerForm
    # template_name = 'help_request/updatepub2.html'
    template_name = 'help_request/ver_reserva_comprador.html'

    def get_success_url(self):
        pk = self.kwargs["pk"]
        aux = Reserva.objects.get(pk=pk)
        print(aux.publicacion.id)
        return '/pedidos_comprador/' + str(aux.publicacion.id)

    def get_context_data(self, *args, **kwargs):
        context = super(ActuaReserVerView, self).get_context_data(**kwargs)
        #context['something'] = Book.objects.filter(pk=self.kwargs.get('pk'))
        # print(self.kwargs['pk'])
        # print(HelpRequest.objects.get(pk=self.kwargs['pk']))

        # HelpRequest.objects.get(pk=self.kwargs['pk']).delete()


        return context


class EliReserDeleteView(DeleteView):
    model = Reserva
    template_name = 'help_request/eliminarreserva.html'
    # success_url = '/'

    def get_success_url(self):
        pk = self.kwargs["pk"]
        aux = Reserva.objects.get(pk=pk)
        print(aux.publicacion.id)
        return '/pedidos_comprador/'+str(aux.publicacion.id)

class ReservaDetalleView(DetailView):
    template_name = 'help_request/reserva_detalle.html'
    model = Reserva

class EliReserProdDeleteView(DeleteView):
    model = Reserva
    template_name = 'help_request/eliminarreservapro.html'
    # success_url = '/'

    def get_success_url(self):
        pk = self.kwargs["pk"]
        aux = Reserva.objects.get(pk=pk)
        print(aux.publicacion.id)
        return '/pedidos/'+str(aux.publicacion.id)


class ReservaListView(generic.ListView):
    model = Reserva
    context_object_name = 'my_reserva_list'   # your own name for the list as a template variable
    #queryset = HelpRequest.objects.filter(user_id=requests.user) # Get 5 books containing the title war
    template_name = 'help_request/list_reserva.html'  # Specify you


    def get_queryset(self, *args, **kwargs):

        if self.request.user.is_anonymous:
            return None
        else:
            print(Reserva.objects.filter(user=self.request.user))
            return Reserva.objects.filter(user=self.request.user)

class UserRegisterEditarView(FormView):
    template_name = 'help_request/edit_user_productor.html'
    form_class = UserRegisterEditarForm
    success_url = '/'

    def form_valid(self, form):
        print('holaaa lola')
        uaux = UserAux.objects.get(pk=self.kwargs['pk'])
        print(uaux)
        uaux.nombre = form.cleaned_data['nombre']
        uaux.apellido = form.cleaned_data['apellido']
        uaux.email = form.cleaned_data['email']
        if form.cleaned_data['foto']:
            uaux.foto = form.cleaned_data['foto']
        if form.cleaned_data['upload']:
            uaux.upload = form.cleaned_data['upload']
        uaux.save()

        return HttpResponseRedirect('../user-ver-pro/'+self.kwargs['pk'])

    def get_form_kwargs(self):
        kwargs = super(UserRegisterEditarView, self).get_form_kwargs()

        kwargs.update({
            'pk': self.kwargs['pk'],
        })
        return kwargs

    def get_context_data(self, *args, **kwargs):
        context = super(UserRegisterEditarView, self).get_context_data(**kwargs)
        print(self.kwargs['pk'])
        print(UserAux.objects.get(pk=self.kwargs['pk']))
        uaux = UserAux.objects.get(pk=self.kwargs['pk'])
        foto_url = str(uaux.foto)
        print(uaux.foto)
        doc_url = str(uaux.upload)
        print(uaux.upload)
        print(foto_url)
        print(doc_url)
        context['foto_url'] = foto_url
        context['doc_url'] = doc_url
        context['nombre_user_aux'] = uaux.nombre
        context['apellido_user_aux'] = uaux.apellido
        context['email_user_aux'] = uaux.email
        context['pkpk'] = self.kwargs['pk']
        return context



class UserRegisterVerView(FormView):
    template_name = 'help_request/edit_user_productor_vista.html'
    form_class = UserRegisterVerForm
    success_url = '/'

    def form_valid(self, form):
        print('holaaa lola')
        uaux = UserAux.objects.get(pk=self.kwargs['pk'])
        print(uaux)
        uaux.nombre = form.cleaned_data['nombre']
        uaux.apellido = form.cleaned_data['apellido']
        uaux.email = form.cleaned_data['email']
        if form.cleaned_data['foto']:
            uaux.foto = form.cleaned_data['foto']
        if form.cleaned_data['upload']:
            uaux.upload = form.cleaned_data['upload']
        uaux.save()

        return HttpResponseRedirect('../perfil-user-detalle/'+self.kwargs['pk'])

    def get_form_kwargs(self):
        kwargs = super(UserRegisterVerView, self).get_form_kwargs()

        kwargs.update({
            'pk': self.kwargs['pk'],
        })
        return kwargs

    def get_context_data(self, *args, **kwargs):
        context = super(UserRegisterVerView, self).get_context_data(**kwargs)
        print(self.kwargs['pk'])
        print(UserAux.objects.get(pk=self.kwargs['pk']))
        uaux = UserAux.objects.get(pk=self.kwargs['pk'])
        foto_url = str(uaux.foto)
        print(uaux.foto)
        doc_url = str(uaux.upload)
        print(uaux.upload)
        print(foto_url)
        print(doc_url)
        context['foto_url'] = foto_url
        context['doc_url'] = doc_url
        context['nombre_user_aux'] = uaux.nombre
        context['apellido_user_aux'] = uaux.apellido
        context['email_user_aux'] = uaux.email
        context['pkpk'] = self.kwargs['pk']
        return context


class UserRegisterVerComView(FormView):
    template_name = 'help_request/edit_user_comprador_vista.html'
    form_class = UserRegisterVerForm
    success_url = '/'

    def form_valid(self, form):
        print('holaaa lola')
        uaux = UserAux.objects.get(pk=self.kwargs['pk'])
        print(uaux)
        uaux.nombre = form.cleaned_data['nombre']
        uaux.apellido = form.cleaned_data['apellido']
        uaux.email = form.cleaned_data['email']
        if form.cleaned_data['foto']:
            uaux.foto = form.cleaned_data['foto']
        if form.cleaned_data['upload']:
            uaux.upload = form.cleaned_data['upload']
        uaux.save()

        return HttpResponseRedirect('../perfil-user-detalle/'+self.kwargs['pk'])

    def get_form_kwargs(self):
        kwargs = super(UserRegisterVerComView, self).get_form_kwargs()

        kwargs.update({
            'pk': self.kwargs['pk'],
        })
        return kwargs

    def get_context_data(self, *args, **kwargs):
        context = super(UserRegisterVerComView, self).get_context_data(**kwargs)
        print(self.kwargs['pk'])
        print(UserAux.objects.get(pk=self.kwargs['pk']))
        uaux = UserAux.objects.get(pk=self.kwargs['pk'])
        foto_url = str(uaux.foto)
        print(uaux.foto)
        doc_url = str(uaux.upload)
        print(uaux.upload)
        print(foto_url)
        print(doc_url)
        context['foto_url'] = foto_url
        context['doc_url'] = doc_url
        context['nombre_user_aux'] = uaux.nombre
        context['apellido_user_aux'] = uaux.apellido
        context['email_user_aux'] = uaux.email
        context['pkpk'] = self.kwargs['pk']
        return context

# editar publicacion con botones funcional

class PublRegisterEditarView(FormView):
    template_name = 'help_request/updatepub3.html'
    form_class = HelpRequestForm3
    success_url = '/'

    def form_valid(self, form):
        print('holaaa lola')
        uaux = HelpRequest.objects.get(pk=self.kwargs['pk'])
        uaux.title = form.cleaned_data['title']
        uaux.name = form.cleaned_data['name']
        uaux.cant_disponible = form.cleaned_data['cant_disponible']
        uaux.unidad_medida = form.cleaned_data['unidad_medida']
        uaux.precio = form.cleaned_data['precio']
        uaux.fecha = form.cleaned_data['fecha']
        uaux.delivery = form.cleaned_data['delivery']
        uaux.buscar = form.cleaned_data['buscar']
        uaux.name2 = form.cleaned_data['name2']
        uaux.phone = form.cleaned_data['phone']
        uaux.location = form.cleaned_data['location']
        uaux.address = form.cleaned_data['address']
        # uaux.picture = form.cleaned_data['picture']
        uaux.user_id = form.cleaned_data['user_id']

        if form.cleaned_data['picture']:
            uaux.picture = form.cleaned_data['picture']
        uaux.save()

        return HttpResponseRedirect('/')

    def get_form_kwargs(self):
        kwargs = super(PublRegisterEditarView, self).get_form_kwargs()
        kwargs.update({
            'pk': self.kwargs['pk'],
        })
        print(self.kwargs['pk'])
        return kwargs

    def get_context_data(self, *args, **kwargs):
        context = super(PublRegisterEditarView, self).get_context_data(**kwargs)

        uaux = HelpRequest.objects.get(pk=self.kwargs['pk'])
        foto_url = str(uaux.picture)
        # print(uaux.foto)
        # doc_url = str(uaux.upload)
        # print(uaux.upload)
        # print(foto_url)
        # print(doc_url)
        context['foto_url'] = foto_url
        # context['doc_url'] = doc_url
        # context['nombre_user_aux'] = uaux.nombre
        # context['apellido_user_aux'] = uaux.apellido
        # context['email_user_aux'] = uaux.email
        # context['pkpk'] = self.kwargs['pk']
        return context

class UserRegisterEditarComView(FormView):
    template_name = 'help_request/edit_user_comprador.html'
    form_class = UserRegisterEditarComForm
    success_url = '/'

    def form_valid(self, form):
        print('holaaa lola')
        uaux = UserAux.objects.get(pk=self.kwargs['pk'])
        print(uaux)
        uaux.nombre = form.cleaned_data['nombre']
        uaux.apellido = form.cleaned_data['apellido']
        uaux.email = form.cleaned_data['email']
        # if form.cleaned_data['foto']:
        #     uaux.foto = form.cleaned_data['foto']
        # if form.cleaned_data['upload']:
        #     uaux.upload = form.cleaned_data['upload']
        uaux.save()

        return HttpResponseRedirect('../user-ver-com/'+self.kwargs["pk"])

    def get_form_kwargs(self):
        kwargs = super(UserRegisterEditarComView, self).get_form_kwargs()

        kwargs.update({
            'pk': self.kwargs['pk'],
        })
        return kwargs

    def get_context_data(self, *args, **kwargs):
        context = super(UserRegisterEditarComView, self).get_context_data(**kwargs)
        # print(self.kwargs['pk'])
        # print(UserAux.objects.get(pk=self.kwargs['pk']))
        # uaux = UserAux.objects.get(pk=self.kwargs['pk'])
        # foto_url = str(uaux.foto)
        # print(uaux.foto)
        # doc_url = str(uaux.upload)
        # print(uaux.upload)
        # print(foto_url)
        # print(doc_url)
        # context['foto_url'] = foto_url
        # context['doc_url'] = doc_url
        # context['nombre_user_aux'] = uaux.nombre
        # context['apellido_user_aux'] = uaux.apellido
        # context['email_user_aux'] = uaux.email
        context['pkpk'] = self.kwargs['pk']
        return context

class AcutenticacionLink(View):

    def get(self, request, *args, **kargs):
        print(self.kwargs['user'])
        print(self.kwargs['pass'])

        codigo = self.kwargs['pass']
        username2 = self.kwargs['user']
        idDeUser = 0
        a = UserAux.objects.filter(username=username2)
        if len(codigo) == 6:
            print(a[0].codigo)
            print(a[0].id)
            print('uuu')
            if (a[0].codigo == codigo):
                aaa = User.objects.filter(username=username2).update(is_active=True)
            else:
                # raise forms.ValidationError('el codigo es incorrecto')
                messages.success(request, "¡el codigo es incorrecto!")
        else:
            messages.success(request, "¡el codigo es incorrecto!")
        return HttpResponseRedirect('/login2')

class AcutenticacionCompradorLink(View):

    def get(self, request, *args, **kargs):
        print(self.kwargs['user'])
        print(self.kwargs['pass'])

        codigo = self.kwargs['pass']
        username2 = self.kwargs['user']
        idDeUser = 0
        a = UserAux.objects.filter(username=username2)
        if len(codigo) == 6:
            print(a[0].codigo)
            print(a[0].id)
            print('uuu')
            if (a[0].codigo == codigo):
                aaa = User.objects.filter(username=username2).update(is_active=True)
            else:
                # raise forms.ValidationError('el codigo es incorrecto')
                messages.success(request, "¡el codigo es incorrecto!")
        else:
            messages.success(request, "¡el codigo es incorrecto!")
        return HttpResponseRedirect('/login3')

class inicio2(TemplateView):
    template_name = "users/login2.html"

class inicio3(TemplateView):
    template_name = "users/login3.html"


