from django.contrib.sitemaps.views import sitemap
from django.conf.urls import include, url
from django.views.generic import TemplateView
from django.views.static import serve
from django.conf.urls.static import static
from django.contrib import admin
from django.conf import settings
from inventory import views

urlpatterns = [
    url(r'^$', views.IndexListView.as_view(), name='home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^profile/', include('userprofile.urls')),
    url(r'^blog/', include('inventory.urls')),
    url(r'about/$', views.About, name='about'),
    url(r'webhistory/$', views.Webhistory, name='webhistory'),
    url(r'^sitemap\.xml$', sitemap, {'sitemaps': {'blog': views.BlogSitemap}},name='django.contrib.sitemaps.views.sitemap')

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += [
        url(r'^media/(?P<path>.*)/$', serve,{'document_root': settings.MEDIA_ROOT,}),
    ]

