from django.core.files.base import ContentFile
from urllib.request import urlretrieve
from requests import request, HTTPError
import requests
from django.db import models
from django import template
from django.contrib.auth.models import User
import datetime
import os
from uuid import uuid4

register = template.Library()


def upload_location(instance, filename):
    #获取图片扩展名
    ext =  filename.split('.')[-1]
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for i in ['-', ':', ' ']:
        now2 = now.replace(i,'')
    return ("profile_images/%s---%s.%s") %(instance.user, now2, ext)


class UserProfile(models.Model):#用户
    user    = models.OneToOneField(User)
    picture = models.ImageField(upload_to=upload_location,
                                null=True,
                                blank=True,
                                width_field="width_field",
                                height_field="height_field",
                                default='myexample.jpg')
    height_field = models.IntegerField(default=100)
    width_field = models.IntegerField(default=100)

    # https://docs.djangoproject.com/en/1.9/ref/contrib/admin/

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = verbose_name = '已注册的用户'

    def download_image_save(self, url, location, usp,*args, **kwargs):
        try:
            uspr = UserProfile()
            uspr.user = usp
            uspr.height_field = 100
            uspr.width_field = 100
            data = requests.get(url)
            urlretrieve(url, location)   #下载头像
            uspr.picture.save(location, ContentFile(data.content),save=True)
            uspr.save
        except:
            pass



