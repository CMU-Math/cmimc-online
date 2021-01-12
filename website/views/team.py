from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from website.models import Contest, Team

# TODO: handle error when user submits a duplicate team name
# TODO: check registration period to see if new teams can still be made
@login_required
def new_team(request, contest_id):
    user = request.user
    contest = get_object_or_404(Contest, pk=contest_id)
    if user.is_mathlete:
        mathlete = user.mathlete
        if user.has_team(contest):
            team = mathlete.get_team(contest)
            return redirect('team_info', team_id=team.id)
        elif request.method == 'GET':
            return render(request, 'team/new_team.html')
        else:
            team = Team.create(contest=contest, team_name=request.POST['teamName'], coach=None)
            team.save()
            team.mathletes.add(mathlete)
            return redirect('team_info', team_id=team.id)
    elif user.is_coach:
        if request.method == 'GET':
            return render(request, 'team/new_team.html')
        else:
            team = Team.create(contest=contest, team_name=request.POST['teamName'], coach=user)
            team.save()
            return redirect('team_info', team_id=team.id)


# TODO: prevent joining after team is registered
@login_required
def join_team(request, team_id, invite_code):
    user = request.user
    team = get_object_or_404(Team, pk=team_id, invite_code=invite_code)
    contest = team.contest
    if user.is_mathlete:
        mathlete = user.mathlete
        if user.has_team(contest):
            real_team = mathlete.get_team(contest)
            return redirect('team_info', team_id=real_team.id)
        elif team.is_finalized:
            return redirect('contest_list')
        else:
            team.mathletes.add(mathlete)
            return redirect('team_info', team_id=team.id)


@login_required
def team_info(request, team_id):
    user = request.user
    team = get_object_or_404(Team, pk=team_id)
    if not team.can_see_info(user):
        return redirect('contest_list')

    if request.method == 'POST':
        if request.POST['submit'] == 'leaveTeam' and user.is_mathlete and not team.is_finalized:
            mathlete = user.mathlete
            team.mathletes.remove(mathlete)
            return redirect('contest_list')
        elif request.POST['submit'] == 'deleteTeam' and (user.is_coach or user.is_staff):
            team.delete()
            return redirect('contest_list')
        elif request.POST['submit'] == 'register':
            team.register()

    context = {
        'team': team,
        'invite_link': request.build_absolute_uri(
            reverse('join_team', args=[team_id, team.invite_code])
        ),
        'too_large': len(team.mathletes.all()) > team.contest.max_team_size,
        'reg_permission': user != team.coach,
    }
    return render(request, 'team/team.html', context)


@login_required
def coach_teams(request, contest_id):
    user = request.user
    contest = get_object_or_404(Contest, pk=contest_id)
    if not user.is_coach:
        return redirect('home')

    teams = Team.objects.filter(contest=contest, coach=user)
    context = {
        'teams': teams,
        'contest': contest,
    }
    return render(request, 'team/coach_teams.html', context)

def finalize_all_teams(request, contest_id):
    contest = get_object_or_404(Contest, pk=contest_id)
    teams = Team.objects.filter(contest=contest)
    for team in teams:
        team.register()


