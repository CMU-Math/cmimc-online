from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.utils import timezone
from website.models import Exam, Problem, Task, Competitor, Submission, Score
from website.forms import EditorForm
from website.tasks import async_grade
from website.tasks import schedule_burst

@login_required
def submit(request, exam_id, problem_number, task_number=None):
    user = request.user
    exam = get_object_or_404(Exam, pk=exam_id)
    if not user.can_view_exam(exam):
        raise PermissionDenied("You must be registered for the contest to access \
                the submission page")

    problem = get_object_or_404(Problem, exam=exam, problem_number=problem_number)
    task = Task.objects.filter(problem=problem, task_number=task_number).first()

    if request.method == 'POST':
        if not user.can_submit(exam):
            raise PermissionDenied("You are not allowed to submit to this problem")
        return make_submission(request, exam, problem, task)
    else: # request.method == 'GET'
        return show_form(request, exam, problem, task)


@login_required
def resubmit(request, submission_id):
    user = request.user
    submission = get_object_or_404(Submission, pk=submission_id)
    if not user.can_view_submission(submission):
        raise PermissionDenied("You do not have access to this submission")
    problem = submission.problem
    exam = problem.exam
    task = submission.task

    if request.method == 'POST':
        return make_submission(request, exam, problem, task)
    else: # request.method == 'GET'
        text = submission.text
        return show_form(request, exam, problem, task, text)


def make_submission(request, exam, problem, task=None):
    user = request.user
    competitor = Competitor.objects.getCompetitor(exam, user.mathlete)
    # get text
    if 'codeFile' in request.FILES:
        try:
            text = request.FILES['codeFile'].read().decode('ascii')
        except:
            # Error while reading file
            submission = Submission(
                problem=problem,
                competitor=competitor,
                text='',
                task=task,
                status=4,
                error_msg='Your uploaded file could not be read',
            )
            submission.save()
            return redirect('view_submission', submission_id=submission.id)
    else:
        if exam.is_optimization:
            text = request.POST['codeText']
        elif exam.is_ai:
            form = EditorForm(request.POST)
            text = form['text'].value()
        else:
            return HttpResponse('Error: Only optimization and AI rounds are supported right now')
    # create and save submission

    submission = Submission(
        problem=problem,
        competitor=competitor,
        text=text,
        task=task,
    )
    submission.save()
    if exam.is_ai:
        schedule_burst(submission)
    # grade the new submission
    # async_grade(submission.id)
    '''
    delayed = timezone.now() + timedelta(minutes=5)
    if delayed > exam.end_time:
        async_grade(submission.id, schedule=delayed)
    else:
        async_grade(submission.id)
    '''
    return redirect('view_submission', submission_id=submission.id)


def show_form(request, exam, problem, task, text=''):
    if exam.is_optimization:
        context = {
            'problem': problem,
            'task': task,
            'text': text,
        }
        return render(request, 'submit/submit_opt.html', context)
    elif exam.is_ai:
        form = EditorForm({'text': text})
        context = {
            'problem': problem,
            'form': form,
        }
        return render(request, 'submit/submit_ai.html', context)
    else:
        return HttpResponse('Error: Only optimization and AI rounds are supported right now')


