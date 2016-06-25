# coding=utf-8
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from userprofile.models import UserProfile
from django import template

register = template.Library()


@register.filter(name='show_avatar')
def show_avatar(value):
    '''
    显示头像
    '''
    if value.is_authenticated:
        try:
            UserProfile.objects.get(user=value)
            #user不是超级用户但是已经注册
            avatar = UserProfile.objects.get(user=value).picture
        except UserProfile.DoesNotExist:
            #user是超级用户或第三方用户但是没有注册
            newuser = UserProfile(
                        user_id = value.id,
                        width_field = 100,
                        height_field = 100
                    )
            newuser.save()
            avatar = newuser.picture
        return avatar.url

@register.filter(name='tag_str_to_list')
def tag_str_to_list(value):
    '''
    将first_tag由str转换为list
    '''
    new_value_list = []
    value_list = value.split(' ')
    for tag in value_list:
        if tag:
            new_value_list.append(tag)
    return new_value_list

@register.filter(name='get_login_redirect_url')
def get_login_redirect_url(request):

    after_login_url = request.META.get('HTTP_REFERER', '/')
    host = request.META['HTTP_HOST']
    if after_login_url.startswith('http') and host not in after_login_url:
        after_login_url = '/'
        if after_login_url.endswith('/user-login/'):
            after_login_url = reverse('home')
    return after_login_url