from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect, get_list_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404
from .forms import MyObjectForm, SObjectTypeForm, \
    SObjectMetroForm, SObjectHideForm, MultiImg
from .models import MyObject, MultiImages
from django.views.generic.edit import UpdateView
from django.views.generic import DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse
from django.utils import timezone
from black_list.models import BlackList
from myclient.forms import SerchNameForm
from django.db.models import Q
import json


@login_required
def upload_photo(request):
    if request.method == "POST" and request.FILES:
        form_img = MultiImg(request.POST, request.FILES)
        print(request.GET)
        # print(request.FILES)
        if form_img.is_valid():
            # print(form_img.cleaned_data.get('title'))
            form_img.instance.my_manager = request.user
            form_img.instance.weight = 1
            photo = form_img.save()
            data = {
                'is_valid': True,
                'name': photo.file.name,
                'url': photo.file.url,
                'pk': photo.id,
                'del_url': 'delete/{}'.format(photo.id)
            }
        else:
            data = {'is_valid': False}
        return JsonResponse(data)


@login_required
def del_photo(request, pk):
    """Удаление фото"""
    print(request.method)
    if request.method == 'GET':
        print(pk)
        x = MultiImages.objects.filter(pk=pk).delete()
        if x[0] != 0:
            return JsonResponse({'status': 'ok'})
        return JsonResponse({'status': 'false'})


@login_required
def save_weight(request):
    """Сохранение веса фото"""
    if request.method == 'GET':
        data = json.loads(request.GET['data'])
        print(data)
        if data:
            for item in data:
                MultiImages.objects.filter(pk=item['id']).update(weight=item['weight'])
            return JsonResponse({'status': 'ok'})


# Добавление объекта
@login_required
def add_object(request):
    error = ""
    photos_list = None
    if request.method == "POST":
        form = MyObjectForm(request.POST)

        if form.is_valid():
            post = form.save(commit=False)
            # Есть ли номер в черном списке
            tel = form.cleaned_data['block_tel']
            if BlackList.objects.filter(tel=tel).exists():
                error = "Номер находится в черном списке"
            else:
                post.my_manager = request.user
                post.save()
                # Задаю родителя для изображений
                MultiImages.objects.filter(parent_id=None, my_manager_id=request.user.id).update(parent_id=post.id)
                return redirect('my_object')
    else:
        form = MyObjectForm()
        # Подчищаю бесхозные файлы (у которых нет родителя и которые принадлежат текущему пользователю)
        # MultiImages.objects.filter(parent_id=None, my_manager=request.user).delete()
        # Отображаю бесхозные файлы, предполагая что они загружены только что текущим пользователем
        photos_list = MultiImages.objects.filter(parent_id=None, my_manager=request.user).order_by('weight').all()

    return render(request, 'myobject/add-object.html', {"form": form, 'error': error, 'photos': photos_list})


@login_required
def my_object(request):
    """Мои объекты"""
    forms = {}
    forms['id'] = SerchNameForm(prefix="id")
    forms['adres'] = SerchNameForm(prefix="adres")
    forms['sobs'] = SerchNameForm(prefix="sobs")
    forms['type'] = SObjectTypeForm()
    forms['metro'] = SObjectMetroForm()
    forms['hide'] = SObjectHideForm()
    search = 3545
    if request.method == "POST":
        # Поиск по полям
        forms_id = SerchNameForm(request.POST, prefix="id")
        forms_adres = SerchNameForm(request.POST, prefix="adres")
        forms_sobs = SerchNameForm(request.POST, prefix="sobs")
        my_object = search_form(forms_id, forms_adres, forms_sobs)
        # Поиск по типу
        form_type = SObjectTypeForm(request.POST)
        if form_type.is_valid():
            search = form_type.cleaned_data['typeobj']
            my_object = MyObject.objects.filter(typeobj=search)
        # Поиск по метро
        form_metro = SObjectMetroForm(request.POST)
        if form_metro.is_valid():
            search = form_metro.cleaned_data['station_one']
            my_object = MyObject.objects\
                .filter(Q(station_one=search) | Q(station_two=search))
        # Скрытые/не скрытые
        form_hide = SObjectHideForm(request.POST)
        if form_hide.is_valid():
            search = form_hide.cleaned_data['hide']
            if search == "no":
                my_object = MyObject.objects\
                    .filter(my_manager_id=request.user.id, hide="0")
            else:
                my_object = MyObject.objects\
                    .filter(my_manager_id=request.user.id)
    else:
        my_object = MyObject.objects.filter(my_manager_id=request.user.id)

    return render(request, 'myobject/my-object.html',
                  {"myobjects": my_object, "forms": forms, 'search': search})


def search_form(id_o, adres, sobs):
    """Обработка поиска по полям"""
    if id_o.is_valid() and id_o.cleaned_data['search'] != '':
        search = id_o.cleaned_data['search']
        query = MyObject.objects.filter(id=search)

    elif adres.is_valid() and adres.cleaned_data['search'] != '':
        search = adres.cleaned_data['search']
        query = MyObject.objects.filter(adres=search)

    elif sobs.is_valid() and sobs.cleaned_data['search'] != '':
        search = sobs.cleaned_data['search']
        query = MyObject.objects\
            .filter(Q(block_name=search) | Q(block_tel=search))
    else:
        query = 0
    return query


@login_required
def hide_obj(request, pk):
    """Скрыть клиента"""
    hide = MyObject.objects.get(id=pk)
    hide.hide_date = "1970-01-01"
    hide.hide = '1'
    hide.save()
    return redirect('my_object')


@login_required
def show_obj(request, pk):
    """Открытия клиента"""
    try:
        hide = MyObject.objects.get(id=pk)
        hide.hide_date = "1970-01-01"
        hide.hide = '0'
        hide.save()
    except ObjectDoesNotExist:
        raise Http404
    return redirect('my_object')


class ObjDelete(LoginRequiredMixin, DeleteView):
    """Удаление объекта"""
    model = MyObject
    template_name = 'myobject/delete-obj.html'

    # редирект на страницу мои объекты
    def get_success_url(self):
        return reverse('my_object')


# Редактирование объекта
class ObjUpdate(LoginRequiredMixin, UpdateView):
    model = MyObject
    form_class = MyObjectForm
    template_name = 'myobject/update-obj.html'

    def get_context_data(self, **kwargs):
        context = super(ObjUpdate, self).get_context_data(**kwargs)
        pk = self.kwargs.get('pk')
        photos_list = MultiImages.objects.filter(parent_id=pk).order_by('weight').all()
        context['photos'] = photos_list
        return context

    def form_valid(self, form, **kwargs):
        self.object = form.save(commit=False)
        self.object.save()
        # print(self.request.user)
        pk = self.kwargs.get('pk')
        MultiImages.objects.filter(parent_id=None, my_manager_id=self.request.user).update(parent_id=pk)
        return redirect('my_object')


class ObjCopy(LoginRequiredMixin, UpdateView):
    """Копирование объекта"""
    model = MyObject
    template_name = "myobject/copy-obj.html"
    form_class = MyObjectForm

    def form_valid(self, form):
        form.instance.my_manager = self.request.user
        # Для копирования устанавливаю pk и id в None
        form.instance.pk = None
        form.instance.id = None
        form.instance.zvon = timezone.now()
        return super(ObjCopy, self).form_valid(form)


@login_required
def zvon_obj(request, pk):
    """Прозвон объекта"""
    zvon = MyObject.objects.get(id=pk)
    zvon.zvon = timezone.now()
    zvon.save()
    return redirect('my_object')

def look_obj(request, pk):
    #Просмотр страницы объекта менеджером
    obj = get_list_or_404(MyObject, pk=pk)
    return render(request, 'site/obj-single.html', {'obj_single': obj})
