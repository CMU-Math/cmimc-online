from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from website.models import Contest, User, Exam, Mathlete, Team, Problem
from django.utils import timezone
from website.tasks import init_all_tasks, check_finished_games_real, final_ai_grading
from website.utils import update_contest, reset_contest, regrade_games, log, reset_exam, scores_from_csv, recompute_leaderboard, recheck_games, reset_problem, default_div1, exam_results_from_csv, calc_indiv_sweepstakes, calc_sweepstakes


def admin_dashboard(request):
    user = request.user
    
    if not user.is_staff:
        raise PermissionDenied("You do not have access to this page")

    all_exams = Exam.objects.all()
    
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
    


    context = {
        'emaillist': ', '.join(all_emails),
        'prog_emails': ', '.join(prog_emails),
        'small_teams': ', '.join(small_teams),
        'member_count': member_count,
        'member_count2': member_count2,
    }
    return render(request, 'admin/admin_dashboard.html', context)