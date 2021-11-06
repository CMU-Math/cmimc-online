from django.shortcuts import render, get_object_or_404
from website.models import Contest, Exam, Problem, Score, Competitor, DivChoice, IndivSweepstake, Sweepstake
from website.utils import log, per_page
from django.core.exceptions import PermissionDenied


def exam_results(request, exam_id):
    user = request.user
    exam = get_object_or_404(Exam, pk=exam_id)
    if not exam.show_results:
        raise PermissionDenied("These results have not been made public")
    problems = exam.problem_list

    comps = exam.competitors
    if exam.is_team_exam:
        comps = comps.order_by('-total_score', 'team__team_name')
    else:
        comps = comps.order_by('-total_score', 'mathlete__user__first_name', 'mathlete__user__last_name')

    rel_rows = []
    if user.is_authenticated:
        rel_comps = user.rel_comps(exam)
        for c in rel_comps:
            scores = []
            for p in problems:
                s = Score.objects.get(problem=p, competitor=c)
                scores.append(s.points)

            rel_rows.append({
                "comp": c,
                "scores": scores,
                "rank": comps.filter(total_score__gt=c.total_score).count() + 1,
            })

    cutoff_idx = min(comps.count()-1, 49)
    cutoff = comps.only('total_score')[cutoff_idx].total_score
    log(exam=str(exam), cutoff=cutoff)
    all_comps = comps.filter(total_score__gte=cutoff)
    all_rows = []
    for c in all_comps:
        scores = []
        for p in problems:
            s = Score.objects.get(problem=p, competitor=c)
            scores.append(s.points)

        all_rows.append({
            "comp": c,
            "scores": scores,
        })

    all_rows[0]['rank'] = 1
    for i in range(1, len(all_rows)):
        if all_rows[i]['comp'].total_score == all_rows[i-1]['comp'].total_score:
            all_rows[i]['rank'] = all_rows[i-1]['rank']
        else:
            all_rows[i]['rank'] = i+1

    context = {
        'all_rows': all_rows,
        'rel_rows': rel_rows,
        'problems': problems,
        'exam': exam,
        'contest': exam.contest,
    }
    return render(request, 'results/exam_results.html', context)


def indiv_sweepstakes(request, contest_id):
    user = request.user
    contest = get_object_or_404(Contest, pk=contest_id)
    if not contest.show_sweepstakes:
        raise PermissionDenied("These results have not been made public")
    try:
        exampairs = contest.exampairs.all()
        indivsweeps = IndivSweepstake.objects.filter(team__contest=contest).order_by('-total_score', 'mathlete__user__first_name', 'mathlete__user__last_name')

        rel_rows = []
        if user.is_authenticated:
            rel_teams = user.rel_teams(contest)
            for team in rel_teams:
                for m in team.mathletes.all():
                    scores = []
                    for ep in exampairs:
                        dc = DivChoice.objects.get(exampair=ep, mathlete=m)
                        for exam in ep.exams.all():
                            if exam.division == dc.division:
                                c = Competitor.objects.getCompetitor(exam=exam, mathlete=m)
                                scores.append(c.total_score)
                    total_score = sum(scores)
                    rel_rows.append({
                        "name": m.user.long_name,
                        "team": team,
                        "scores": scores,
                        "total_score": total_score,
                        "rank": indivsweeps.filter(total_score__gt=total_score).count() + 1,
                    })

        cutoff_idx = min(indivsweeps.count()-1, 49)
        cutoff = indivsweeps[cutoff_idx].total_score
        indivsweeps = indivsweeps.filter(total_score__gte=cutoff)

        all_rows = []
        for iss in indivsweeps:
            m = iss.mathlete
            scores = []
            for ep in exampairs:
                dc = DivChoice.objects.get(exampair=ep, mathlete=m)
                for exam in ep.exams.all():
                    if exam.division == dc.division:
                        c = Competitor.objects.getCompetitor(exam=exam, mathlete=m)
                        scores.append(c.total_score)

            all_rows.append({
                "name": m.user.name,
                "team": iss.team,
                "scores": scores,
                "total_score": iss.total_score,
            })

        all_rows[0]['rank'] = 1
        for i in range(1, len(all_rows)):
            if all_rows[i]['total_score'] == all_rows[i-1]['total_score']:
                all_rows[i]['rank'] = all_rows[i-1]['rank']
            else:
                all_rows[i]['rank'] = i+1

        context = {
            'all_rows': all_rows,
            'rel_rows': rel_rows,
            'exampairs': exampairs,
            'contest': contest,
        }
        return render(request, 'results/indiv_sweepstakes.html', context)
    except Exception as e:
        log(error=str(e), during='indiv_sweepstakes view')


def sweepstakes(request, contest_id):
    user = request.user
    contest = get_object_or_404(Contest, pk=contest_id)
    if not contest.show_sweepstakes:
        raise PermissionDenied("These results have not been made public")
    try:
        sweeps = Sweepstake.objects.filter(team__contest=contest).order_by('-total_score', 'team__team_name')

        rel_sweeps = []
        if user.is_authenticated:
            rel_teams = user.rel_teams(contest)
            for team in rel_teams:
                ss = team.sweepstake
                ss.rank = sweeps.filter(total_score__gt=ss.total_score).count() + 1
                rel_sweeps.append(ss)

        cutoff_idx = min(sweeps.count()-1, 49)
        cutoff = sweeps[cutoff_idx].total_score
        all_sweeps = list(sweeps.filter(total_score__gte=cutoff))

        all_sweeps[0].rank = 1
        for i in range(1, len(all_sweeps)):
            if all_sweeps[i].total_score == all_sweeps[i-1].total_score:
                all_sweeps[i].rank = all_sweeps[i-1].rank
            else:
                all_sweeps[i].rank = i+1

        context = {
            'all_sweeps': all_sweeps,
            'rel_sweeps': rel_sweeps,
            'contest': contest,
        }
        return render(request, 'results/sweepstakes.html', context)
    except Exception as e:
        log(error=str(e), during='sweepstakes view')


