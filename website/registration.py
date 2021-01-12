from website.models import Competitor

# Creates Competitors for this exam
def register_team(team):
    # TODO: check if this is during the contest registration period
    assert(not team.is_finalized)
    size = team.mathletes.count()
    assert(size >= team.contest.min_team_size and size <= team.contest.max_team_size)
    for exam in team.contest.exams.all():
        # TODO: check if Competitor already exists
        if exam.is_team_exam:
            c = Competitor(exam=exam, team=team, mathlete=None)
            c.save()
        else:
            for m in team.mathletes.all():
                c = Competitor(exam=exam, team=team, mathlete=m)
                c.save()
    team.is_finalized = True
    team.save()


def unregister_team(team):
    assert(team.is_finalized)
    for c in team.competitors.all():
        c.delete()
    team.is_finalized = False
    team.save()


def register_all_teams(contest):
    # TODO: check if this is during the contest registration period
    for team in contest.teams.all():
        register_team(team)

