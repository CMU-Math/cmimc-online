from .base import BaseGrader

class OptimizationGrader(BaseGrader):
    def __init__(self, problem):
        super().__init__(problem)
        self.num_tasks = problem.num_tasks

    def grade(self, submission, score):
        task = submission.task
        self.task_number = task.task_number
        self.task_data = task.grader_data
        points = self.grade_task(submission.text)
        submission.points = points
        submission.is_graded = True
        submission.save()

        idx = submission.task.task_number-1 # 0 indexed for list
        if points is not None and points > score.task_scores[idx]:
            score.task_scores[idx] = points
            score.points = sum(score.task_scores)
            score.save()
            submission.competitor.update_total_score()


    def grade_task(self, user_input):
        raise NotImplementedError()