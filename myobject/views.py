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
        # print(request.GET)
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
    if request.method == 'GET':
        response_ok = JsonResponse({'status': 'ok'})
        object_id = request.GET.get('object_id')
        photo_id = pk

        if object_id:
            # Удаляю фото из объекта, если объект известен
            obj = MyObject.objects.get(pk=object_id).photos.all()
            photo = obj.filter(pk=photo_id).first()
            if photo:
                # Если фото имеет привязку к объекту (не загружено только что, без сохранения объекта)
                if photo.myobject_set.count() == 1:
                    # Если фото не связано с другим объектом
                    photo.delete()
                    return response_ok
                else:
                    # Если фото связано и с другими объектами тоже
                    obj = MyObject.objects.filter(pk=object_id).first()
                    photo = MultiImages.objects.filter(pk=photo_id).first()
                    obj.photos.remove(photo)
                    return response_ok
            else:
                # Если фото загружно, но еще не привязано к текущему объекту
                x = MultiImages.objects.filter(pk=photo_id).delete()
                if x[0] != 0:
                    return response_ok

        else:
            # Если объект не известен
            if MultiImages.objects.filter(pk=photo_id).first().myobject_set.count() == 0:
                # Если фото не имеет связей
                x = MultiImages.objects.filter(pk=photo_id).delete()
                if x[0] != 0:
                    return response_ok

        return JsonResponse({'status': 'false'})


@login_required
def save_weight(request):
    """Сохранение веса фото"""
    if request.method == 'GET':
        data = json.loads(request.GET['data'])
        # print(data)
        if data:
            for item in data:
                MultiImages.objects.filter(pk=item['id']).update(weight=item['weight'])
            return JsonResponse({'status': 'ok'})


# Добавление объекта
@login_required
def add_object(request):
    error = ""
    photo_list = None
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
                # Задаю родителя для изображений
                photo_list = MultiImages.objects.filter(myobject__photos=None, my_manager_id=request.user.id)\
                    .values_list('id', flat=True)
                post.save()
                post.photos.add(*list(photo_list))
                post.save()
                form.save_m2m()
                return redirect('my_object')
    else:
        form = MyObjectForm()
        # Подчищаю бесхозные файлы (у которых нет родителя и которые принадлежат текущему пользователю)
        # MultiImages.objects.filter(parent_id=None, my_manager=request.user).delete()
        # Отображаю бесхозные файлы, предполагая что они загружены только что, текущим пользователем
        photo_list = MultiImages.objects.filter(myobject__photos=None, my_manager=request.user).order_by('weight').all()

    return render(request, 'myobject/add-object.html', {"form": form, 'error': error, 'photos': photo_list})


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
        # pk = self.kwargs.get('pk')
        photo_list = self.object.photos.all().order_by('weight')
        context['photos'] = photo_list
        return context

    def form_valid(self, form, **kwargs):
        self.object = form.save(commit=False)
        # self.object.save()
        form.save_m2m()
        # pk = self.kwargs.get('pk')
        photo_list = MultiImages.objects.filter(myobject__photos=None, my_manager_id=self.request.user.id) \
            .values_list('id', flat=True)
        self.object.photos.add(*list(photo_list))
        self.object.save()
        return redirect('my_object')


class ObjCopy(LoginRequiredMixin, UpdateView):
    """Копирование объекта"""
    model = MyObject
    template_name = "myobject/copy-obj.html"
    form_class = MyObjectForm

    def get_context_data(self, **kwargs):
        context = super(ObjCopy, self).get_context_data(**kwargs)
        photo_list = self.object.photos.all().order_by('weight')
        context['photos'] = photo_list
        return context

    def form_valid(self, form):
        form.instance.my_manager = self.request.user
        # Для копирования устанавливаю pk и id в None
        pk = form.instance.pk
        form.instance.pk = None
        form.instance.id = None
        form.instance.zvon = timezone.now()
        self.object = form.save(commit=False)
        self.object.save()
        form.save_m2m()
        # Связываю фото с новым объектом
        imgs = MultiImages.objects.filter(myobject__photos=None, my_manager_id=self.request.user.id)\
            .values_list('id', flat=True).distinct()
        imgs2 = MultiImages.objects.filter(myobject__photos__myobject=pk).values_list('id', flat=True).distinct()
        self.object.photos.add(*list(imgs | imgs2))
        self.object.save()
        return super(ObjCopy, self).form_valid(form)


@login_required
def zvon_obj(request, pk):
    """Прозвон объекта"""
    zvon = MyObject.objects.get(id=pk)
    zvon.zvon = timezone.now()
    zvon.save()
    return redirect('my_object')


def look_obj(request, pk):
    # Просмотр страницы объекта менеджером
    obj = get_list_or_404(MyObject, pk=pk)
    return render(request, 'site/obj-single.html', {'obj_single': obj})
