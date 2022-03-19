from background_task import background
from django.utils import timezone
from website.models import Exam, AIGame, AISubmission, Submission, Score, MiniRoundScore, MiniRoundQueue, TaskScore
from background_task.models import Task
from datetime import timedelta
from website.utils import log, update_ai_leaderboard
import trueskill
import random


def lastSub(competitor, problem, time):
    sub = competitor.submissions.filter(problem=problem, submit_time__lte=time).order_by("-submit_time").first()
    if sub is None:
        return ''
    else:
        return sub.text


def final_ai_grading(exam):
    log(grade_ai_final='started')
    try:
        comps = exam.competitors.all()
        time = timezone.now()
        for p in exam.problems.all():
            log(problem=p.name)
            subs = []
            for c in comps:
                lastsub = c.submissions.filter(problem=p, submit_time__lte=time).order_by("-submit_time").first()
                if lastsub is not None:
                    subs.append(lastsub)

            n = len(subs)
            ai_prob = p.aiproblem.first()
            np = ai_prob.numplayers
            if n < max(np, 2):
                log(not_enough_players=n, problem=p.problem_name)
                continue                # not enough people to play matches against

            # reset all ratings
            for sub in subs:
                sub.mu = None
                sub.sigma = None
                sub.save()

            
            if np == 2:
                # 1 iteration = n games in total
                c = 12*(n-1) # 12 round robins
                random.shuffle(subs)
                for i in range(c):
                    shift = i % (n-1) + 1
                    for j1 in range(n):
                        j2 = (j1 + shift) % n
                        g = AIGame(status=-1, time=time, numplayers=np, aiproblem=ai_prob, miniround=i)
                        g.save()
                        s1 = AISubmission(game=g, seat=1, competitor=subs[j1].competitor, submission=subs[j1])
                        s1.save()
                        s2 = AISubmission(game=g, seat=2, competitor=subs[j2].competitor, submission=subs[j2])
                        s2.save()
                        g.status = 0    # add to queue after submissions are made
                        g.save()
            elif ai_prob.numplayers == 3:
                # 1 iteration = n games in total
                c = 334
                random.shuffle(subs)
                for i in range(c):
                    x = i % (n-2) + 1
                    y = n - 1 - i % (n-1)
                    if x >= y:
                        x += 1
                    # guaranteed that 1 <= x,y <= n and x =/= y
                    # loops over grid diagonally from top-left to bottom-right (x shifted by 1)
                    # this ensures that you don't get matched with the same opponent
                    # at most twice in one iteration (unless n is small or c is large)
                    for j1 in range(n):
                        j2 = (j1 + x) % n
                        j3 = (j1 + y) % n
                        g = AIGame(status=-1, time=time, numplayers=np, aiproblem=ai_prob, miniround=i)
                        g.save()
                        s1 = AISubmission(game=g, seat=1, competitor=subs[j1].competitor, submission=subs[j1])
                        s1.save()
                        s2 = AISubmission(game=g, seat=2, competitor=subs[j2].competitor, submission=subs[j2])
                        s2.save()
                        s3 = AISubmission(game=g, seat=3, competitor=subs[j3].competitor, submission=subs[j3])
                        s3.save()
                        g.status = 0    # add to queue after submissions are made
                        g.save()
            elif ai_prob.numplayers == 0:
                c = 1000
                for i in range(c):
                    random.shuffle(subs)
                    g = AIGame(status=-1, time=time, numplayers=n, aiproblem=ai_prob, miniround=i)
                    g.save()
                    for j in range(n):
                        s = AISubmission(game=g, seat=j+1, competitor=subs[j].competitor, submission=subs[j])
                        s.save()
                    g.status = 0    # add to queue after submissions are made
                    g.save()
        log(grade_ai_final='ended')
    except Exception as e:
        log(error=str(e))


@background
def schedule_ai_games(exam_id):
    time = timezone.now()
    exam = Exam.objects.get(pk=exam_id)
    comps = exam.competitors.all()
    for p in exam.problems.all():
        subs = []
        for c in comps:
            lastsub = c.submissions.filter(problem=p, submit_time__lte=time).order_by("-submit_time").first()
            if lastsub is not None:
                subs.append(lastsub)

        n = len(subs)
        ai_prob = p.aiproblem.first()
        np = ai_prob.numplayers
        if n < max(np, 2):
            log(not_enough_players=n, problem=p.problem_name)
            continue                # not enough people to play matches against
        random.shuffle(subs)
        if np == 0:
            g = AIGame(status=-1, time=time, numplayers=n, aiproblem=ai_prob, miniround=-1)
            g.save()
            for i in range(n):
                s = AISubmission(game=g, seat=i+1, competitor=subs[i].competitor, submission=subs[i])
                s.save()
            g.status = 0            # add to queue after submissions are made
            g.save()
        else:
            roundup = np * ((n + np - 1) // np)
            for i in range(roundup - n):
                subs.append(subs[i])
            for i in range(roundup // np):
                g = AIGame(status=-1, time=time, numplayers=np, aiproblem=ai_prob, miniround=-1)
                g.save()
                for j in range(np):
                    idx = np*i + j
                    s = AISubmission(game=g, seat=j+1, competitor=subs[idx].competitor, submission=subs[idx])
                    s.save()
                g.status = 0        # add to queue after submissions are made
                g.save()


@background(schedule=0)
def async_grade(submission_id):
    sub = Submission.objects.get(pk=submission_id)
    sub.grade()


def schedule_burst(submission):
    p = submission.problem
    exam = p.exam
    if exam.is_ai:
        # schedule a burst of matches
        time = timezone.now()
        comps = exam.competitors.all()
        subs = []
        othersubs = []
        for c in comps:
            lastsub = c.submissions.filter(problem=p, submit_time__lte=time).order_by("-submit_time").first()
            if lastsub is not None:
                subs.append(lastsub)
                if c != submission.competitor:
                    othersubs.append(lastsub)

        n = len(subs)
        ai_prob = p.aiproblem.first()
        np = ai_prob.numplayers
        if n < max(np, 2):
            log(not_enough_players=n, problem=p.problem_name)
            return                # not enough people to play matches against
        if np == 0:
            for _ in range(ai_prob.burst_matches):
                random.shuffle(subs)
                g = AIGame(status=-1, time=time, numplayers=n, aiproblem=ai_prob, miniround=-1)
                g.save()
                for i in range(n):
                    s = AISubmission(game=g, seat=i+1, competitor=subs[i].competitor, submission=subs[i])
                    s.save()
                g.status = 0        # add to queue after submissions are made
                g.save()
        else:
            seats = [i+1 for i in range(np)]
            for i in range(ai_prob.burst_matches):
                random.shuffle(othersubs)
                subs = [submission] + othersubs
                random.shuffle(seats)
                g = AIGame(status=-1, time=time, numplayers=np, aiproblem=ai_prob, miniround=-1)
                g.save()
                for j in range(np):
                    s = AISubmission(game=g, seat=seats[j], competitor=subs[j].competitor, submission=subs[j])
                    s.save()
                g.status = 0        # add to queue after submissions are made
                g.save()


def check_finished_games_real():
    from website.models import MatchResult
    # log(check_finished_games_real='started')
    games = AIGame.objects.defer("history").filter(status=2)
    for g in games:
        g.status = -1
        g.save()
    for g in games:
        try:
            prob = g.aiproblem.problem
            exam = prob.exam
            subs = []
            ratings = []
            scores = []
            aisubs = []
            for aisub in g.aisubmissions.all():
                sub = aisub.submission
                subs.append(sub)
                ratings.append((sub.rating,))
                scores.append(-aisub.score)
                aisubs.append(aisub)
            new_ratings = trueskill.rate(ratings, ranks=scores)
            for i in range(len(subs)):
                s = subs[i]
                prev_rating = s.public_rating
                s.mu = new_ratings[i][0].mu
                s.sigma = new_ratings[i][0].sigma
                s.save()
                s.update_score_from_rating()
                score = Score.objects.get(problem=prob, competitor=s.competitor)
                mr = MatchResult(score=score, aisubmission=aisubs[i], time_played=g.time, prev_rating=prev_rating, new_rating=s.public_rating)
                mr.save()
            g.status = 4
            g.save()
        except Exception as e:
            log(error=str(e), at='check_finished_games_real', game_id=g.id)
    # log(check_finished_games_real='ended')


@background
def check_finished_games():
    check_finished_games_real()



@background
def check_graded_submissions():
    subs = Submission.objects.filter(status=2)
    for sub in subs:
        sub.status = -1
        sub.save()
    for sub in subs:
        p = sub.problem
        t = sub.task
        c = sub.competitor
        s = Score.objects.get(problem=p, competitor=c)
        ts = TaskScore.objects.get(task=t, score=s)
        if sub.points is not None:
            if ts.raw_points is None or sub.points > ts.raw_points:
                ts.raw_points = sub.points
                ts.save()

                if t.best_raw_points is None or ts.raw_points > t.best_raw_points:
                    t.best_raw_points = ts.raw_points
                    t.save()
                    for ts2 in t.taskscores.all():
                        ts2.norm_points = ts2.raw_points / t.best_raw_points * 100 if ts2.raw_points is not None and t.best_raw_points else 0
                        ts2.save()
                        s2 = ts2.score
                        norms = [ts3.norm_points for ts3 in s2.taskscores.all()]
                        s2.points = sum(norms)/len(norms)
                        ts2.score.save()
                        ts2.score.competitor.update_total_score()
                else:
                    ts.norm_points = ts.raw_points / t.best_raw_points * 100 if t.best_raw_points else 0
                    ts.save()
                    norms = [ts2.norm_points for ts2 in s.taskscores.all()]
                    s.points = sum(norms)/len(norms)
                    s.save()
                    s.competitor.update_total_score()
            sub.status = 4
            sub.save()





def init_all_tasks():
    Task.objects.all().delete() # Clear all previous tasks
    exams = Exam.objects.all()
    ongoing_ai = False
    for exam in exams:
        if exam.is_ai and exam.real_end_time is not None and exam.real_end_time > exam._now:
            ongoing_ai = True
            time = max(exam.fake_start_time, timezone.now())
            schedule_ai_games(exam.id, schedule=time, repeat=60, repeat_until=exam.fake_end_time)
    if ongoing_ai:
        check_finished_games(schedule=0, repeat=30)
        check_graded_submissions(schedule=0, repeat=30)
