from django.db import models
from django import template
from django.contrib.auth.models import User
from sorl.thumbnail import ImageField
from userprofile.models import UserProfile
register = template.Library()



class Blogitem(models.Model):
    title            = models.CharField(max_length=200)
    content_html     = models.TextField()#html格式博客正文
    content_markdown = models.TextField()#markdown格式博客正文
    publication_date = models.DateTimeField()
    update_date      = models.DateTimeField()
    first_tag        = models.CharField(max_length=200,
                                        default= 'other')#url分类
    tag_supplement   = models.CharField(max_length=100) #tag补充
    view_number      = models.IntegerField()

    def __str__(self):
        return (u'%s %s') %(self.title,self.publication_date)

    class Admin:
        pass

    class Meta:
        ordering = ['publication_date']
        verbose_name_plural = verbose_name = '博客'




class Comment(models.Model):
    comment_blog = models.ForeignKey(Blogitem, verbose_name=u'博客')
    comment_user = models.ForeignKey(UserProfile, verbose_name= u'用户',blank= True,null = True)
    comment_date = models.DateTimeField(verbose_name=u'评论日期',auto_now = True)
    comment_content = models.TextField(verbose_name=u'评论内容')
    comment_approved = models.BooleanField(verbose_name=u'审核',default= True)
    comment_like = models.IntegerField(verbose_name=u'赞的个数',default=0)

    def __str__(self):
        return (u'%s %s %s %s') % (self.comment_blog, self.comment_user, self.comment_content, self.comment_date)

    class Meta:
        ordering = ['-comment_date']
        verbose_name_plural = verbose_name = '评论'












