from social.backends.google import GooglePlusAuth
from django.conf.urls import url
from django.views.static import serve
from django.conf.urls.static import static
from django.conf import settings
from inventory import views


context = dict(
    plus_id=getattr(settings, 'SOCIAL_AUTH_GOOGLE_PLUS_KEY', None),
    plus_scope=' '.join(GooglePlusAuth.DEFAULT_SCOPE),
)


urlpatterns = [
    # url以blog/开头
    url(r'^(?P<pk>(\d+))/$',views.BlogDetailView.as_view() , name='item_detail'),
    url(r'^publish/$', views.BlogPublishView.as_view(), name='item_publish'),
    url(r'^search/$', views.BlogSearchView.as_view(), name='item_search'),
    url(r'^(?P<tag>([a-zA-Z\-&]+))/$',views.CategoriesListView.as_view() , name='item_categories'),
    url(r'^(?P<id>(\d+))/edit/$', views.BlogEditView.as_view(), name='item_edit'),
    url(r'^(?P<id>(\d+))/comment/$',views.commentreq,name='comment'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += [
        url(r'^media/(?P<path>.*)/$', serve,{'document_root': settings.MEDIA_ROOT,}),
    ]

