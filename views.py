import datetime

from django.db.models import F, Q
from django.shortcuts import render, get_object_or_404, redirect 
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib import messages

from .models import Question, Choice
from .forms import QuestionForm, ChoiceForm


def index(request):
    query = request.GET.get("q")
    filter_date = request.GET.get("filter_date")
    latest_question_list = Question.objects.filter(pub_date__lte=timezone.now())

    if query:
        latest_question_list = latest_question_list.filter(
            Q(question_text__icontains=query)
        )

    if filter_date == "today":
        today = timezone.now().date()
        latest_question_list = latest_question_list.filter(pub_date__date=today)
    elif filter_date == "week":
        last_week = timezone.now() - datetime.timedelta(days=7)
        latest_question_list = latest_question_list.filter(pub_date__gte=last_week)
    elif filter_date == "month":
        now = timezone.now()
        latest_question_list = latest_question_list.filter(pub_date__year=now.year, pub_date__month=now.month)
    elif filter_date == "year":
        year = timezone.now().year
        latest_question_list = latest_question_list.filter(pub_date__year=year)

    latest_question_list = latest_question_list.order_by("-pub_date")[:5]

    return render(request, "polls/index.html", {
        "latest_question_list": latest_question_list,
        "query": query,
        "filter_date": filter_date,
    })


def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    choices = question.choice_set.all()
    form = ChoiceForm()

    if request.method == "POST":
        if "add_choice" in request.POST:
            form = ChoiceForm(request.POST)
            if form.is_valid():
                new_choice = form.save(commit=False)
                new_choice.question = question
                new_choice.save()
                messages.success(request, "Choice has been added successfully!")
                return redirect("polls:detail", question_id=question.id)

        elif "edit_choice" in request.POST:
            choice_id = request.POST.get("choice_id")
            choice = get_object_or_404(Choice, pk=choice_id)
            form = ChoiceForm(request.POST, instance=choice)
            if form.is_valid():
                form.save()
                messages.success(request, "Choice has been updated successfully!")
                return redirect("polls:detail", question_id=question.id)

        elif "delete_choice" in request.POST:
            choice_id = request.POST.get("choice_id")
            choice = get_object_or_404(Choice, pk=choice_id)
            choice.delete()
            messages.success(request, "Choice has been deleted successfully!")
            return redirect("polls:detail", question_id=question.id)

    return render(request, "polls/detail.html", {
        "question": question,
        "choices": choices,
        "form": form,
    })


class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        messages.success(request, "Your vote has been recorded!")
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))
    

def create_poll(request):
    if request.method == "POST":
        form = QuestionForm(request.POST)
        if form.is_valid():
            new_question = form.save(commit=False)
            new_question.pub_date = timezone.now()
            new_question = form.save()
            messages.success(request, "Poll has been created successfully!")
            return redirect("polls:detail", question_id=new_question.id)
    else:
        form = QuestionForm()

    return render(request, "polls/create_poll.html", {"form": form})


def edit_poll(request, pk):
    question = get_object_or_404(Question, pk=pk)
    if request.method == "POST":
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            messages.success(request, "Question has been changed successfully!")
            return redirect("polls:index")
    else:
        form = QuestionForm(instance=question)
    return render(request, "polls/edit_poll.html", {"form": form, "question": question})

def delete_poll(request, pk):
    question = get_object_or_404(Question, pk=pk)
    if request.method == "POST":
        question.delete()
        messages.success(request, "Question has been deleted successfully!") 
        return redirect("polls:index")
    return render(request, "polls/delete_poll.html", {"question": question})
