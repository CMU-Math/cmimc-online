from django.db import models
from .exam import Exam
from .team import Team
from .mathlete import Mathlete
from django.utils.translation import ugettext_lazy as _
from website.managers import CompetitorManager

class Competitor(models.Model):
    exam = models.ForeignKey(Exam, related_name='competitors', on_delete=models.CASCADE)
    team = models.ForeignKey(Team, related_name='competitors', on_delete=models.CASCADE)
    mathlete = models.ForeignKey(Mathlete, blank=True, null=True, \
            related_name='competitors', on_delete=models.CASCADE, \
            help_text=_('If the exam is an individual exam, this is the \
            corresponding mathlete. If the exam is a team exam, this is null'))
    total_score = models.FloatField(default=0.0, db_index=True)
    password = models.CharField(max_length=100, blank=True)

    objects = CompetitorManager()

    class Meta:
        unique_together = ['exam', 'team', 'mathlete']

    @property
    def is_team(self):
        return self.exam.is_team_exam

    def __str__(self):
        if self.is_team:
            return "T_Comp [exam={0}]: {1}".format(str(self.exam), str(self.team))
        else:
            return "M_Comp [exam={0}]: {1}".format(str(self.exam), str(self.mathlete))

    def update_total_score(self):
        self.total_score = 0
        for s in self.scores.all():
            self.total_score += s.points
        self.save()

    @property
    def name(self):
        if self.is_team:
            return self.team.team_name
        else:
            return self.mathlete.user.name

    @property
    def display_score(self):
        return f'{self.total_score:.2f}'

    @property
    def score_list(self):
        return self.scores.order_by('problem__problem_number')

