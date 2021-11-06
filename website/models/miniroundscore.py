from django.db import models
from .score import Score
from .exam import Exam
from .competitor import Competitor

# Only used for AI Round
class MiniRoundScore(models.Model):
    score = models.ForeignKey(Score, related_name="miniroundscores", on_delete=models.CASCADE)
    miniround = models.IntegerField()
    points = models.FloatField(default=0.0) # sum of points over all games this miniround
    games = models.IntegerField(default=0.0)
    weighted_avg = models.FloatField(default=0.0) # cumulative score, weighted by miniround
    norm_w_avg = models.FloatField(default=0.0)

    class Meta:
        unique_together = ['score', 'miniround']

    def __str__(self):
        return 'points={0}, mr={1}, game={2}'.format(str(self.points), str(self.miniround), str(self.score.problem))

    @property
    def avg_points(self):
        if self.games == 0:
            return 0.0
        return self.points / self.games


class MiniRoundQueue(models.Model):
    exam = models.ForeignKey(Exam, related_name="miniroundqueues", on_delete=models.CASCADE)
    miniround = models.IntegerField()
    num_games = models.IntegerField(default=-1)

    def __str__(self):
        return '{0}, mr={1}, queue={2}'.format(self.exam, self.miniround, self.num_games)


class MiniRoundTotal(models.Model):
    competitor = models.ForeignKey(Competitor, related_name="miniroundtotals", on_delete=models.CASCADE)
    miniround = models.IntegerField()
    total_score = models.FloatField(default=0.0)


