from django.db import models
from .problem import Problem
from .competitor import Competitor
from .submission import Submission
from django.utils.translation import ugettext_lazy as _

class Score(models.Model):
    problem = models.ForeignKey(Problem, related_name='scores', on_delete=models.CASCADE)
    competitor = models.ForeignKey(Competitor, related_name='scores', on_delete=models.CASCADE)
    points = models.FloatField(default=0.0, db_index=True)
    latest_sub = models.OneToOneField(Submission, null=True, blank=True, related_name="score", on_delete=models.SET_NULL)

    def __str__(self):
        return '{0}, {1}, score={2}'.format(str(self.problem), self.competitor.name, str(self.points))

    @property
    def display_points(self):
        return f'{self.points:.2f}'

    class Meta:
        unique_together = ['problem', 'competitor']

    @property
    def taskscore_list(self):
        return self.taskscores.order_by('task__task_number')



