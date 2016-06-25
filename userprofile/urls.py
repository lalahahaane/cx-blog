from django.conf.urls import include, url
from django.views.generic import TemplateView
from django.views.static import serve
from django.conf.urls.static import static
from django.conf import settings
from userprofile import views

urlpatterns = [
    # url以profile开头
    url(r'^all/$', TemplateView.as_view(template_name = 'userprofile/profile.html'),name='user-profile'),
    url(r'^register/$', views.register, name='register'),
    url(r'^user-login/$', views.user_login, name='user-login'),
    url(r'^changepassword/$', views.changepwd, name='change_password'),
    url(r'^forgetpassword/$', views.forgetpwd, name='forget_password'),
    url(r'^changeusername/$', views.changeusername, name='change_username'),
    url(r'^user-logout/$', views.user_logout, name='logout'),
    url(r'^qq-connect/', views.get_qqlogin_connect, name='qqconnect'),
    url(r'^qq-login/', views.QQ_login_complete, name='qqlogin'),
    url(r'^git-connect/', views.get_gitlogin_connect, name='gitconnect'),
    url(r'^git-login/', views.GIT_login_complete, name='gitlogin'),
    url(r'^google-login/$', views.home, name='googlelogin'),
    url(r'^done/$', views.done, name='done'),
    url('', include('social.apps.django_app.urls', namespace='social')),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += [
        url(r'^media/(?P<path>.*)/$', serve,{'document_root': settings.MEDIA_ROOT,}),
    ]



