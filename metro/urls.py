"""metro URL Configuration
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^login/client/', include('myclient.urls')),
    url(r'^login/object/', include('myobject.urls')),
    url(r'^login/prof/', include('seo.urls')),
    url(r'^login/search/', include('search.urls')),
    url(r'^login/black_list/', include('black_list.urls')),
    url(r'^', include('metro_site.urls')),
    url(r'^zvonok/', include('contactform.urls')),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^photo/', include('photo_baza.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
