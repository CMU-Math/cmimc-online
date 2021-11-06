from django.db import models
from .team import Team
from .mathlete import Mathlete
from .competitor import Competitor

class IndivSweepstake(models.Model):
    team = models.ForeignKey(Team, related_name='indivsweepstakes', on_delete=models.CASCADE)
    mathlete = models.ForeignKey(Mathlete, related_name='indivsweepstakes', on_delete=models.CASCADE)
    total_score = models.FloatField(default=0.0, db_index=True)

    def update_total_score(self):
        self.total_score = 0
        for exam in self.team.contest.reg_exams(self.mathlete):
            if not exam.is_team_exam:
                c = Competitor.objects.getCompetitor(exam=exam, mathlete=self.mathlete)
                self.total_score += c.total_score
        self.save()

class Sweepstake(models.Model):
    team = models.OneToOneField(Team, related_name='sweepstake', on_delete=models.CASCADE)
    indiv_total = models.FloatField(default=0.0, db_index=True)
    norm_power = models.FloatField(default=0.0)
    norm_team = models.FloatField(default=0.0)
    norm_indiv = models.FloatField(default=0.0)
    total_score = models.FloatField(default=0.0, db_index=True)

    def update_indiv_total(self):
        self.indiv_total = 0
        for iss in self.team.indivsweepstakes.all():
            self.indiv_total += iss.total_score
        self.save()
