from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from website.models import Contest, Team, Mathlete, DivChoice
from website.utils import update_competitors

# TODO: handle error when user submits a duplicate team name
# TODO: check registration period to see if new teams can still be made
@login_required
def new_team(request, contest_id):
    user = request.user
    contest = get_object_or_404(Contest, pk=contest_id)
    if not user.can_create_team(contest):
        raise PermissionDenied("You are not allowed to create a team for this contest")

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
            update_competitors(team)
            return redirect('team_info', team_id=team.id)
    elif user.is_coach:
        if request.method == 'GET':
            return render(request, 'team/new_team.html')
        else:
            team = Team.create(contest=contest, team_name=request.POST['teamName'], coach=user)
            team.save()
            update_competitors(team)
            return redirect('team_info', team_id=team.id)


# TODO: prevent joining after team is registered
@login_required
def join_team(request, team_id, invite_code):
    user = request.user
    team = get_object_or_404(Team, pk=team_id, invite_code=invite_code)
    contest = team.contest
    # TODO: handle errors like when a coach uses invite link, or team is full, or team is finalized

    if user.is_mathlete:
        mathlete = user.mathlete
        if user.has_team(contest):
            real_team = mathlete.get_team(contest)
            return redirect('team_info', team_id=real_team.id)
        elif team.is_finalized:
            return redirect('contest_list')
        else:
            team.mathletes.add(mathlete)
            update_competitors(team)
            return redirect('team_info', team_id=team.id)
    else:
        # temporary fix so that coaches don't see "Server Error 500"
        return redirect('team_info', team_id=team.id)


@login_required
def team_info(request, team_id):
    user = request.user
    team = get_object_or_404(Team, pk=team_id)
    if not user.can_view_team(team):
        return redirect('contest_list')

    can_edit = user.can_edit_team(team)
    exampairs = team.contest.exampairs.all()

    if request.method == 'POST':
        if 'save' in request.POST:
            for m in team.mathletes.all():
                for pair in exampairs:
                    dc = DivChoice.objects.get(exampair=pair, mathlete=m)
                    ID = f'divchoice-{dc.id}'
                    if ID in request.POST:
                        dc.division = request.POST[ID]
                        dc.save()
            if 'merge' in request.POST:
                team.wants_merge = True
                team.save()
            else:
                team.wants_merge = False
                team.save()
            return redirect('team_info', team_id=team_id)

        elif 'deleteTeam' in request.POST and can_edit:
            team.delete() # cascade deletes for comps, scores, taskscores, MRscores
            return redirect('contest_list')
        elif 'removeMember' in request.POST:
            mathlete_id = request.POST['removeMember']
            ml = Mathlete.objects.get(pk=mathlete_id)
            team.mathletes.remove(ml)
            if team.mathletes.count() == 0 and team.coach == None:
                team.delete()
            else:
                update_competitors(team)
            if user == ml.user: # removed yourself from the team
                return redirect('contest_list')
            return redirect('team_info', team_id=team_id)

    rows = []
    for m in team.mathletes.all():
        row = []
        for pair in exampairs:
            dc = DivChoice.objects.filter(exampair=pair, mathlete=m).first() # TODO: update comps
            if dc is None:
                dc = DivChoice(exampair=pair, mathlete=m)
                dc.save()
            row.append(dc)
        rows.append({
            'mathlete': m,
            'divchoices': row,
        })

    context = {
        'team': team,
        'invite_link': request.build_absolute_uri(
            reverse('join_team', args=[team_id, team.invite_code])
        ),
        'too_large': len(team.mathletes.all()) > team.contest.max_team_size,
        'too_small': len(team.mathletes.all()) < team.contest.max_team_size,
        'reg_permission': user != team.coach,
        'can_edit': can_edit,
        'exampairs': exampairs,
        'rows': rows,
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


