from datetime import datetime, timedelta
from django.db import models

# Create your models here.


class Question(models.Model):
    """
    问题模型
    """
    question_text = models.CharField(max_length=200, help_text='问题', verbose_name='问题描述')
    pub_date = models.DateTimeField(verbose_name='发布时间')
    question_img = models.FileField(upload_to='files/', default=None)
    isok = True

    class Meta:
        verbose_name = '问题'
        verbose_name_plural = '问题'

    def __str__(self):
        return self.question_text

    def was_published_recently(self):
        now = datetime.now()
        return now - timedelta(days=1) <= self.pub_date <= now
    was_published_recently.admin_order_field = 'pub_date'
    was_published_recently.boolean = True
    was_published_recently.short_description = '最近发布'


class Choice(models.Model):
    """
    答案
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices', verbose_name='所属问题')
    choice_text = models.CharField(max_length=200, verbose_name='答案')
    votes = models.IntegerField(default=0, verbose_name='投票')

    class Meta:
        verbose_name = '答案'
        verbose_name_plural = '答案'

    def __str__(self):
        return self.question.question_text + ":" + self.choice_text

    def vote(self):
        """
        给答案投票，投票后该答案的投票数量+1
        """
        self.votes = models.F('votes') + 1
        self.save()
        self.refresh_from_db()
