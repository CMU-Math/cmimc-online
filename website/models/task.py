from django.db import models
from .problem import Problem
from django.core.validators import MinValueValidator
from django.utils.translation import ugettext_lazy as _

def input_data_path(task, filename):
    problem = task.problem
    return 'private/{0}/input_data/{0}_{1}.in'.format(problem.short_name, task.task_number)

class Task(models.Model):
    problem = models.ForeignKey(Problem, related_name="tasks", on_delete=models.CASCADE)
    task_number = models.IntegerField(validators=[MinValueValidator(1)])
    input_file = models.CharField(max_length=1000, blank=True)
    # Currently using links instead of storing files, but this would be the alternative:
    # input_file = models.FileField(upload_to=input_data_path)
    best_raw_points = models.FloatField(null=True, blank=True)
    grader_data = models.JSONField(null=True, blank=True, help_text=_("Data for the \
            problem's grader to use. The format depends on the type of grader"))
    raw_grader_data = models.TextField(blank=True)
    grader_data_file = models.FileField(null=True, blank=True)

    def __str__(self):
        return '{0} - Task {1}'.format(self.problem.name, self.task_number)

