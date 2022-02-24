from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from website.models import Contest, User, Exam, Mathlete, Team, Problem, Competitor, Score, Submission
from django.utils import timezone
from django.http import HttpResponse
from django.conf import settings

from website.tasks import init_all_tasks, check_finished_games_real, final_ai_grading
from website.utils import update_contest, reset_contest, regrade_games, log, reset_exam, scores_from_csv, recompute_leaderboard, recheck_games, reset_problem, default_div1, exam_results_from_csv, calc_indiv_sweepstakes, calc_sweepstakes, start_round


def admin_dashboard(request):
    user = request.user
    if not user.is_staff:
        raise PermissionDenied("You do not have access to this page")

    if request.method == 'POST':
        if 'submission_csv' in request.POST:
            e = Exam.objects.get(pk=request.POST['submission_csv'])
            comps = Competitor.objects.filter(exam=e)
            content = 'Team ID,Indiv ID'
            for p in e.problems.all():
                content += f',P{p.problem_number} Answer'
            content += '\n'
            for c in comps:
                content += f'{c.team.id}'
                if not e.is_team_exam:
                    content += f',{c.mathlete.user.id}'
                for p in e.problems.all():
                    sub = Score.objects.get(problem=p, competitor=c).latest_sub
                    if sub is None:
                        content += ','
                    else:
                        content += f',{sub.text}'
                content += '\n'

            response = HttpResponse(content, content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename={0}_emails.csv'.format(e.name)
            return response

        if 'start_round' in request.POST:
            e = Exam.objects.get(pk=request.POST['start_round'])
            start_round(e)
        if 'get_contest_info' in request.POST:
            c = Contest.objects.get(pk=request.POST['get_contest_info'])
            teams = Team.objects.filter(contest=c)
            content = 'Team ID,Indiv ID,Team Name,Indiv Name,Email,Type\n'

            for team in teams:
                if team.coach:
                    content += f'{team.id},{team.coach.id},{team.team_name},{team.coach.long_name},{team.coach.email},Coach\n'
            for team in teams:
                for m in team.mathletes.all():
                    content += f'{team.id},{m.user.id},{team.team_name},{m.user.long_name},{m.user.email},Contestant\n'

            '''
            coach_emails = teams.exclude(coach__isnull=True).values_list('coach__email', 'coach__full_name').distinct()
            mathlete_emails = Mathlete.objects.filter(teams__in=teams).values_list('user__email', 'user__full_name').distinct()

            team_sizes = teams.annotate(size=Count('mathletes'))
            small_teams = team_sizes.filter(size__lt=c.max_team_size)

            small_coach_emails = small_teams.exclude(coach__isnull=True).values_list('coach__email', flat=True).distinct()
            small_mathlete_emails = Mathlete.objects.filter(teams__in=small_teams).values_list('user__email', flat=True).distinct()

            #contest_emails = list(coach_emails) + list(mathlete_emails)
            contest_small_teams = list(small_coach_emails) + list(small_mathlete_emails)

            member_count = [0]*(c.max_team_size + 2)
            size_list = team_sizes.values_list('size', flat=True)
            for sz in size_list:
                member_count[min(sz, c.max_team_size + 1)] += 1
            '''

            response = HttpResponse(content, content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename={0}_emails.csv'.format(c.name)
            return response

        if 'update_contest' in request.POST:
            contest = Contest.objects.get(pk=request.POST['update_contest'])
            update_contest(contest)
        elif 'reset_contest' in request.POST:
            contest = Contest.objects.get(pk=request.POST['reset_contest'])
            reset_contest(contest)
        elif 'reset_exam' in request.POST:
            exam = Exam.objects.get(pk=request.POST['reset_exam'])
            reset_exam(exam)
        elif 'reset_problem' in request.POST:
            problem = Problem.objects.get(pk=request.POST['reset_problem'])
            reset_problem(problem)
        elif 'init_all_tasks' in request.POST:
            init_all_tasks()
        elif 'regrade_games' in request.POST:
            regrade_games()
        elif 'recheck_games' in request.POST:
            recheck_games()
        elif 'score_file' in request.FILES:
            text = request.FILES['score_file'].read().decode('utf-8')
            scores_from_csv(text)
        elif 'recompute_leaderboard' in request.POST:
            exam = Exam.objects.get(pk=request.POST['recompute_leaderboard'])
            recompute_leaderboard(exam)
        elif 'final_ai_grading' in request.POST:
            exam = Exam.objects.get(pk=request.POST['final_ai_grading'])
            final_ai_grading(exam)
        elif 'check_finished_games' in request.POST:
            check_finished_games_real()
        elif 'delete_team' in request.POST:
            team = Team.objects.get(pk=request.POST['delete_team'])
            log(deleting_team=team.team_name)
            team.delete()
            log(deleted_team='')
        elif 'default_div1' in request.POST:
            contest = Contest.objects.get(pk=request.POST['default_div1'])
            default_div1(contest)
        elif 'exam_results' in request.POST:
            exam = Exam.objects.get(pk=request.POST['exam_results'])
            text = request.FILES['csv_file'].read().decode('utf-8')
            exam_results_from_csv(exam, text)
        if 'calc_indiv_sweepstakes' in request.POST:
            contest = Contest.objects.get(pk=request.POST['calc_indiv_sweepstakes'])
            calc_indiv_sweepstakes(contest)
        if 'calc_sweepstakes' in request.POST:
            contest = Contest.objects.get(pk=request.POST['calc_sweepstakes'])
            calc_sweepstakes(contest)

    all_exams = Exam.objects.all()
    all_contests = Contest.objects.all()

    contest_ids = []
    contest_names = []
    for contest in all_contests:
        contest_ids.append(contest.id)
        contest_names.append(contest.name)


    cid = 11
    if settings.DEBUG:
        cid = 2

    all_emails = []

    member_count = [0]*10
    teams = Team.objects.filter(contest=cid) # id 11 = Math Contest 2022
    for team in teams:
        sz = team.mathletes.count()
        if sz == 0:
            log(empty_team=str(team.team_name))
        member_count[min(sz, 9)] += 1

    math_exams = []
    math_contest = Contest.objects.get(pk=cid)
    if math_contest:
        for exam in math_contest.exams.all():
            if exam.is_math:
                math_exams.append(exam)

    context = {
        'user': user,
        'contest_emails': ', '.join([]),
        'contest_small_teams': ', '.join([]),
        'member_count': member_count,
        'contest_ids_names': zip(contest_ids,contest_names),
        'math_exams': math_exams,
    }

    return render(request, 'admin/admin_dashboard.html', context)
