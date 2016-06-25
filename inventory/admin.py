from django.contrib import admin
from .models import Blogitem, Comment



class BlogItemAdmin(admin.ModelAdmin):
    list_display   = ['title', 'view_number', 'publication_date', 'content_html', 'content_markdown']
    search_fields  = ('title', 'publication_date')
    list_filter    = ['publication_date']#为日期型字段提供了快捷过滤方式，它包含：今天、过往七天、当月和今年。
    date_hierarchy = 'publication_date'#页面中的列表顶端会有一个逐层深入的显示.
                                         #它从可用的年份 开始，然后逐层细分到月乃至日。
    fields = ('title', 'content_html', 'content_markdown')#不在括号里的不能被其他人编辑
    readonly_fields = ("publication_date", 'content_html', 'content_markdown')



class CommentAdmin(admin.ModelAdmin):
    readonly_fields = ('comment_date',)
    list_display = ['comment_user','comment_date', 'comment_content','comment_blog', 'comment_approved']
    search_fields = ('comment_blog', 'comment_user', 'comment_date', 'comment_content')
    fields = ('comment_blog', 'comment_user', 'comment_date', 'comment_content')
    date_hierarchy = 'comment_date'


admin.site.register(Blogitem, BlogItemAdmin)
admin.site.register(Comment, CommentAdmin)