from django.db import models
from .contest import Contest
from .mathlete import Mathlete
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
import random

class Team(models.Model):
    contest = models.ForeignKey(Contest, related_name='teams', on_delete=models.CASCADE)
    mathletes = models.ManyToManyField(Mathlete, related_name='teams')
    coach = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, \
                              related_name='teams', on_delete=models.SET_NULL)
    team_name = models.CharField(max_length=40)
    invite_code = models.CharField(unique=True, max_length=15)
    wants_merge = models.BooleanField(default=False)

    @classmethod
    def create(cls, contest, team_name, coach):
        invite_code = Team.generate_code()
        return cls(contest=contest,team_name=team_name,invite_code=invite_code,coach=coach)

    @staticmethod
    def generate_code():
        digits = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        code = ''.join(random.choice(digits) for _ in range(15))
        while Team.objects.filter(invite_code=code).exists():
            code = ''.join(random.choice(digits) for _ in range(15))
        return code

    def __str__(self):
        return '{0} ({1})'.format(self.team_name, self.mathlete_list)

    class Meta:
        unique_together = ['team_name', 'contest']

    def has_member(self, user):
        return user.is_mathlete and user.mathlete.teams.filter(pk=self.id).exists()

    @property
    def mathlete_list(self):
        if not self.mathletes.exists():
            return 'No students'
        return ', '.join([m.user.long_name for m in self.mathletes.all()])

    @property
    def email_list(self):
        if not self.mathletes.exists():
            return 'No students'
        return ', '.join([m.user.email for m in self.mathletes.all()])


    # TODO: add feature to manually extend registration deadline for certain teams
    @property
    def is_finalized(self):
        return self.contest.locked
