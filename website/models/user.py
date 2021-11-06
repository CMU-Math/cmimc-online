from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from website.managers import UserManager

class User(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), blank=True, max_length=150)
    last_name = models.CharField(_('last name'), blank=True, max_length=150)
    full_name = models.CharField(max_length=100, blank=True, help_text=_('full name'))
    alias = models.CharField(max_length=100, blank=True, help_text=_('preferred name'))
    is_tester = models.BooleanField(default=False, help_text=_('whether they can view private contests'))

    MATHLETE = 'ML'
    STAFF = 'ST'
    COACH = 'CO'
    role_CHOICES = [
        (STAFF, 'CMU Student'),
        (MATHLETE, 'Contestant'),
        (COACH, 'Coach'),
    ]
    role = models.CharField(max_length=2, choices=role_CHOICES, default=MATHLETE)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    def __str__(self):
        return self.name

    @property
    def short_name(self):
        if self.first_name:
            return self.first_name
        else:
            return self.name

    @property
    def long_name(self): # full_name already taken
        if self.first_name and self.last_name:
            return '{0} {1}'.format(self.first_name, self.last_name)
        elif self.full_name:
            return self.full_name
        elif self.first_name:
            return self.first_name
        else:
            return self.last_name

    @property
    def name(self):
        return self.long_name

    @property
    def is_mathlete(self):
        return self.role == self.MATHLETE

    @property
    def is_coach(self):
        return self.role == self.COACH

    def has_team(self, contest):
        if self.is_mathlete:
            return self.mathlete.teams.filter(contest=contest).exists()
        elif self.is_coach:
            return self.teams.filter(contest=contest).exists()
        else: # staff
            return False

    def in_team(self, team):
        if self.is_mathlete:
            return self.mathlete in team.mathletes.all()
        elif self.is_coach:
            return self == team.coach
        else: # staff
            return False

    # TODO: update for coaches
    # whether the user is registered for this contest
    # Do we need both is_registered and has_team?
    def is_registered(self, contest):
        if not self.is_authenticated:
            return False
        if not self.is_mathlete:
            return False
        return self.has_team(contest)

    def can_edit_team(self, team):
        if self.is_staff:
            return True
        if self.is_coach:
            if self == team.coach and not team.is_finalized:
                return True
        if self.is_mathlete:
            if team.coach == None and team in self.mathlete.teams.all() and not team.is_finalized:
                return True
        return False

    # whether the user is currently doing the exam
    # TODO: check if this is actually used
    def is_in_exam(self, exam):
        return exam.ongoing and self.is_registered(exam.contest)

    # whether the user can view the exam pages, which includes:
    # 1. all problems page
    # 2. individual problem pages
    # 3. all submissions page
    # 4. individual submission pages (only when the submission belongs to them)
    # 5. leaderboard (only when the leaderboard is meant to be public)
    # 6. problem submit pages (only permission to view the page, not to submit)
    def can_view_exam(self, exam):
        if self.is_staff:
            return True
        if exam.ended:
            return True     # anyone can view a past contest
        if exam.ongoing and self.has_team(exam.contest):
            return True     # you need to be registered for an ongoing contest
        return False

    def can_view_leaderboard(self, exam):
        if self.is_staff:
            return True
        if self.can_view_exam(exam) and exam.show_leaderboard:
            return True
        return False

    def can_submit(self, exam):
        if self.is_mathlete:
            if exam.ongoing and self.is_registered(exam.contest):
                return True
        return False

    def can_view_submission(self, submission):
        from website.models import Competitor
        if self.is_staff:
            return True
        if self.is_coach and self == submission.competitor.team.coach:
            return True
        if self.is_mathlete:
            comp = Competitor.objects.getCompetitor(submission.problem.exam, self.mathlete)
            if comp == submission.competitor:
                return True
        return False

    def can_create_team(self, contest):
        if self.is_staff:
            return False
        if contest.locked:
            return False
        if contest.is_private and not self.is_tester:
            return False
        return True

    # whether the user has access to the team info page
    def can_view_team(self, team):
        if self.is_staff:
            return True
        if self.is_mathlete and team.has_member(self):
            return True
        if self.is_coach and self == team.coach:
            return True
        return False

    # list of teams that this user is part of
    def rel_teams(self, contest):
        from website.models import Team
        if self.is_staff:
            return Team.objects.none()
        if self.is_mathlete:
            return self.mathlete.teams.filter(contest=contest)
        if self.is_coach:
            return self.teams.filter(contest=contest)


    def rel_comps(self, exam):
        from website.models import Competitor
        if self.is_staff:
            return Competitor.objects.none()
        teams = self.rel_teams(exam.contest)
        if self.is_mathlete:
            if exam.is_team_exam:
                return Competitor.objects.filter(exam=exam, team__in=teams, mathlete=None)
            else:
                return Competitor.objects.filter(exam=exam, team__in=teams, mathlete=self.mathlete)
        if self.is_coach:
            return Competitor.objects.filter(exam=exam, team__in=teams)
