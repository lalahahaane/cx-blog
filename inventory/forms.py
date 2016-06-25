from __future__ import unicode_literals
from django import forms
from .models import Blogitem
import markdown
import datetime



class BlogPublishForm(forms.Form):
    '''
    文章发布
    '''
    title = forms.CharField(
        label = u'文章标题',
        widget = forms.TextInput(attrs={'class': '', 'placeholder': u'标题添加'}),
    )
    content = forms.CharField(
        label= u'文章内容',
        min_length= 4,
        widget = forms.Textarea()
    )
    first_tag = forms.CharField(
        label = u'第一个标签',
        widget = forms.TextInput(attrs={'class': '', 'placeholder': u'添加第一个标签'}),
    )
    tag_supplement = forms.CharField(
        label = u'补充的标签',
        widget = forms.TextInput(attrs={'class': '', 'placeholder': u'补充标签'}),
    )

    def save(self):
        cd = self.cleaned_data
        title = cd['title']
        now = datetime.datetime.now()
        content_markdown = cd['content']
        content_html = markdown.markdown(cd['content'], extensions=['markdown.extensions.extra', 'markdown.extensions.codehilite'])
        data = content_html
        blogitem = Blogitem(
            title = title,
            content_markdown = content_markdown,
            content_html = data,
            first_tag = cd['first_tag'],
            tag_supplement = cd['tag_supplement'],
            view_number = 0,
            publication_date = now,
            update_date = now
        )
        blogitem.save()



class BlogEditForm(forms.Form):
    '''
    文章编辑
    '''
    title = forms.CharField(
        label = u'文章标题',
        widget = forms.TextInput(attrs={'class': '', 'placeholder': u'标题添加'}),
    )
    content = forms.CharField(
        label= u'文章内容',
        min_length= 4,
        widget = forms.Textarea()
    )
    first_tag = forms.CharField(
        label = u'第一个标签',
        widget = forms.TextInput(attrs={'class': '', 'placeholder': u'添加第一个标签'}),
    )
    tag_supplement = forms.CharField(
        label = u'补充的标签',
        widget = forms.TextInput(attrs={'class': '', 'placeholder': u'补充标签'}),
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        self.id = kwargs.pop('id')
        super(BlogEditForm, self).__init__(*args, **kwargs)

    def save(self):
        blogitem = Blogitem.objects.get(id=self.id)
        cd = self.cleaned_data
        title = cd['title']
        now = datetime.datetime.now()
        content_markdown = cd['content']
        content_html = markdown.markdown(cd['content'], extensions=['markdown.extensions.extra', 'markdown.extensions.codehilite'])

        if blogitem: #以前创建的
            blogitem.title = title
            blogitem.content_markdown = content_markdown
            blogitem.content_html = content_html
            blogitem.first_tag = cd['first_tag']
            blogitem.tag_supplement = cd['tag_supplement']
            blogitem.update_date = now
            # blogitem.publication_date = now
        else:#现在创建的
            blogitem = Blogitem(
                title = title,
                content_markdown = content_markdown,
                content_html = content_html,
                first_tag = cd['first_tag'],
                tag_supplement = cd['tag_supplement'],
                view_number = 0,
                publication_date = now,
                update_date = now)
        blogitem.save()



























