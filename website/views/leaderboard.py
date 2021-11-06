from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from website.models import Contest, Exam, Problem, Score, Competitor, TaskScore, Task, MiniRoundTotal, MiniRoundScore
from website.utils import log, per_page
from django.core.paginator import Paginator 
from django.db.models import F
from django.db.models.expressions import Window
from django.db.models.functions import Rank, RowNumber
from website.utils import log


# No longer used
def ai_leaderboard(request, exam):
    user = request.user
    problems = exam.problem_list
    m = exam.display_miniround
    mrts = MiniRoundTotal.objects.filter(competitor__exam=exam, miniround=m).order_by('-total_score')

    rows = []
    for mrt in mrts:
        c = mrt.competitor
        scores = []
        for p in problems:
            s = Score.objects.get(problem=p, competitor=c)
            mrs = MiniRoundScore.objects.get(score=s, miniround=m)
            scores.append(f'{mrs.weighted_avg:.2f}')

        rows.append({
            "name": c.name,
            "scores": scores,
            "total_score": f'{mrt.total_score:.2f}',
            "rank": mrts.filter(total_score__gt=mrt.total_score).count() + 1,
            "highlight": user.in_team(c.team),
        })

    context = {
        'rows': rows,
        'problems': problems,
        'exam': exam,
    }
    return render(request, 'exam/ai_leaderboard.html', context)




@login_required
def leaderboard(request, exam_id):
    # Authentication
    user = request.user
    exam = get_object_or_404(Exam, pk=exam_id)
    # log(user=str(user), exam=exam_id, end=exam.ended, can_view=user.can_view_exam(exam), cvl=user.can_view_leaderboard(exam))
    if not user.can_view_leaderboard(exam):
        raise PermissionDenied("You do not have permission to view the "
                               "leaderboard for this exam")

#    if exam.is_ai:
#        return ai_leaderboard(request, exam)

    problems = exam.problem_list
    comps = exam.competitors.annotate(
        rank=Window(
            expression=Rank(),
            order_by=F('total_score').desc()
        ),
    ).order_by('-total_score')

    items_per_page = per_page(comps.count())
    if user.is_mathlete: # should be: if user is participating mathlete, because leaderboard can be viewed by non-participants after the contest ends
        comp = user.rel_comps(exam).first() # replace with participating comp
        # maybe break ties by time so we can just use score__lte to get rank?
        for i, c in enumerate(comps):
            if c.id == comp.id:
                default_page = i // items_per_page + 1
                break
    else:
        default_page = 1
    paginator = Paginator(comps, items_per_page)
    page_number = request.GET.get('page', default=default_page)
    page_obj = paginator.get_page(page_number)

    context = {
        'problems': problems,
        'exam': exam,
        'page_obj': page_obj,
        'rel_comps': user.rel_comps(exam),
        'all_pages': [paginator.page(i) for i in paginator.page_range]
    }
    return render(request, 'exam/leaderboard.html', context)

@login_required
def problem_leaderboard(request, exam_id, problem_number):
    # Authentication
    user = request.user
    exam = get_object_or_404(Exam, pk=exam_id)
    problem = get_object_or_404(Problem, exam=exam, problem_number=problem_number)

    tasks = problem.tasks.order_by('task_number')
    scores = problem.scores.order_by('-points')

    items_per_page = per_page(scores.count())
    if user.is_mathlete:
        comp = user.rel_comps(exam).first()
        # maybe break ties by time so we can just use score__lte to get rank?
        for i, s in enumerate(scores):
            if s.competitor == comp:
                default_page = i // items_per_page + 1
                break
    else:
        default_page = 1
    paginator = Paginator(scores, items_per_page)
    page_number = request.GET.get('page', default=default_page)
    page_obj = paginator.get_page(page_number)

    context = {
        'problem': problem,
        'tasks': tasks,
        'exam': exam,
        'problems': exam.problems.order_by('problem_number'),
        'page_obj': page_obj,
        'rel_comps': user.rel_comps(exam),
        'all_pages': [paginator.page(i) for i in paginator.page_range]
    }
    return render(request, 'exam/problem_leaderboard.html', context)


def contest_leaderboard(request, contest_id):
    try:
        user = request.user
        contest = get_object_or_404(Contest, pk=contest_id)
        teams = contest.teams.all()
        exams = list(contest.exams.all())
        max_scores = [0]*len(exams)
        for i in range(len(exams)):
            if not (exams[i].is_optimization or exams[i].is_ai):
                continue
            for t in teams:
                try:
                    c = Competitor.objects.get(exam=exams[i], team=t, mathlete=None)
                    max_scores[i] = max(max_scores[i], c.total_score)
                except Exception as e:
                    log(error=str(e), during='contest_leaderboard view', team=t.team_name, exam=exams[i].name)

        rows = []
        for t in teams:
            scores = []
            for i in range(len(exams)):
                if not (exams[i].is_optimization or exams[i].is_ai):
                    continue
                try:
                    c = Competitor.objects.get(exam=exams[i], team=t, mathlete=None)
                    if max_scores[i] > 0:
                        norm_score = c.total_score / max_scores[i] * 300
                    else:
                        norm_score = 0
                    scores.append(norm_score)
                except:
                    log(error='Competitor not found', exam=exams[i].name, team=t.team_name, contest=contest.name)
            rows.append({'scores': scores, 'name': t.team_name, 'total': sum(scores)})
        rows = sorted(rows, key=lambda d: d['total'], reverse=True)

        rows[0]['rank'] = 1
        for i in range(1, len(rows)):
            if rows[i]['total'] == rows[i-1]['total']:
                rows[i]['rank'] = rows[i-1]['rank']
            else:
                rows[i]['rank'] = i+1

        context = {
            'contest': contest,
            'exams': exams,
            'rows': rows,
        }
        return render(request, 'contest_leaderboard.html', context)
    except Exception as e:
        log(error=str(e), during='contest_leaderboard view')
