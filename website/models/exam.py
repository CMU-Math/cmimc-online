from django.db import models
from .contest import Contest
from .mathlete import Mathlete
from django.utils.functional import cached_property
from django.utils import timezone


class ExamPair(models.Model):
    contest = models.ForeignKey(Contest, related_name='exampairs', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.name}, {self.contest}'


class DivChoice(models.Model):
    exampair = models.ForeignKey(ExamPair, related_name='divchoices', on_delete=models.CASCADE)
    mathlete = models.ForeignKey(Mathlete, related_name='divchoices', on_delete=models.CASCADE)
    division = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f'{self.mathlete.user.name} - {self.exampair.name} Division {self.division}'


class Exam(models.Model):
    contest = models.ForeignKey(Contest, related_name='exams', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, unique=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    submit_start_time = models.DateTimeField(null=True, blank=True)

    division = models.IntegerField(null=True, blank=True)
    exampair = models.ForeignKey(ExamPair, null=True, blank=True, related_name='exams', on_delete=models.SET_NULL)
    is_team_exam = models.BooleanField()
    password = models.CharField(max_length=100, blank=True)
    show_results = models.BooleanField(default=False, help_text="make the final results public")
    
    OPTIMIZATION = 'OPT'
    AI = 'AI'
    MATH = 'MATH'
    POWER = 'POW'
    TYPE_CHOICES = [
        (OPTIMIZATION, 'Optimization'),
        (AI, 'AI'),
        (MATH, 'Math (short answer)'),
        (POWER, 'Power (proof)'),
    ]
    exam_type = models.CharField(max_length=4, choices=TYPE_CHOICES, default=OPTIMIZATION)

    def __str__(self):
        return self.name

    @cached_property
    def is_optimization(self):
        return self.exam_type == self.OPTIMIZATION

    @cached_property
    def is_ai(self):
        return self.exam_type == self.AI

    @cached_property
    def is_math(self):
        return self.exam_type == self.MATH

    @cached_property
    def is_power(self):
        return self.exam_type == self.POWER

    # whether to allow contestants to see the leaderboard during the exam
    @cached_property
    def show_leaderboard(self):
        if self.exam_type == self.OPTIMIZATION:
            return True
        if self.exam_type == self.AI:
            return True
        if self.exam_type == self.MATH:
            return False
        if self.exam_type == self.POWER:
            return False

    # whether to allow contestants to see their submission scores during the exam
    @cached_property
    def show_own_scores(self):
        if self.exam_type == self.OPTIMIZATION:
            return True
        if self.exam_type == self.AI:
            return True
        if self.exam_type == self.MATH:
            return False
        if self.exam_type == self.POWER:
            return False
        
    @cached_property
    def _now(self):
        return timezone.now()

    @cached_property
    def ended(self):
        return self._now > self.end_time

    @cached_property
    def started(self):
        return self._now >= self.start_time

    @cached_property
    def ongoing(self):
        return self.started and not self.ended

    @cached_property
    def time_until_start_days(self):
        if not self.started:
            return (self.start_time - self._now).days
        else:
            return None

    @cached_property
    def time_until_start_hours(self):
        if not self.started:
            return (int)((self.start_time - self._now).seconds/60/60)
        else:
            return None

    @cached_property
    def time_until_start_minutes(self):
        if not self.started:
            return (int)((self.start_time - self._now).seconds / 60)
        else:
            return None

    @cached_property
    def time_until_start_seconds(self):
        if not self.started:
            return (self.start_time - self._now).seconds
        else:
            return None

    @cached_property
    def time_remaining_days(self):
        if not self.ended:
            return (self.end_time - self._now).days
        else:
            return None

    @cached_property
    def time_remaining_hours(self):
        if not self.ended:
            return (int)((self.end_time - self._now).seconds/60/60)
        else:
            return None

    @cached_property
    def time_remaining_minutes(self):
        if not self.ended:
            return (int)((self.end_time - self._now).seconds / 60)%60
        else:
            return 0

    # number of seconds remaining in exam
    @cached_property
    def time_remaining(self):
        return max((self.end_time - self._now).total_seconds(), 0)

    # in seconds
    @cached_property
    def time_until_submit_start(self):
        return max((self.submit_start_time - self._now).total_seconds(), 0)


    def time_remaining_seconds(self):
        if not self.ended:
            return (self.end_time - self._now).seconds%60
        else:
            return None

    @property
    def problem_list(self):
        return self.problems.order_by('problem_number')

    @property
    def num_minirounds(self):
        return (self.end_time - self.miniround_start) // self.miniround_time + 1

    # the time that the ith miniround ends, and gets graded
    # i is 1-indexed
    def miniround_end_time(self, i):
        return self.miniround_start + (i-1) * self.miniround_time

    @cached_property
    def prev_miniround(self):
        if self._now < self.miniround_start:
            return 0
        return (self._now - self.miniround_start) // self.miniround_time + 1


