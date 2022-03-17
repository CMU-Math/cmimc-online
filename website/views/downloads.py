from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from website.models import Exam, Competitor, Submission, AISubmission, AIProblem, Contest, Score, Problem, AIVisualizer
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.views.decorators.clickjacking import xframe_options_exempt
import json

@login_required
def match_replay(request, aisubmission_id):
    user = request.user
    aisub = get_object_or_404(AISubmission, pk=aisubmission_id)
    if not user.in_team(aisub.competitor.team) and not user.is_staff:
        raise PermissionDenied("You do not have access to view this match")

    gamedata = aisub.game.history
    replay = {"seat": aisub.seat, "gamedata": gamedata}
    content = json.dumps(replay)
    return render(request, 'exam/run_visualizer.html', {
        'visualizer_data': content,
        'problem_name': aisub.game.aiproblem.problem.short_name,
    })

def local_visualizer(request):
    return render(request, 'exam/run_visualizer.html', {
        'problem': None,
    })

@login_required
def ai_starter_file(request, aiproblem_id):
    user = request.user
    aiprob = get_object_or_404(AIProblem, pk=aiproblem_id)
    problem = aiprob.problem
    exam = problem.exam
    if not user.can_view_exam(exam):
        raise PermissionDenied("You do not have access to this file")

    content = aiprob.starter_file
    response = HttpResponse(content, content_type='text/x-python')
    response['Content-Disposition'] = 'attachment; filename={0}_starter.py'.format(problem.short_name)
    return response


@xframe_options_exempt
def ai_visualizer(request, aiproblem_id):
    user = request.user
    aiprob = get_object_or_404(AIVisualizer, name=aiproblem_id)

    content = aiprob.visualizer
    response = HttpResponse(content)
    return response

@login_required
def mailinglist(request, contest_id):
    user = request.user
    c = get_object_or_404(Contest, pk=contest_id)
    if not user.is_staff:
        raise PermissionDenied("You do not have access to this file")

    emails = ['Email,Name,Team,Contestant/Coach']
    for team in c.teams.all():
        for m in team.mathletes.all():
            emails.append(f'{m.user.email},{m.user.long_name},{team.team_name},Contestant')
        #if team.coach:
        #    emails.append(f'{team.coach.email},{team.coach.long_name},{team.team_name},Coach')
    content = '\n'.join(emails)
    response = HttpResponse(content, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename={0} mailing list.csv'.format(c.name)
    return response


@login_required
def download_subs(request, exam_id):
    user = request.user
    exam = get_object_or_404(Exam, pk=exam_id)
    if not user.is_staff:
        raise PermissionDenied("You do not have access to this file")

    problems = exam.problem_list
    lines = []
    for c in exam.competitors.all():
        line = c.name
        for p in problems:
            s = Score.objects.get(problem=p, competitor=c)
            sub = s.latest_sub
            if sub is not None and sub.points == 1:
                line += ',1,'
            else:
                line += ',0,'
            if sub is not None:
                line += sub.text
        line += ',' + c.team.team_name
        lines.append(line)

    content = '\n'.join(lines)
    response = HttpResponse(content, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename={0} scores.csv'.format(exam.name)
    return response


