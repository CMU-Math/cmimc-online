from django.db import models
from .score import Score
from .airound import AISubmission

class MatchResult(models.Model):
    score = models.ForeignKey(Score, related_name='matchresults', on_delete=models.CASCADE)
    aisubmission = models.ForeignKey(AISubmission, related_name='matchresults', on_delete=models.CASCADE)
    time_played = models.DateTimeField(auto_now_add=True, db_index=True)
    prev_rating = models.FloatField(default=0)
    new_rating = models.FloatField(default=0)

    @property
    def opponent_list(self):
        g = self.aisubmission.game
        if g.aiproblem.numplayers == 0:
            return 'Everyone'
        else:
            names = []
            for aisub in g.aisubmissions.all():
                if aisub == self.aisubmission:
                    continue
                names.append(aisub.competitor.name)
            return ', '.join(names)

