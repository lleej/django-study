from datetime import datetime

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic

from .models import Question, Choice


# def index(request):
#     """
#     投票首页
#     :param request:
#     :return:
#     """
#     latest_question_list = Question.objects.order_by('-pub_date')[:5]
#     context = {
#         'latest_question_list': latest_question_list
#     }
#     return render(request, 'polls/index.html', context)


class IndexView(generic.ListView):
    """
    投票首页视图类
    """
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
        只返回发布时间小于当前时间的问题
        """
        return Question.objects.filter(
            pub_date__lte=datetime.now()
        ).order_by('-pub_date')[:5]


# def detail(request, question_id):
#     """
#     查询问题详情信息
#     :param request:
#     :param question_id: 问题编号
#     :return: 问题详情
#     """
#     question = get_object_or_404(Question, pk=question_id)
#     context = {
#         'question': question
#     }
#     return render(request, 'polls/detail.html', context)


class DetailView(generic.DeleteView):
    """
    问题详情视图类
    """
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """
        过滤掉发布时间大于当前时间的问题
        """
        return Question.objects.filter(
            pub_date__lte=datetime.now()
        )


# def results(request, question_id):
#     """
#     查询问题的备选答案列表
#     :param request:
#     :param question_id: 问题编号
#     :return:
#     """
#     question = get_object_or_404(Question, pk=question_id)
#     return render(request, 'polls/results.html', {'question': question})


class ResultsView(generic.DeleteView):
    """
    问题投票结果视图类
    """
    model = Question
    template_name = 'polls/results.html'

    def get_queryset(self):
        """
        过滤掉发布时间大于当前时间的问题
        """
        return Question.objects.filter(
            pub_date__lte=datetime.now()
        )


def vote(request, question_id):
    """
    给问题投票
    :param request:
    :param question_id:
    :return:
    """
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choices.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': '选项无效！',
        })
    else:
        selected_choice.vote()
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
