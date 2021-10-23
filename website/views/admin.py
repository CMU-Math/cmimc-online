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


    context = {

    }
    return render(request, 'admin/admin_dashboard.html', context)