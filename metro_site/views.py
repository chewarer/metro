from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.views.generic import View

from myclient.models import Okrug
from myobject.models import MyObject, MultiImages, StancMetro
from photo_baza.models import Photo
from .forms import SearchObjectFront, SearchMetroFront, SearchObjFullFront


def home(request):
    ''' Гланая страница сайта '''
    myobj = MyObject.objects.all().order_by('-id')[:3]
    form = SearchObjFullFront()
    if request.method == "POST":
        order = "station_one"
        form = SearchObjFullFront(request.POST)
        if form.is_valid():
            form_price = form.cleaned_data['price']
            okrug = form.cleaned_data['okrug']
            area = form.cleaned_data['area_range']
            naznach = form.cleaned_data['naznach']
            sort = form.cleaned_data['sort']
            if sort == '1':
                order = "station_one__name"
            elif sort == '2':
                order = "price"
            elif sort == '3':
                order = "station_one"
            elif sort == '4':
                order = "id"

            if form_price == '6' or form_price == "":
                price = 10000000
            elif form_price != "":
                form_price = int(form_price)
                price = (form.fields['price'].choices)[form_price][1]
            if not okrug:
                okrug = Okrug.objects.all()

            if (not area) and (not naznach):
                myobjs = MyObject.objects.filter(
                                price__lte=price,
                                okrug__in=okrug
                                ).order_by(order).distinct()
            elif not area:
                myobjs = MyObject.objects.filter(
                                naznach=form.cleaned_data['naznach'],
                                price__lte=price,
                                okrug__in=okrug
                            ).order_by(order).distinct()
            elif not naznach:
                myobjs = MyObject.objects.filter(
                                area_range=area,
                                price__lte=price,
                                okrug__in=okrug
                            ).order_by(order).distinct()
            else:
                myobjs = MyObject.objects.filter(
                                naznach=form.cleaned_data['naznach'],
                                area_range=area,
                                price__lte=price,
                                okrug__in=okrug
                            ).order_by(order).distinct()
            form = SearchObjFullFront(data=request.POST)
            context = {'mytest': myobjs, 'form': form}
            return render(request, 'site/search.html', context)

    context = {'myobj': myobj, 'form': form}
    return render(request, 'site/home.html', context)


def search_object(request):
    ''' Поиск объекта по номеру '''
    if request.method == "POST":
        form = SearchObjectFront(request.POST)
        if form.is_valid():
            search = form.cleaned_data['search']
            myobject = get_object_or_404(MyObject, id=search)
            photos = MultiImages.objects.filter(parent=myobject)
            try:
                img_obj = MyObject.objects.\
                            filter(okrug=myobject.okrug.all()[:1])
                context = {'obj': myobject, 'photos': photos,
                            'img_objs': img_obj}
            except:
                context = {'obj': myobject, 'photos': photos}
    else:
        return redirect('/')

    return render(request, 'site/obj-single.html', context)


def search_metro(request):
    ''' Поиск станции метро '''
    form = SearchObjFullFront()
    if request.method == "POST":
        form = SearchMetroFront(request.POST)
        if form.is_valid():
            search = form.cleaned_data['search']
            metro = MyObject.objects.\
                filter(Q(station_one__name=search) |
                       Q(station_two__name=search))
            context = {'search_object': metro, 'form': form}
    else:
        return redirect('/')
    return render(request, 'site/search.html', context)


def obj_single(request, pk):
    '''Переход по ссылки на объект'''
    myobject = get_object_or_404(MyObject, pk=pk)
    photos = MultiImages.objects.filter(parent=myobject)
    try:
        img_obj = MyObject.objects.filter(station_one=myobject.station_one)
        context = {'obj': myobject, 'photos': photos, 'img_objs': img_obj}
    except:
        context = {'obj': myobject, 'photos': photos}
    return render(request, 'site/obj-single.html', context)


def new_obj(request):
    '''Новые объекты'''
    myobjs = MyObject.objects.all().order_by("station_one")[:16]
    form = SearchObjFullFront()
    context = {'mytest': myobjs, 'form': form}
    return render(request, 'site/obj.html', context)


def under(request):
    '''Объекты подземки'''
    myobjs = MyObject.objects.filter(typeobj=4).order_by("-station_one")
    form = SearchObjFullFront()
    context = {'mytest': myobjs, 'form': form}
    return render(request, 'site/obj.html', context)
