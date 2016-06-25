from __future__ import unicode_literals
from django import forms
from django.contrib.auth.models import User
from .models import UserProfile
from django.utils.translation import ugettext_lazy as _
import re



class RegisterUserForm(forms.ModelForm):
    error_messages = {
        'password_mismatch': _(u"您输入的两次密码不一致"),
        'required': _(u"邮箱格式不正确 "),
        'username_format_error': _(u'用户名中不能包含空格和@字符'),
        'username_had_register': _(u'此用户名已经注册，请重新输入!'),
        'too_long':_(u'您的密码太长！'),
        'too_short':_(u'您的密码太短！'),
    }
    username = forms.CharField(
        label=u'用户名',
        help_text=u'用户名不能包含空格和@字符。',
        max_length=20,
        initial='',
        widget=forms.TextInput(attrs={'placeholder':u"请输入您的用户名！",'class': 'form-control'}),
    )

    password = forms.CharField(label=_(u"密码"),
        help_text=u'密码 6-30 个字',
        widget=forms.PasswordInput(attrs={'placeholder':u"请输入您的密码！",'class': 'form-control'}))

    '''password2 = forms.CharField(label=_(u"确认密码"),
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text=_(u"输入与上面输入框相同的密码以进行验证！"))'''

    email = forms.CharField(label=_(u"邮箱"), max_length=70,required=True,
        help_text=_(u"邮箱方便注册和联系您 "),
        widget=forms.TextInput(attrs={'placeholder':u"请输入您的邮箱！",'class': 'form-control'})
        )


    class Meta:
        model = User
        fields = ['username','password', 'email']


    def clean_username(self):
        username = self.cleaned_data['username']
        if ' ' in username or '@' in username:
            raise forms.ValidationError(self.error_messages['username_format_error'],code='username_format_error')
        res = User.objects.filter(username=username)
        if len(res) != 0:
            raise forms.ValidationError(self.error_messages['username_had_register'],code='username_had_register')
        return username

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if len(password)<6:
            raise forms.ValidationError(
                self.error_messages['too_short'],
                code='too_short',
            )
        if len(password)>30:
            raise forms.ValidationError(
                self.error_messages['too_long'],
                code='too_long',
            )
        return password


    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            if re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email):
                pass
            else:
                raise forms.ValidationError(self.error_messages['required'],code='required',)
        else:
            raise forms.ValidationError(self.error_messages['required'],code='required')
        return email


class RegisterProfileForm(forms.ModelForm):

    picture = forms.ImageField(
        label=u'用户头像',
        help_text=_(u"请点击选择文件按钮上传您的头像！"),
        widget=forms.FileInput()
    )

    #height_field = forms.IntegerField()
    #width_field = forms.IntegerField()

    class Meta:
        model = UserProfile
        fields = ('picture',)

class LoginForm(forms.Form):

    error_messages={'email_has_not_register': u'您还没有注册！'}

    email = forms.CharField(
            label=_(u"邮箱"),
            max_length=70,
            required=True,
            help_text=_(u"邮箱方便注册和联系您 "),
            error_messages={'required': u'邮箱格式不正确,请输入您的邮箱！'},
            widget=forms.TextInput(attrs={'placeholder':u"请输入您的邮箱！",'class': 'form-control'})
        )

    password = forms.CharField(
        required=True,
        label=u"密码",
        help_text=_(u'密码 6-30 个字'),
        error_messages={'required': u'密码错误！'},
        widget=forms.PasswordInput(
            attrs={
                'placeholder':u"请输入密码！",
                'class': 'form-control'
            }
        ),
    )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            if re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email):
                if User.objects.filter(email=email):
                    pass
                else:
                    raise forms.ValidationError(self.error_messages['email_has_not_register'],code='email_has_not_register')
            else:
                raise forms.ValidationError(self.error_messages[u'邮箱格式不正确,请输入您的邮箱！'],code=u'邮箱格式不正确,请输入您的邮箱！',)
        else:
            raise forms.ValidationError(self.error_messages['required'],code='required')
        return email

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if len(password)<6:
            raise forms.ValidationError(
                self.error_messages['too_short'],
                code='too_short',
            )
        if len(password)>30:
            raise forms.ValidationError(
                self.error_messages['too_long'],
                code='too_long',
            )
        return password

    #参考https://docs.djangoproject.com/en/1.9/ref/forms/validation/

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('picture',)

class ChangepwdForm(forms.Form):
    '''
    修改密码
    '''
    oldpassword = forms.CharField(
        required=True,
        label=u"原密码",
        error_messages={'required': u'请输入原密码'},
        widget=forms.PasswordInput(
            attrs={
                'placeholder':u"请输入原密码",
                'class': 'form-control'
            }
        ),
    )
    newpassword1 = forms.CharField(
        required=True,
        label=u"新密码",
        error_messages={'required': u'请输入新密码'},
        widget=forms.PasswordInput(
            attrs={
                'placeholder':u"请输入新密码",
                'class': 'form-control'
            }
        ),
    )
    newpassword2 = forms.CharField(
        required=True,
        label=u"确认密码",
        error_messages={'required': u'请再次输入新密码'},
        widget=forms.PasswordInput(
            attrs={
                'placeholder':u"请再次输入新密码",
                'class': 'form-control'
            }
        ),
     )
    def clean(self):
        if not self.is_valid():
            raise forms.ValidationError(u"所有项都为必填项")
        elif self.cleaned_data['newpassword1'] != self.cleaned_data['newpassword2']:
            raise forms.ValidationError(u"两次输入的新密码不一样")
        else:
            cleaned_data = super(ChangepwdForm, self).clean()
        return cleaned_data

class ForgetpwdForm(forms.Form):
    '''
    忘记密码
    '''

    error_messages = {
        'too_long':_(u'您的密码太长！'),
        'too_short':_(u'您的密码太短！'),
        'you_have_not_register':_(u'您还没有注册！'),
    }

    email = forms.CharField(
            label=_(u"邮箱"),
            max_length=70,
            required=True,
            help_text=_(u"邮箱方便注册和联系您 "),
            error_messages={'required': u'请输入您的邮箱！'},
            widget=forms.TextInput(attrs={'placeholder':u"请输入您的邮箱！",'class': 'form-control'})
        )

    newpassword1 = forms.CharField(
        required=True,
        label=u"新密码",
        error_messages={'required': u'请输入新密码'},
        widget=forms.PasswordInput(
            attrs={
                'placeholder':u"新密码",'class': 'form-control'
            }
        ),
    )
    newpassword2 = forms.CharField(
        required=True,
        label=u"请再次输入新密码！",
        error_messages={'required': u'请再次输入新密码'},
        widget=forms.PasswordInput(
            attrs={
                'placeholder':u"请再次输入新密码！",'class': 'form-control'
            }
        ),
     )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            if re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email):
                if User.objects.filter(email=email):
                    pass
                else:
                    raise forms.ValidationError(self.error_messages['you_have_not_register'],code='you_have_not_register')
            else:
                raise forms.ValidationError(self.error_messages['required'],code='required',)
        else:
            raise forms.ValidationError(u'请您的输入邮箱！')
        return email

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if len(password)<6:
            raise forms.ValidationError(
                self.error_messages['too_short'],
                code='too_short',
            )
        if len(password)>30:
            raise forms.ValidationError(
                self.error_messages['too_long'],
                code='too_long',
            )
        return password


class ChangeusernameForm(forms.Form):
    '''
    修改用户名
    '''
    error_messages = {
        'not_registered':_(u'您还没有注册！'),
        'username_format_error':_(u'用户名中不能包含空格和@字符')
    }

    email = forms.CharField(
            label=_(u"邮箱"),
            max_length=70,
            required=True,
            help_text=_(u"邮箱方便注册和联系您 "),
            error_messages={'required': u'请输入您的邮箱！'},
            widget=forms.TextInput(attrs={'placeholder':u"请输入您的邮箱！",'class': 'form-control'})
        )

    oldusername = forms.CharField(
        label=u'旧用户名',
        required=True,
        help_text=u'用户名不能包含空格和@字符。',
        max_length=20,
        initial='',
        widget=forms.TextInput(attrs={'placeholder':u"请输入您的旧用户名！",'class': 'form-control'}),
    )

    newusername = forms.CharField(
        required=True,
        label=u"新用户名",
        error_messages={'required': u'请输入您的新用户名'},
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder':u"请输入您的新用户名",
            }
        ),
    )

    def clean_oldusername(self):
        oldusername = self.cleaned_data['oldusername']
        if ' ' in oldusername or '@' in oldusername:
            raise forms.ValidationError(self.error_messages['username_format_error'],code='username_format_error')
        res = User.objects.filter(username=oldusername)
        if len(res):
            raise forms.ValidationError(self.error_messages['not_registered'],code='not_registered')
        return oldusername

    def clean_newusername(self):
        newusername = self.cleaned_data['newusername']
        if ' ' in newusername or '@' in newusername:
            raise forms.ValidationError(self.error_messages['username_format_error'],code='username_format_error')
        return newusername

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            if re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email):
                if User.objects.filter(email=email):
                    pass
                else:
                    raise forms.ValidationError(self.error_messages['not_registered'],code='not_registered')
            else:
                raise forms.ValidationError(self.error_messages['required'],code='required')
        else:
            raise forms.ValidationError(u'请您的输入邮箱！')
        return email




























