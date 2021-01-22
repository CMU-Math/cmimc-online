from background_task import background
from website.models import Exam, Team
from django.utils import timezone
from website.models import AIGame, AISubmission, Submission
from background_task.models import Task
from datetime import timedelta

@background
def initialize_one(exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)

    #TODO make schedule, right now just puts all things at the same time

    teams = Team.objects.filter(contest=exam.contest)

    counter = 0
    curr_game = None
    for team in teams:
        if(counter==0):
            temp_game = AIGame(history=None, time=exam.start_time, numplayers=4, contest=exam)
            temp_game.save()
            curr_game = temp_game

        temp_sub = AISubmission(game=curr_game, seat = counter, code=None, team=team)
        temp_sub.save()
        counter+=1
        counter%=4

def lastSub(competitor, problem):
    sub = competitor.submissions.filter(problem=problem).order_by("-submit_time").first()
    if sub is None:
        return ''
    else:
        return sub.text


# miniround m is graded 5*m minutes after exam starts (1 <= n <= 36)
@background
def grade_miniround(exam_id, m):
    print("Grading miniround, time = ", timezone.now())
    exam = Exam.objects.get(pk=exam_id)
    comps = exam.competitors.all()
    n = len(comps)
    for p in exam.problems.all():
        codes = [lastSub(c, p) for c in comps]
        ai_prob = p.aiproblem.first()
        if ai_prob.numplayers == 2:
            # 10 iterations = 20 games per player
            c = 10
            for i in range(c*(m-1), c*m):
                shift = i % (n-1) + 1
                for j1 in range(n):
                    j2 = (j1 + shift) % n
                    print(j1, j2)
                    g = AIGame(time=timezone.now(), numplayers=2, problem=ai_prob)
                    g.save()
                    s1 = AISubmission(game=g, seat=1, code=codes[j1], competitor=comps[j1])
                    s1.save()
                    s2 = AISubmission(game=g, seat=2, code=codes[j2], competitor=comps[j2])
                    s2.save()
        elif ai_prob.numplayers == 3:
            # 7 iterations = 21 games per player
            c = 7
            for i in range(c*(m-1), c*m):
                x = i % (n-2) + 1
                y = n - 1 - i % (n-1)
                if x >= y:
                    x += 1
                # guaranteed that 1 <= x,y <= n and x =/= y
                # loops over grid diagonally from top-left to bottom-right
                # this ensures that you don't get matched with the same opponent
                # at most twice in one iteration (unless n is small or c is large)
                for j1 in range(n):
                    j2 = (j1 + x) % n
                    j3 = (j1 + y) % n
                    print(j1, j2, j3)
                    g = AIGame(time=timezone.now(), numplayers=3, problem=ai_prob)
                    g.save()
                    s1 = AISubmission(game=g, seat=1, code=codes[j1], competitor=comps[j1])
                    s1.save()
                    s2 = AISubmission(game=g, seat=2, code=codes[j2], competitor=comps[j2])
                    s2.save()
                    s3 = AISubmission(game=g, seat=3, code=codes[j3], competitor=comps[j3])
                    s3.save()
        elif ai_prob.numplayers == 0:
            g = AIGame(time=timezone.now(), numplayers=n, problem=ai_prob)
            g.save()
            for i in range(n):
                s = AISubmission(game=g, seat=i+1, code=codes[i], competitor=comps[i])
                s.save()


@background(schedule=0)
def async_grade(submission_id):
    sub = Submission.objects.get(pk=submission_id)
    sub.grade()


def init_all_tasks():
    Task.objects.all().delete() # Clear all previous tasks
    exams = Exam.objects.all()
    for exam in exams:
        if exam.is_ai:
            exam_time = exam.end_time - exam.start_time
            miniround_time = timedelta(minutes=1)
            num_minirounds = exam_time // miniround_time 
            print(exam_time, miniround_time, num_minirounds)
            for i in range(1, num_minirounds+1):
                if timezone.now() < exam.start_time + i*miniround_time:
                    grade_miniround(exam.id, i, schedule=exam.start_time + i*miniround_time)
                    print(i)
