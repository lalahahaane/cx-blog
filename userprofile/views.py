from .forms import RegisterUserForm,RegisterProfileForm, ChangepwdForm, ForgetpwdForm, LoginForm, ChangeusernameForm
from django.contrib.auth import authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from sorl.thumbnail import delete
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.shortcuts import render, render_to_response
from django.views.generic import TemplateView
from django.contrib.auth.models import User
from .models import UserProfile
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from social.backends.google import GooglePlusAuth
from social.backends.utils import load_backends
from userprofile.decorators import render_to
import requests
import urllib.parse
import json
import copy
import re
import uuid


def register(request):
    '''
    注册
    '''
    registered = False
    if request.method == 'POST':
        user_form = RegisterUserForm(data=request.POST)
        profile_form = RegisterProfileForm(data=request.POST)
        username = request.POST.get('username', '')
        if user_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            if 'picture' in request.FILES:
                image = request.FILES['picture']
                profile = UserProfile(
                    user_id = user.id,
                    picture = image,
                    width_field = 100,
                    height_field = 100
                )
                delete(image)
            else:
                #默认头像
                profile = UserProfile(
                        user_id = user.id,
                        width_field = 100,
                        height_field = 100
                    )
            profile.save()
            registered = True
        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = RegisterUserForm()
        profile_form = RegisterProfileForm()
    return render(request, 'userprofile/register.html',\
                  {'user_form': user_form, 'profile_form': profile_form, 'registered': registered})


@login_required
def changepwd(request):
    '''
    用户已经登录的情况下修改密码
    '''
    if request.method == 'GET':
        form = ChangepwdForm()
        return render_to_response('userprofile/password_change.html', RequestContext(request, {'form': form,}))
    else:
        form = ChangepwdForm(request.POST)
        if form.is_valid():
            username = request.user.username
            oldpassword = request.POST.get('oldpassword', '')
            user = authenticate(username=username, password=oldpassword)
            if user is not None and user.is_active:
                newpassword = request.POST.get('newpassword1', '')
                user.set_password(newpassword)
                user.save()
                return render_to_response('home', RequestContext(request,{'changepwd_success':True}))
            else:
                return render_to_response('userprofile/password_change.html', RequestContext(request, {'form': form,'oldpassword_is_wrong':True}))
        else:
            return render_to_response('userprofile/password_change.html', RequestContext(request, {'form': form,}))

def passwordture(request, user_list, password):
    '''
    获得用户列表，验证用户和密码能不能匹配，如果能匹配就跳出循环，登录该用户,并返回该用户。
    如果不能匹配就返回None。
    '''
    result = None
    for usr in user_list:
        user = authenticate(username=usr.username, password=password)
        if user is not None and user.is_active:
            login(request, user)
            result = usr
            break
        else:
            continue
    return result

def user_login(request):

    if request.method == 'GET':
        form = LoginForm()
        return render_to_response('userprofile/login.html', RequestContext(request, {'form': form,}))
    else:
        form = LoginForm(request.POST)
        if form.is_valid():
            email = request.POST.get('email', '')
            users = User.objects.filter(email=email)
            password = request.POST.get('password')
            if passwordture(request, users, password):
                return HttpResponseRedirect(reverse('home'))
            else:
                return render_to_response('userprofile/login.html', RequestContext(request, {'form': form,'user_or_password_is_error':True}))
        else:
            return render_to_response('userprofile/login.html', RequestContext(request, {'form': form,}))

@login_required
def user_logout(request):
    '''
    退出网站
    '''
    logout(request)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def forgetpwd(request):
    '''
    用户忘记密码
    '''
    if request.method == 'GET':
        form = ForgetpwdForm()
        return render_to_response('userprofile/forget_password.html', RequestContext(request, {'form': form,}))
    else:
        form = ForgetpwdForm(request.POST)
        if form.is_valid():
            email = request.POST.get('email', '')
            user = User.objects.filter(email=email)[0]
            newpassword = request.POST.get('newpassword1', '')
            if user:
                user.set_password(newpassword)
                user.save()
                return HttpResponseRedirect('/login/')
            else:
                return render_to_response('userprofile/forget_password.html', RequestContext(request, {'form': form,'email_is_not_exit':True}))
        else:
            return render_to_response('userprofile/forget_password.html', RequestContext(request, {'form': form,}))

@login_required
def changeusername(request):
    '''
    用户已经登录的情况下修改用户名
    '''
    if request.method == 'GET':
        form = ChangeusernameForm()
        return render_to_response('userprofile/username_change.html', RequestContext(request, {'form': form,}))
    else:
        form = ChangeusernameForm(request.POST)
        if form.is_valid():
            newusername = request.POST.get('newusername', '')
            user = request.user
            if user.is_active:
                logout(request)
                user.username = newusername
                user.save()
                newuser = authenticate(username=newusername, password=user.password)
                login(request, newuser)
                return HttpResponseRedirect('..')
            else:
                return render_to_response('userprofile/password_change.html', RequestContext(request, {'form': form,'user_is_not_active':True}))
        else:
            return render_to_response('userprofile/password_change.html', RequestContext(request, {'form': form,}))

class ProfileView(LoginRequiredMixin, TemplateView):
    '''
    网站登录用户可见
    '''
    template_name = 'userprofile/profile.html'


##############################
######   google登录    #######
##############################


def context(**extra):
    return dict({
        'plus_id': getattr(settings, 'SOCIAL_AUTH_GOOGLE_PLUS_KEY', None),
        'plus_scope': ' '.join(GooglePlusAuth.DEFAULT_SCOPE),
        'available_backends': load_backends(settings.AUTHENTICATION_BACKENDS)
    }, **extra)


@render_to('index.html')
def home(request):
    """Home view, displays login mechanism
    """

    if request.user.is_authenticated():
        return redirect('done')
    return context()


@login_required
@render_to('index.html')
def done(request):
    """Login complete view, displays user data"""
    return context(google_required=True)



##############################
######      qq登录     #######
##############################


def get_qq_after_login_url(request):
    '''
    保存初始url,以便登录后能跳转回此url
    '''
    after_login_url = request.META.get('HTTP_REFERER', '/')
    host = request.META['HTTP_HOST']
    if after_login_url.startswith('http') and host not in after_login_url:
        after_login_url = '/'
        if after_login_url.endswith('/user-login/'):
            after_login_url = reverse('home')
    request.session['after_login_url'] = after_login_url

def get_qqlogin_connect(request):
        '''
        点击qq登录时的url
        https://graph.qq.com/oauth2.0/authorize?response_type=code&client_id=101232…&state=xxxxxx
        '''
        get_qq_after_login_url(request)
        qq_state = uuid.uuid4().hex
        request.session['qq_auth_state'] = qq_state
        data = {
                    'response_type': 'code',
                    'client_id': settings.QQ_APP_ID,
                    'state': qq_state,
                    'redirect_uri': settings.QQ_CALLBACK,
                    'scope': 'get_user_info',
                }
        params = urllib.parse.urlencode(data)
        qq_auth_url = 'https://graph.qq.com/oauth2.0/authorize?%s'% params
        return redirect(qq_auth_url)


def qq_get_access_token(request):
    '''
    获取Authorization Code即下面url里的code
    http://graph.qq.com/demo/index.jsp?code=9A5F************************06AF&state=test
    利用Authorization Code,获取access_token
    '''
    #确认接收的state是否是原先我们给state取的值
    original_state = request.session.get('qq_auth_state')
    if not original_state:
        raise Http404
    del(request.session['qq_auth_state'])
    state = request.GET.get('state')
    code = request.GET.get('code')
    if not state or not code:
        raise Http404
    if original_state != state:
        raise Http404


    params = {'grant_type': 'authorization_code',
              'client_id': settings.QQ_APP_ID,
              'client_secret': settings.QQ_APP_KEY,
              'code': code,
              'redirect_uri': settings.QQ_CALLBACK,}
    #https://graph.qq.com/oauth2.0/token?     获取access_token
    url = '%s/%s/%s?%s' % ('https://graph.qq.com', 'oauth2.0', 'token', urllib.parse.urlencode(params))
    str_url = requests.get(url).text  #获得str 'access_token=1xxx&expires_in=2xxx&refresh_token=3xxx'

    re_url= re.sub(r'[&|=]', ' ', str_url)
    c = re_url.split(' ')
    dict_url = {}
    for i in [0,2,4]:
        dict_url[c[i]] = c[i+1] # {'refresh_token': '3xxx', 'access_token': '2xxx', 'expires_in': '1xxx'}
    return dict_url


def qq_get_openid(request, access_token):
    #https://graph.qq.com/oauth2.0/me?access_token=******获取openid
    params = {'access_token': access_token}
    url = '%s/%s/%s?%s' % ('https://graph.qq.com', 'oauth2.0', 'me', urllib.parse.urlencode(params))
    bb = requests.get(url)
    bb1 = bb.text  #callback( {"client_id":"101xxxx","openid":"2B6xxxx"} );
    str_url = bb1.split(' ')[1] # str {"client_id":"101xxxx","openid":"2B6xxxx"}
    re_url = re.sub(r'["|,|:|{|}]', ' ', str_url)
    c = re_url.strip().split(' ')  #['client_id', '', '', '101xxx', '', '', 'openid', '', '', '2B6xxx']
    dict_url = {}
    dict_url[c[0]] = c[3]
    dict_url[c[6]] = c[9]
    return dict_url #{"client_id":"101xxx","openid":"2B6xxxx"}

def qq_get_user_info(request, access_token, openid):
    oauth_consumer_key = settings.QQ_APP_ID
    params = {'access_token': access_token,
              'oauth_consumer_key': oauth_consumer_key,
              'openid': openid,
              }

    url = 'https://graph.qq.com/user/get_user_info?%s' % urllib.parse.urlencode(params)
    res = requests.get(url)
    user_info = res.content.decode('utf-8')      #处理获取的信息
    dat = json.loads(user_info)
    username = dat['nickname']
    email = '%s@qq.com'% openid
    password = access_token
    uuu = UserProfile.objects.filter(picture__icontains=username)
    if uuu:
        usp = uuu[0]
    else:
        if User.objects.get(username=username):
            usp = User.objects.get(username=username)
        else:
            usp = User.objects.create_user(username, email, password)                    #创建用户
        picture_url = dat['figureurl_2'] #100*100头像的url
        location = settings.MEDIA_ROOT
        pic_address = "%s%s##%s.jpg"% (location, username, openid)
        uspr = UserProfile()
        uspr.download_image_save(picture_url, pic_address, usp)

    user = authenticate(username=username, password=password)
    login(request, user)


def QQ_login_complete(request):

    try:
        user = request.user
        if user.is_active:
            pass
        else:
            dict_access_token = qq_get_access_token(request)
            access_token = dict_access_token['access_token']
            dict_openid = qq_get_openid(request, access_token)

            openid = dict_openid['openid']
            qq_get_user_info(request, access_token, openid)
            after_login_url = copy.copy(request.session['after_login_url'])
            del(request.session['after_login_url'])
        return HttpResponseRedirect(after_login_url)
    except:
        return HttpResponse(u'登录过程出现错误')

##############################
######      git登录     #######
##############################


def get_gitlogin_connect(request):
        '''
        点击git登录时的url

        '''
        get_qq_after_login_url(request)
        git_state = uuid.uuid4().hex
        request.session['git_auth_state'] = git_state
        data = {
            'response_type': 'code',
            'client_id': settings.SOCIAL_AUTH_GITHUB_KEY,
            'state': git_state,
            'redirect_uri': settings.GIT_CALLBACK,
            'scope': 'get_user_info',
        }

        params = urllib.parse.urlencode(data)
        url = "https://github.com/login/oauth/authorize?%s"% params
        return redirect(url)

def get_git_access_token(request):
    original_state = request.session.get('git_auth_state')
    if not original_state:
        raise Http404
    del(request.session['git_auth_state'])
    state = request.GET.get('state')
    code = request.GET.get('code')
    if not state or not code:
        raise Http404
    if original_state != state:
        raise Http404

    url = 'https://github.com/login/oauth/access_token'
    params = {
        'grant_type': 'authorization_code',
        'client_id': settings.SOCIAL_AUTH_GITHUB_KEY,
        'client_secret': settings.SOCIAL_AUTH_GITHUB_SECRET,
        'code': code,
        'redirect_uri': settings.GIT_CALLBACK,
    }

    headers = {'accept': 'application/json'}
    url = 'https://github.com/login/oauth/access_token'
    r = requests.post(url, params=params, headers=headers)
    if not r.ok:
        raise Http404
    data = r.json()
    access_token = data['access_token']
    return access_token

def get_git_user_info(request, access_token):
    headers = {
        'authorization': 'token %s' % access_token
    }
    r = requests.get('https://api.github.com/user', headers=headers)
    data = r.json()
    username = data['login'] + '(git)'
    password = data['id']
    email = '%s@git.com'% access_token
    uuu = UserProfile.objects.filter(picture__icontains=username)
    if uuu:
        usp = uuu[0]
    else:
        if User.objects.get(username=username):
            usp = User.objects.get(username=username)
        else:
            usp = User.objects.create_user(username, email, password)                    #创建用户
        picture_url = data['avatar_url'] #头像的url
        location = "/home/lalahahaane/chexi-blog/firstdjango/static/media/profile_images/"
        pic_address = "%s%s.jpg"% (location, username)
        uspr = UserProfile()
        uspr.download_image_save(picture_url, pic_address, usp)

    user = authenticate(username=username, password=password)
    login(request, user)

def GIT_login_complete(request):

    after_login_url = copy.copy(request.session.get('after_login_url', None))
    if after_login_url:
        del(request.session['after_login_url'])
    user = request.user
    if user.is_active:
        pass
    else:
        try:
            access_token = get_git_access_token(request)
            get_git_user_info(request, access_token)
        except:
            pass

    return HttpResponseRedirect(after_login_url)
