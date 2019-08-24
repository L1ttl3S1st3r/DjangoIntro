from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic
from django.utils import timezone


from .models import Question, Choice


# Main View
class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
            Return the last five published questions.
            Exclude future questions.
        """
        return Question.objects.filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')[:5]


# Question Detail View
class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """ Excludes any future question """
        return Question.objects.filter(pub_date__lte=timezone.now())


# Question Results View
class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'


# Vote Command View
def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    # Handle if any choice isn't selected
    except (KeyError, Choice.DoesNotExist):
        return render(
            request,
            'polls/detail.html',
            {
                'question': question,
                'error_message': 'You did not select a choice.'
            }
        )
    else:
        selected_choice.votes += 1
        selected_choice.save()
        return HttpResponseRedirect(
            reverse(
                'polls:results', args=(question_id,)
            )
        )
