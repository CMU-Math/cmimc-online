from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from website import views
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url, include

urlpatterns = [
    path('', views.home, name='home'),
    path('contests', views.contest_list, name='contest_list'),
    path('math/format', views.math_info, name='math_info'),
    path('math/rules', views.math_rules, name='math_rules'),
    path('math/sample-problems', views.math_sample_problems, name='math_sample_problems'),
    path('math/schedule', views.math_schedule, name='math_schedule'),
    path('math/mini-events', views.math_mini_events, name='math_mini_events'),
    path('programming/format', views.prog_info, name='prog_info'),
    path('programming/sample-problems', views.prog_sample_problems, name='prog_sample_problems'),
    path('programming/schedule', views.prog_schedule, name='prog_schedule'),
    path('programming/mini-events', views.prog_mini_events, name='prog_mini_events'),
    path('programming/resources', views.resources, name='resources'),
    path('registration', views.reg_info, name='reg_info'),
    path('faq', views.faq, name='faq'),
    path('programming/updates', views.updates, name='updates'),

    path('admin', admin.site.urls),

    path('signup', views.signup, name='signup'),
    path('accounts/', include('django.contrib.auth.urls')),

    path('terms_and_conditions', views.terms_and_conditions, name='terms_and_conditions'),

    path('contest/<int:contest_id>/newteam', views.new_team, name='new_team'),
    path('team/<int:team_id>', views.team_info, name='team_info'),
    path('team/<int:team_id>/join/<str:invite_code>', views.join_team, name='join_team'),
    path('contest/<int:contest_id>/myteams', views.coach_teams, name='coach_teams'),

    path('exam/<int:exam_id>', views.all_problems, name='all_problems'),
    path('exam/<int:exam_id>/leaderboard', views.leaderboard, name='leaderboard'),
    path('contest/<int:contest_id>/leaderboard', views.contest_leaderboard, name='contest_leaderboard'),
    path('exam/<int:exam_id>/leaderboard/<int:problem_number>', views.problem_leaderboard, name='problem_leaderboard'),
    path('exam/<int:exam_id>/miniround-scores', views.miniround_scores, name='miniround_scores'),
    path('exam/<int:exam_id>/matches/<int:problem_number>', views.match_results, name='match_results'),
    path('exam/<int:exam_id>/problem/<int:problem_number>', views.view_problem, name='view_problem'),
    path('exam/<int:exam_id>/problem/<int:problem_number>/submit', views.submit, name='submit'),
    path('exam/<int:exam_id>/problem/<int:problem_number>/submit/task/<int:task_number>', views.submit, name='submit'),

    path('exam/<int:exam_id>/submissions', views.all_submissions, name='all_submissions'),
    path('exam/<int:exam_id>/admin-all-submissions', views.admin_all_submissions, name='admin_all_submissions'),
    path('submission/<int:submission_id>', views.view_submission, name='view_submission'),
    path('resubmit/<int:submission_id>', views.resubmit, name='resubmit'),

    path('results/contest/<int:contest_id>/sweepstakes', views.sweepstakes, name='sweepstakes'),
    path('results/contest/<int:contest_id>/indiv-sweepstakes', views.indiv_sweepstakes, name='indiv_sweepstakes'),
    path('results/exam/<int:exam_id>', views.exam_results, name='exam_results'),

    path('download/match/<int:aisubmission_id>', views.match_replay, name='match_replay'),
    path('download/starter-file/<int:aiproblem_id>', views.ai_starter_file, name='ai_starter_file'),
    path('download/visualizer/<int:aiproblem_id>', views.ai_visualizer, name='ai_visualizer'),
    path('download/mailinglist/<int:contest_id>', views.mailinglist, name='mailinglist'),
    path('download/subs/<int:exam_id>', views.download_subs, name='download_subs'),
]
