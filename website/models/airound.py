from django.db import models
from .team import Team
from .competitor import Competitor
from .problem import Problem
from .submission import Submission



class AIGrader(models.Model):
    hostname = models.TextField() # hostname of the grader
    currently = models.TextField() # current status of the grader
    class Meta:
        db_table = "graders_airound"


class AIProblem(models.Model):
    code = models.TextField() # python grading code for the contest
    problem = models.ForeignKey(Problem, related_name="aiproblem", on_delete=models.CASCADE)
    numplayers = models.IntegerField() # if numplayers == 0, the game can have a variable number of players. Otherwise, numplayers is constant
    starter_file = models.TextField(blank=True)
    visualizer = models.TextField(blank=True)
    burst_matches = models.IntegerField(default=10)
    class Meta:
        db_table = "contests_airound"

    def __str__(self):
        return self.problem.name


class AIGame(models.Model):
    """
    0 = in queue
    1 = running
    2 = graded
    3 = error while grading
    4 = results saved to leaderboard
    """
    status = models.IntegerField(default=0)
    history = models.JSONField(null=True, blank=True) # after the game is played, gives the history output of the grader
    time = models.DateTimeField(db_index=True) # when the game should be played
    numplayers = models.IntegerField() # number of players
    aiproblem = models.ForeignKey(AIProblem, related_name="aigames", on_delete=models.CASCADE) # which problem to use
    worker = models.ForeignKey(AIGrader, null=True, blank=True, on_delete=models.SET_NULL) # which grader was used to grade this
    miniround = models.IntegerField()
    class Meta:
        db_table = "games_airound"

    def __str__(self):
        return '{0}, MR={1}, status={2}'.format(str(self.aiproblem), str(self.miniround), str(self.status))


class AISubmission(models.Model):
    game = models.ForeignKey(AIGame, related_name="aisubmissions", on_delete=models.CASCADE) # game that submission was made for
    seat = models.IntegerField() # position the player's entry should be in for the grader
    score = models.FloatField(null=True, blank=True) # resulting score of the round for the team
    competitor = models.ForeignKey(Competitor, related_name="aisubmissions", on_delete=models.CASCADE) # team that made the submission
    submission = models.ForeignKey(Submission, related_name="aisubmissions", null=True, blank=True, on_delete=models.CASCADE)
    class Meta:
        db_table = "submissions_airound"

    def __str__(self):
        return '[{0}] comp={1}'.format(str(self.game), str(self.competitor))
