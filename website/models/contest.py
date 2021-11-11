from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from datetime import timedelta

class Contest(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    min_team_size = models.IntegerField() # if we ever need an individual contest,
    max_team_size = models.IntegerField() # set min and max team size to 1
    reg_deadline = models.DateField()
    is_private = models.BooleanField(default=False)
    locked = models.BooleanField(default=False) # manually lock registration 24 hours after the reg deadline
    show_final_results = models.BooleanField(default=False)
    div_locked = models.BooleanField(default=False)
    show_sweepstakes = models.BooleanField(default=False, help_text="make final results public")
    is_math = models.BooleanField()




    def __str__(self):
        return self.name

    @cached_property
    def now(self):
        return timezone.now()

    # Assumes there is at least one exam in each contest
    @cached_property
    def end_time(self):
        if not self.exams.exists():
            return self.now + timedelta(days=10001+self.id)
        temp = self.now - timedelta(days=100000) # 300 years in the past
        for e in self.exams.all():
            if e.end_time > temp:
                temp = e.end_time
        return temp
    
    # Assumes there is at least one exam in each contest
    @cached_property
    def start_time(self):
        if not self.exams.exists():
            return self.now + timedelta(days=10000+self.id)
        temp = self.now + timedelta(days=100000) # 300 years in the future
        for e in self.exams.all():
            if e.start_time < temp:
                temp = e.start_time
        return temp

    @cached_property
    def ended(self):
        return timezone.localtime(self.now).date() > timezone.localtime(self.end_time).date()

    @cached_property
    def started(self):
        return timezone.localtime(self.now).date() >= timezone.localtime(self.start_time).date()

    @cached_property
    def ongoing(self):
        return self.started and not self.ended

    def reg_exams(self, mathlete):
        from website.models import DivChoice
        ret = []
        for e in self.exams.all():
            if e.exampair is None:
                ret.append(e)
            else:
                dc = DivChoice.objects.filter(exampair=e.exampair, mathlete=mathlete).first()
                if dc is not None and dc.division == e.division:
                    ret.append(e)
        return ret

