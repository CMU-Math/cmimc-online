from django.db import models
from .problem import Problem
from .competitor import Competitor
from .task import Task
from django.utils.translation import ugettext_lazy as _
import trueskill

class Submission(models.Model):
    problem = models.ForeignKey(Problem, related_name='submissions', on_delete=models.CASCADE)
    competitor = models.ForeignKey(Competitor, related_name='submissions', \
            on_delete=models.CASCADE)
    points = models.FloatField(null=True, blank=True)
    task = models.ForeignKey(Task, null=True, blank=True, related_name='submissions', on_delete=models.CASCADE)
    text = models.TextField(help_text=_('The string that the competitor submitted. \
            Its format depends on the exam (can be an integer, source code, \
            program output, etc)'))
    submit_time = models.DateTimeField(auto_now_add=True, db_index=True)
    status = models.IntegerField(default=0, db_index=True)
    error_msg = models.TextField(blank=True)
    mu = models.FloatField(null=True, blank=True)
    sigma = models.FloatField(null=True, blank=True)

    def __str__(self):
        return str(self.competitor) + "'s submission to problem " + str(self.problem)

    def grade(self):
        from .score import Score
        score = Score.objects.get(problem=self.problem, competitor=self.competitor)
        g = self.problem.grader
        if g is not None:
            g.grade(self, score)

    def display_points(self, default='N/A'):
        if self.points is None:
            return default
        g = self.problem.grader
        if g is not None: # assumes optimization
            return g.display_raw(self.points)
        else:
            return str(self.points)
    
    @property
    def rating(self):
        if self.mu is None:
            return trueskill.Rating()
        else:
            return trueskill.Rating(mu=self.mu, sigma=self.sigma)

    @property
    def public_rating(self):
        # trueskill mu-3*sigma ratings are usually from 0-50,
        # so we double them to 0-100
        return 2*trueskill.expose(self.rating)
    
    def update_score_from_rating(self):
        from .score import Score
        s = Score.objects.get(problem=self.problem, competitor=self.competitor)
        s.points = self.public_rating
        s.save()
        s.competitor.update_total_score()
        
