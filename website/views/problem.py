from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from website.models import Exam, Problem, Task, Competitor, Score
from django.http import HttpResponse

@login_required
def view_problem(request, exam_id, problem_number):
    user = request.user
    exam = get_object_or_404(Exam, pk=exam_id)
    if not user.can_view_exam(exam):
        raise PermissionDenied("You must be registered for the contest to see \
                the problems")

    problem = get_object_or_404(Problem, exam=exam, problem_number=problem_number)

    # TODO: needs to work for coaches too (except they can't submit)
    if user.is_mathlete:
        mathlete = user.mathlete
        competitor = Competitor.objects.getCompetitor(exam, mathlete)
        score = Score.objects.get(problem=problem, competitor=competitor)
        context = {
            'problem': problem,
            'score': score,
            'exam': exam,
            'aiprob': problem.aiproblem.first(),
        }
        return render(request, 'exam/view_problem.html', context)


