from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from website.models import Exam, Competitor, Submission, Score, Problem
from website.forms import ViewOnlyEditorForm
from django.core.exceptions import PermissionDenied
from sympy.parsing.latex import parse_latex
from website.utils import log
from background_task import background

@background
def autograde_one_submission(sub_id, problem_id):
    sub = Submission.objects.get(pk=sub_id)
    p = Problem.objects.get(pk=problem_id)
    try:
        expr = parse_latex(sub.text)
        ans_expr = parse_latex(p.answer)
        if expr.equals(ans_expr):
            sub.points = 1
        else:
            sub.points = 0
        sub.save()
    except Exception as e:
        log(error=str(e), during='autograde_one_submission', sub_id=sub_id, prob=p.problem_number, sub_text=sub.text)


def autograde_submissions(exam):
    problems = exam.problem_list
    for c in exam.competitors.all():
        for p in problems:
            s = Score.objects.get(problem=p, competitor=c)
            sub = s.latest_sub
            if sub is not None and sub.points is None:
                autograde_one_submission(sub.id, p.id)


@login_required
def admin_all_submissions(request, exam_id):
    user = request.user
    exam = get_object_or_404(Exam, pk=exam_id)
    if not user.is_staff:
        raise PermissionDenied("You do not have access to this page")

    if request.POST:
        if 'grade' in request.POST:
            autograde_submissions(exam)
            return redirect('admin_all_submissions', exam_id=exam.id)
        elif 'reset_problem' in request.POST:
            p = Problem.objects.get(exam=exam, problem_number=int(request.POST['reset_problem']))
            for c in exam.competitors.all():
                s = Score.objects.get(problem=p, competitor=c)
                sub = s.latest_sub
                if sub is not None:
                    sub.points = None
                    sub.save()

    num_comp = 0
    num_solves = [0]*15
    problems = exam.problem_list
    rows = []
    for c in exam.competitors.all():
        subs = []
        for p in problems:
            s = Score.objects.get(problem=p, competitor=c)
            sub = s.latest_sub
            if sub is not None:
                url = reverse('admin:website_submission_change', args=(sub.id,))
                url = request.build_absolute_uri(url)
                if sub.points is not None:
                    num_solves[p.problem_number-1] += sub.points
            else:
                url = None
            subs.append({'sub': sub, 'url': url})
        rows.append({
            'name': c.name,
            'subs': subs,
        })
        if c.password == exam.password:
            num_comp += 1

    context = {
        'rows': rows,
        'exam': exam,
        'problems': problems,
        'num_comp': num_comp,
        'num_solves': num_solves,
    }
    return render(request, 'submission/admin_all_submissions.html', context)

@login_required
def all_submissions(request, exam_id):
    user = request.user
    exam = get_object_or_404(Exam, pk=exam_id)
    if not user.can_view_exam(exam):
        raise PermissionDenied("You do not have access to view these submissions")

    submissions = []
    if user.is_mathlete:
        competitor = Competitor.objects.getCompetitor(exam, user.mathlete)
        submissions = Submission.objects.filter(competitor=competitor).order_by('-submit_time')

    context = {
        'exam': exam,
        'submissions': submissions,
    }
    return render(request, 'submission/all_submissions.html', context)

@login_required
def view_submission(request, submission_id):
    user = request.user
    submission = get_object_or_404(Submission, pk=submission_id)
    if not user.can_view_submission(submission):
        raise PermissionDenied("You do not have access to this submission")
    exam = submission.problem.exam

    if exam.is_optimization:
        context = {
            'submission': submission,
            'exam': exam,
        }
        return render(request, 'submission/view_submission_opt.html', context)
    elif exam.is_ai:
        form = ViewOnlyEditorForm({'text': submission.text})
        context = {
            'submission': submission, 
            'form': form,
            'exam': exam,
        }
        return render(request, 'submission/view_submission_ai.html', context)
    else:
        return HttpResponse('Error: Only optimization and AI rounds are supported right now')


