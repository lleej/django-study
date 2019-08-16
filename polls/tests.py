from datetime import datetime, timedelta

from django.test import TestCase, LiveServerTestCase, tag
from django.urls import reverse
from selenium.webdriver.chrome.webdriver import WebDriver

from .models import Question, Choice


def create_question(question_text, days):
    """
    根据参数创建问题
    :param question_text: 问题描述
    :param days: 发布时间的偏移量。单位：天，正值前偏移，负值后偏移
    :return: 问题实例
    """
    time = datetime.now() + timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


def create_choice(question, choice_text, votes):
    """
       根据参数创建问题答案
       :param question: 答案所属问题
       :param choice_text: 答案描述
       :param votes: 当前票数
       :return: 答案的实例
       """
    return Choice.objects.create(question=question, choice_text=choice_text, votes=votes)


@tag('model')
class QuestionModelTests(TestCase):
    """
    问题模型测试类
    """
    def test_was_published_recently_with_future_question(self):
        """
        当添加一个发布时间为未来时间的问题时，was_published_recently函数应该返回False
        """
        time = datetime.now() + timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False, msg='测试未来日期')

    def test_was_published_recently_with_old_question(self):
        """
        当添加一个发布时间过去了1天的问题时，was_published_recently函数应该返回False
        """
        time = datetime.now() - timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False, msg='测试过去日期')

    def test_was_published_recently_with_recent_question(self):
        """
        当添加一个发布时间过去不到1天的问题时，was_published_recently函数应该返回True
        """
        time = datetime.now() - timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True, msg='测试当前日期')


@tag('view')
class QuestionIndexViewTests(TestCase):
    """
    问题IndexView视图类测试
    """
    def test_no_question(self):
        """
        如果问题表为空，显示适当的提示信息
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '没有投票信息')
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        """
        发布时间是过去的问题，显示在首页中
        """
        create_question(question_text='过去的问题.', days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: 过去的问题.>'])

    def test_future_question(self):
        """
        发布时间是未来的问题，不显示在首页中
        """
        create_question(question_text='未来的问题.', days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question(self):
        """
        当存在发布时间为过去和未来的多个问题时，只显示过去的问题
        """
        create_question(question_text='过去的问题.', days=-30)
        create_question(question_text='未来的问题.', days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: 过去的问题.>'])

    def test_two_past_questions(self):
        """
        当有多个发布时间为过去的问题，都显示出来
        """
        create_question(question_text='过去的问题1.', days=-30)
        create_question(question_text='过去的问题2.', days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: 过去的问题2.>', '<Question: 过去的问题1.>'])


@tag('view')
class QuestionDetailViewTests(TestCase):
    """
    DetailView视图类的测试
    """
    def test_future_question(self):
        """
        发布时间是未来的问题，不显示
        """
        future_question = create_question(question_text='未来的问题.', days=5)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        发布时间是过去的问题，显示
        """
        past_question = create_question(question_text='过去的问题.', days=-5)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)


@tag('view')
class QuestionResultsViewTests(TestCase):
    """
    ResultsView视图类的测试
    """
    def test_future_question(self):
        """
        发布时间是未来的问题，不显示
        """
        future_question = create_question(question_text='未来的问题.', days=5)
        url = reverse('polls:results', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        发布时间是过去的问题，显示
        """
        past_question = create_question(question_text='过去的问题.', days=-5)
        url = reverse('polls:results', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)


@tag('view')
class ChoiceVoteViewTests(TestCase):
    """
    测试问题投票视图
    """
    def test_one_user_vote(self):
        """
        测试只有一个人投票时，票数每次增加1
        """
        vote_question = create_question(question_text='投票的问题.', days=-5)
        choice_1 = create_choice(vote_question, '答案1', 0)
        choice_2 = create_choice(vote_question, '答案2', 0)

        url = reverse('polls:vote', args=(vote_question.id,))
        response = self.client.post(url, {'choice': choice_1.id})
        self.assertEqual(response.status_code, 302)

        choice = Choice.objects.get(pk=choice_1.id)
        self.assertEqual(choice.votes, 1)

        choice = Choice.objects.get(pk=choice_2.id)
        self.assertEqual(choice.votes, 0)


@tag('model')
class ChoiceModelTests(TestCase):
    """
    答案模型的测试用例
    """
    def test_two_user_vote(self):
        """
        测试有两个人同时投票
        """
        question = create_question(question_text='投票的问题.', days=-5)
        choice = create_choice(question, '答案1', 0)
        choice_2 = Choice.objects.get(pk=1)

        choice_2.votes += 1
        choice_2.save()
        choice.vote()
        self.assertEqual(choice.votes, 2)


@tag('selenium')
class VoteSeleniumTests(LiveServerTestCase):
    """
    使用Selenium模拟测试
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = WebDriver('/Users/lijie/downloads/chromedriver')
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_vote(self):
        """
        测试投票
        """
        question = create_question(question_text='投票的问题.', days=-5)
        choice = create_choice(question, '答案1', 0)
        create_choice(question, '答案2', 0)
        self.selenium.get('%s%s' % (self.live_server_url, reverse('polls:detail', args=(question.id,))))
        self.selenium.find_element_by_id('choice1').click()
        self.selenium.find_element_by_id('vote').click()
        choice.refresh_from_db()
        self.assertEqual(choice.votes, 1)

