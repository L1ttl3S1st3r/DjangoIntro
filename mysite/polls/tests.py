import datetime


from django.test import TestCase
from django.urls import reverse
from django.utils import timezone


from .models import Question


# HTTP ok code
HTTP_OK: int = 200

# HTTP error not found code
HTTP_NOT_FOUND: int = 404

# Offset of default question in the past
PAST_OFFSET: int = -30

# Offset of default question in the future
FUTURE_OFFSET: int = 30


def create_question(question_text: str, days: int) -> Question:
    """
    Create question with given text and days offset
        :param question_text:str: 
            Text of created question
        :param days:int: 
            Offset in days from now.
            Positive is future, Negative is past
    """
    time = timezone.now() + datetime.timedelta(days=days)

    return Question.objects.create(
        question_text=question_text,
        pub_date=time
    )


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        If no questions exist, an appropriate
        question message is displayed
        """
        response = self.client.get(reverse('polls:index'))

        self.assertEqual(response.status_code, HTTP_OK)
        self.assertContains(response, "No polls are avaliable.")
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            []
        )

    def test_past_question(self):
        """ Questions with pub_date in the past are displayed """
        text = "Past question."

        create_question(text, PAST_OFFSET)
        response = self.client.get(reverse('polls:index'))

        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: {}>'.format(text)]
        )

    def test_future_question(self):
        """ Questions with pub_date in the future aren't displayed."""
        create_question('Future question.', FUTURE_OFFSET)

        response = self.client.get(reverse('polls:index'))

        self.assertContains(response, "No polls are avaliable.")
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            []
        )

    def test_future_and_past_questions(self):
        """
        Even if both future and past questions exist,
        only past questions are displayed.
        """
        text: str = "Past question."

        create_question(text, PAST_OFFSET)
        create_question('Future question.', FUTURE_OFFSET)
        response = self.client.get(reverse('polls:index'))

        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: {}>'.format(text)]
        )

    def test_two_past_questions(self):
        """ Multiple questions can be displayed """
        create_question("Past one.", PAST_OFFSET)
        create_question("Past two.", PAST_OFFSET)
        response = self.client.get(reverse('polls:index'))

        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [
                '<Question: Past one.>',
                '<Question: Past two.>'
            ]
        )


class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        The detail view of a question with pub_date in the future
        must return a 404 not found.
        """
        question = create_question('Future question', FUTURE_OFFSET)

        url = reverse('polls:detail', args=(question.id,))
        response = self.client.get(url)

        self.assertEqual(response.status_code, HTTP_NOT_FOUND)

    def test_past_question(self):
        """
        The detail view of a question with pub_date in the past
        must display the question's text.
        """
        question = create_question('Past question', PAST_OFFSET)

        url = reverse('polls:detail', args=(question.id,))
        response = self.client.get(url)

        self.assertContains(response, question.question_text)


class QuesionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """
            Question.was_published_recently() returns False
            for quesions whose pub_date is in the future
        """

        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)

        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
            Question.was_published_recently() returns False
            for quesions whose pub_date is older than 1 day
        """

        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)

        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
            Question.was_published_recently() returns True
            for quesions whose pub_date is within the last day
        """

        time = timezone.now() - datetime.timedelta(hours=22)
        recent_question = Question(pub_date=time)

        self.assertIs(recent_question.was_published_recently(), True)
