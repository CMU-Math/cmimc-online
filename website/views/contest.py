from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from website.models import Contest, User, Exam, Mathlete, Team, Problem
from django.utils import timezone
from website.tasks import init_all_tasks, check_finished_games_real, final_ai_grading
from website.utils import update_contest, reset_contest, regrade_games, log, reset_exam, scores_from_csv, recompute_leaderboard, recheck_games, reset_problem, default_div1, exam_results_from_csv, calc_indiv_sweepstakes, calc_sweepstakes

@login_required
def contest_list(request):
    

    if request.method == 'POST':
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


    user = request.user
    all_contests = Contest.objects.all()
    if not user.is_tester:
        all_contests = all_contests.filter(is_private=False)     # hide private contests

    tuples = []
    for contest in all_contests:
        if user.is_mathlete:
            if user.has_team(contest):
                team = user.mathlete.get_team(contest)
                tuples.append({'contest':contest, 'has_team':True, 'team':team, 'exams': contest.reg_exams(user.mathlete), 'canjoin': contest.started})
            else:
                tuples.append({'contest':contest, 'has_team':False, 'team':None, 'exams': contest.reg_exams(user.mathlete), 'canjoin': False})
        else:
            tuples.append({'contest':contest, 'has_team':user.has_team(contest), 'team':None, 'exams': contest.exams.all(), 'canjoin': contest.started})
    
    # Categorize the contests in the tuples
    ongoing_contests = []
    for t in tuples:
        if t['contest'].ongoing:
            ongoing_contests.append(t)
    upcoming_contests = []
    for t in tuples:
        if not t['contest'].started:
            upcoming_contests.append(t)
    past_contests = []
    for t in tuples:
        if t['contest'].ended:
            past_contests.append(t)
    ongoing_contests = sorted(ongoing_contests, key=lambda d: d['contest'].start_time)
    upcoming_contests = sorted(upcoming_contests, key=lambda d: d['contest'].start_time)
    past_contests = sorted(past_contests, key=lambda d: d['contest'].end_time, reverse=True)
    
    # Get all exams
    all_exams = Exam.objects.all()
    '''
    all_emails = []
    prog_emails = []
    small_teams = []
    member_count = [0]*10
    member_count2 = [0]*10

    if user.is_staff:

        # Temporary email list (only visible to staff)
        all_users = User.objects.all()
        for user in all_users:
            all_emails.append(user.email)

        c = Contest.objects.get(pk=1) # programming contest
        teams = Team.objects.filter(contest=c)
        for team in teams:
            member_count[min(team.mathletes.all().count(), 9)] += 1
            for m in team.mathletes.all():
                prog_emails.append(m.user.email)
            if team.coach:
                prog_emails.append(team.coach.email)
            if team.mathletes.all().count() < 3:
                for m in team.mathletes.all():
                    small_teams.append(m.user.email)

        c = Contest.objects.get(pk=2) # programming contest
        teams = Team.objects.filter(contest=c)
        for team in teams:
            member_count2[min(team.mathletes.all().count(), 9)] += 1
    '''

    context = {
        'exams': all_exams,
        'ongoing': ongoing_contests,
        'upcoming': upcoming_contests,
        'past': past_contests,
    }
    # staff only
    '''
    'emaillist': ', '.join(all_emails),
    'prog_emails': ', '.join(prog_emails),
    'small_teams': ', '.join(small_teams),
    'member_count': member_count,
    'member_count2': member_count2,
    '''
    return render(request, 'contest_list.html', context)

