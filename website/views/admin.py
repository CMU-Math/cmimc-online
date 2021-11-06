from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from website.models import Contest, User, Exam, Mathlete, Team, Problem
from django.utils import timezone
from website.tasks import init_all_tasks, check_finished_games_real, final_ai_grading
from website.utils import update_contest, reset_contest, regrade_games, log, reset_exam, scores_from_csv, recompute_leaderboard, recheck_games, reset_problem, default_div1, exam_results_from_csv, calc_indiv_sweepstakes, calc_sweepstakes

def admin_dashboard(request):
    user = request.user
    
    if request.method == 'POST':
        if 'get_contest_info' in request.POST:
            c = Contest.objects.get(pk=request.POST['get_contest_info'])
            teams = Team.objects.filter(contest=c)

            coach_emails = teams.exclude(coach__isnull=True).values_list('coach__email', flat=True).distinct()
            mathlete_emails = Mathlete.objects.filter(teams__in=teams).values_list('user__email', flat=True).distinct()

            team_sizes = teams.annotate(size=Count('mathletes'))
            small_teams = team_sizes.filter(size__lt=c.max_team_size)

            small_coach_emails = small_teams.exclude(coach__isnull=True).values_list('coach__email', flat=True).distinct()
            small_mathlete_emails = Mathlete.objects.filter(teams__in=small_teams).values_list('user__email', flat=True).distinct()

            contest_emails = list(coach_emails) + list(mathlete_emails)
            contest_small_teams = list(small_coach_emails) + list(small_mathlete_emails)

            member_count = [0]*(c.max_team_size + 2)
            size_list = team_sizes.values_list('size', flat=True)
            for sz in size_list:
                member_count[min(sz, c.max_team_size + 1)] += 1

            context = {
                'user': user,
                'contest_emails': ', '.join(contest_emails),
                'contest_small_teams': ', '.join(contest_small_teams),
                'member_count': member_count,
            }    


            return render(request, 'admin/admin_dashboard.html', context)

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

    if not user.is_staff:
        raise PermissionDenied("You do not have access to this page")

    all_exams = Exam.objects.all()
    all_contests = Contest.objects.all()

    for contest in all_contests:
        print(contest.id)
        print(contest.name)

    
    all_emails = []

    member_count2 = [0]*10

    # if user.is_staff:

        # Temporary email list (only visible to staff)
        # all_users = User.objects.all()
        # for curr_user in all_users:
        #     all_emails.append(curr_user.email)

        


        # c = Contest.objects.get(pk=2) # math contest
        # teams = Team.objects.filter(contest=c)
        # counter = 0
        # team_len = len(teams)
        # for team in teams:
        #     counter += 1
        #     if(counter > 10):
        #         break
        #     member_count2[min(team.mathletes.all().count(), 9)] += 1
    
    context = {
        'user': user,
        'contest_emails': ', '.join([]),
        'contest_small_teams': ', '.join([]),
        'member_count': [],
    }  

    return render(request, 'admin/admin_dashboard.html', context)
