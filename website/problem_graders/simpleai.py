
from .base import BaseGrader

class SimpleAI(BaseGrader):
    def grade(self, submission, score):
        try:
            points = int(submission.text)
        except ValueError:
            points = 0

        submission.points = points
        submission.is_graded = True
        submission.save()

        score.points = points
        score.save()
        submission.competitor.update_total_score()