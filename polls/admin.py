from django.contrib import admin
from django.db import models

# Register your models here.

from .models import Question, Choice


class ChoiceInLine(admin.TabularInline):
    model = Choice


@ admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """
    Question自定义样式
    """
    # fields = ['pub_date', 'question_text']
    # date_hierarchy = 'pub_date'
    fieldsets = [
        ('问题描述', {'fields': ['question_text']}),
        ('发布日期', {'fields': ['pub_date']}),
        ('上传文件', {'fields': ['question_img']}),
    ]
    list_display = ('question_text', 'pub_date', 'was_published_recently')
    # formfield_overrides = {
    #     models.CharField: {'widget': admin.}
    # }
    list_filter = ('pub_date', )
    search_fields = ('question_text', )
    inlines = [ChoiceInLine]


# admin.site.register(Question, QuestionAdmin)
