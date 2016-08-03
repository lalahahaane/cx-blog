from django.contrib.admin.views.decorators import staff_member_required
from social.backends.google import GooglePlusAuth
from social.backends.utils import load_backends
from django.core.paginator import PageNotAnInteger, Paginator, EmptyPage
from django.db.models import F, Q #查询列表
from firstdjango import settings
from functools import reduce
from django.views.generic.list import ListView
from django.views.generic.edit import FormView
from django.views.generic.detail import DetailView
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.http import HttpResponse, Http404
from django.shortcuts import render, render_to_response
from django.template.loader import get_template
from django.template import Context
from .models import Blogitem, UserProfile, Comment
from .forms import BlogPublishForm, BlogEditForm
from django.contrib.sitemaps import Sitemap
from datetime import datetime
import operator
import json




def context(**extra):
    '''
    python-social-auth 中用于第三方注册携带信息的重写了的 context
    '''
    return dict({
        'plus_id': getattr(settings, 'SOCIAL_AUTH_GOOGLE_PLUS_KEY', None),
        'plus_scope': ' '.join(GooglePlusAuth.DEFAULT_SCOPE),
        'available_backends': load_backends(settings.AUTHENTICATION_BACKENDS)
    }, **extra)




class AdminRequiredMixin(object):
    '''
    发布和编辑文章的权限
    '''
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(AdminRequiredMixin, cls).as_view(**initkwargs)
        return staff_member_required(view)

class IndexListView(ListView):
    '''
    首页
    '''
    template_name = 'index.html'
    model = Blogitem

    def get_context_data(self, **kwargs):

        blog_list_all = Blogitem.objects.all().order_by(F('publication_date').desc())[:50] #按照文章的发布日期从晚到早排序
        paginator = Paginator(blog_list_all, 10) #每一页显示十篇文章
        page = self.request.GET.get('page')
        try:
            blog_list = paginator.page(page)
        except PageNotAnInteger:#不满一页就取第一页
            blog_list = paginator.page(1)
        except EmptyPage:#页数太多，提供最后一页
            blog_list = paginator.page(paginator.num_pages)
        context['blog_list'] = blog_list
        return context

class CategoriesListView(ListView):
    '''
    文章分类
    '''
    template_name = 'inventory/item_categories.html'
    model = Blogitem

    def get_context_data(self, **kwargs):
        search_tag = self.kwargs.get('tag')
        blog_list_all = Blogitem.objects.filter(first_tag__contains=search_tag).order_by(F('publication_date').desc())[:50]
        paginator = Paginator(blog_list_all, 10)
        page = self.request.GET.get('page')
        try:
            blog_list = paginator.page(page)
        except PageNotAnInteger:#不满一页就取第一页
            blog_list = paginator.page(1)
        except EmptyPage:#页数太多，提供最后一页
            blog_list = paginator.page(paginator.num_pages)

        context = super(CategoriesListView, self).get_context_data(**kwargs)
        context['blog_list'] = blog_list
        return context


class BlogPublishView(AdminRequiredMixin, FormView):
    '''
    发布文章
    '''
    template_name = 'inventory/blog_publish.html'
    form_class = BlogPublishForm

    def form_valid(self, form):
        form.save()
        return super(BlogPublishView,self).form_valid(form)

    def get_success_url(self, **kwargs):
        blog_new = Blogitem.objects.all().order_by(F('publication_date').desc())[0]
        success_url = reverse('item_detail', args=(blog_new.id,))
        return success_url

class BlogDetailView(DetailView):
    '''
    文章详细内容
    '''
    model = Blogitem
    template_name = 'inventory/item_detail.html'
    slug_field = 'pk'

    def get_context_data(self, **kwargs):
        context = super(BlogDetailView, self).get_context_data(**kwargs)
        pk = self.kwargs.get('pk')
        try:
            item = Blogitem.objects.get(id=pk)
            item.view_number = item.view_number + 1
            item.save()
            comment_of_a_blog  = Comment.objects.filter(comment_blog_id=pk)
            keys = set([i.comment_group_by for i in comment_of_a_blog])
            ke = list(keys)
            result = {}
            for each_key in ke:
                result[str(each_key)] = list(Comment.objects.filter(comment_group_by=int(each_key)).order_by('id'))
            context['item'] = item
            context['comment_list'] = result
        except Blogitem.DoesNotExist:
            raise Http404(u"文章不存在，您无法访问！")

        return context

class BlogEditView(AdminRequiredMixin, FormView):
    '''
    编辑文章
    '''
    template_name = 'inventory/blog_publish.html'
    form_class = BlogEditForm
    blogitem = None

    # add the request to the kwargs
    def get_form_kwargs(self):
        '''
        将request添加到kwargs,FormView就能传递用户的登录信息
        '''
        kwargs = super(BlogEditView, self).get_form_kwargs()
        kwargs['request'] = self.request
        kwargs['id'] = self.kwargs.get('id')
        return kwargs


    def get_initial(self, **kwargs):
        '''
        设定表单初始值
        '''
        pk = self.kwargs.get('id')
        try:
            self.blogitem = Blogitem.objects.get(pk=pk)
            initial = {
                'title': self.blogitem.title,
                'content': self.blogitem.content_markdown,
                'first_tag': self.blogitem.first_tag,
                'tag_supplement': self.blogitem.tag_supplement,
            }
            return initial
        except Blogitem.DoesNotExist:
            raise Http404(u"文章不存在！")

    def form_valid(self, form, **kwargs):
        form.save()
        return super(BlogEditView, self).form_valid(form)

    def get_success_url(self, **kwargs):
        id = self.kwargs.get('id')
        success_url = reverse('item_detail', args=(id,))
        return success_url

def commentreq(request, pk):
    '''
    评论系统
    '''
    if request.is_ajax() and request.POST:
        #获取评论
        comment_content = request.POST.get('comment-get')
        #处理评论
        comment_co = comment_content.strip()
        #获取判断：是否是某条评论的回复。如果是，则返回replay-box-{{ id }},id为所回复的评论的Comment.id .如果不是，则返回"0"
        is_replay_or_not = request.POST.get('is_replay_or_not')
        #获取当前用户
        comment_user = request.user
        now = datetime.now()
        #用户没有登录
        if not comment_user.is_authenticated():
            return HttpResponse(json.dumps({'status': u'请登录后评论！'}), content_type='application/json')

        if len(comment_co)>4:
            usercomment = Comment()
            usercomment.comment_user = UserProfile.objects.get(user=request.user)
            usercomment.comment_content=comment_co
            usercomment.comment_blog=Blogitem.objects.get(id=pk)
            usercomment.comment_date = now
            usercomment.save()
            if '-' in is_replay_or_not:
                up_id = int(is_replay_or_not.split('-')[-1])
                usercomment.comment_group_by = Comment.objects.get(id=up_id).comment_group_by # 与所回复的评论的groupby一样
                usercomment.comment_is_replay_or_not = up_id # 所回复评论的id，同一个 groupby中可能有至少三个人评论，确定回复的具体人员
            else:
                usercomment.comment_group_by = usercomment.id
            usercomment.save()
            t = get_template('inventory/blog_comment_test.html')
            html = t.render(Context({'usercomment': usercomment}))
            return HttpResponse(json.dumps({'status':is_replay_or_not + u'评论提交成功！','html': html}), content_type='application/json')
        else:
            return HttpResponse(json.dumps({'status':u'多说几句吧！'}), content_type='application/json')
    else:
        return HttpResponse(json.dumps({'status': u'评论提交有误！'}), content_type='application/json')

def About(request):
    return render(request,'inventory/about.html')

def Webhistory(request):
    return render(request,'inventory/webhistory.html')



class BlogSearchView(ListView):
    """
    显示搜索结果
    """
    template_name = 'inventory/search_result.html'
    # context_object_name = 'latest_blogitem_list'
    model = Blogitem
    paginate_by = 10


    def get_context_data(self, **kwargs):
        context = super(BlogSearchView, self).get_context_data(**kwargs)
        query = self.request.GET.get('q')
        if query:
            query_list = query.split()
            result = Blogitem.objects.all().filter(
                reduce(operator.and_,
                       (Q(title__icontains=q) for q in query_list)) |
                reduce(operator.and_,
                       (Q(content_html__icontains=q) for q in query_list))
            )
            paginator = Paginator(result, self.paginate_by)
            page = self.request.GET.get('page')
            try:
                show_result = paginator.page(page)
            except PageNotAnInteger:#不满一页就取第一页
                show_result = paginator.page(1)
            except EmptyPage:#页数太多，提供最后一页
                show_result = paginator.page(paginator.num_pages)
            context['search_words'] =query
            context['result'] = show_result
        return context


class BlogSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.5

    def items(self):
        return ['item_detail', ]

    def lastmod(self, obj):
        return obj.update_date

    def location(self, item):
        return reverse(item)









































