from background_task import background
from django.utils import timezone
from django.utils.timezone import localtime, now, make_aware
import math
from datetime import timedelta, datetime

# Lets you easily log things when in production, by calling
# log(asdf='hello world') to display {'asdf': 'hello world'}
@background(schedule=365*24*60*60)
def log():
    return

def start_round(exam):
    exam.started = True
    exam.real_end_time = exam._now + exam.duration
    exam.submit_start_time = exam.real_end_time - timedelta(minutes=5)
    exam.save()
    return

def miniround_sub(competitor, problem, miniround):
    time = problem.exam.miniround_end_time(miniround)
    return competitor.submissions.filter(problem=problem, submit_time__lte=time).order_by("-submit_time").first()

def clone_exam(exam, new_contest, new_ep, time):
    from website.models import Exam, Problem
    new_exam = Exam()
    new_exam.contest = new_contest
    new_exam.name = f'{exam.name} - Clone {time}'
    # start_offset = exam.fake_start_time - exam.fake_start_time.date()
    tz = timezone.get_default_timezone()
    new_exam.fake_start_time = datetime.combine(time.date(), exam.fake_start_time.astimezone(tz).time())
    new_exam.fake_end_time = datetime.combine(time.date(), exam.fake_end_time.astimezone(tz).time())
    new_exam.duration = exam.duration
    new_exam.division = exam.division
    new_exam.exampair = new_ep
    new_exam.is_team_exam = exam.is_team_exam
    new_exam.password = exam.password
    new_exam.exam_type = exam.exam_type
    new_exam.save()

    for p in exam.problems.all():
        new_p = Problem()
        new_p.exam = new_exam
        new_p.problem_text = p.problem_text
        new_p.name = f'{p.name} - Clone {time}'
        new_p.problem_number = p.problem_number
        new_p.google_form_link = p.google_form_link
        new_p.save()


def clone_contest(contest):
    from website.models import Contest, ExamPair
    time = datetime.now()
    new_contest = Contest()
    new_contest.name = f'{contest.name} - Clone {time}'
    new_contest.description = contest.description
    new_contest.min_team_size = contest.min_team_size
    new_contest.max_team_size = contest.max_team_size
    new_contest.reg_deadline = time
    new_contest.is_private = True
    new_contest.is_math = contest.is_math
    new_contest.save()

    for ep in contest.exampairs.all():
        new_ep = ExamPair()
        new_ep.contest = new_contest
        new_ep.name = ep.name
        new_ep.save()
        for e in ep.exams.all():
            clone_exam(e, new_contest, new_ep, time)

    for e in contest.exams.all():
        if not e.exampair:
            clone_exam(e, new_contest, None, time)



# score.problem.exam and score.competitor.exam should always match
# do we need to check for invalid scores?
# TODO: what if problems, tasks, or minrounds get added/removed?
def update_scores(comp):
    from website.models import Score, TaskScore, MiniRoundScore, MiniRoundTotal
    exam = comp.exam
    for problem in exam.problems.all():
        s = Score.objects.filter(problem=problem, competitor=comp).first()
        if s is None:
            s = Score(problem=problem, competitor=comp)
            s.save()

        if exam.is_optimization:
            # create taskscores if they don't exist yet
            for task in problem.tasks.all():
                ts = TaskScore.objects.filter(task=task, score=s).first()
                if ts is None:
                    ts = TaskScore(task=task, score=s)
                    ts.save()

        elif exam.is_ai:
            # create miniroundscores if they don't exist
            for i in range(exam.num_minirounds+1):
                mrs = MiniRoundScore.objects.filter(score=s, miniround=i).first()
                if mrs is None:
                    mrs = MiniRoundScore(score=s, miniround=i)
                    mrs.save()
    if exam.is_ai:
        for i in range(exam.num_minirounds):
            mrt = MiniRoundTotal.objects.filter(competitor=comp, miniround=i).first()
            if mrt is None:
                mrt = MiniRoundTotal(competitor=comp, miniround=i)
                mrt.save()




def update_competitors(team):
    from website.models import Competitor, DivChoice
    for exam in team.contest.exams.all():
        # Django guarantees at most one competitor for each
        # (exam, team, mathlete) triple, so there are no duplicates

        # delete any invalid competitors
        for c in Competitor.objects.filter(pk=None):
            c.delete()
        comps = Competitor.objects.filter(exam=exam, team=team)
        for c in comps:
            if exam.is_team_exam:
                # this shouldn't happen, unless manually set in Django Admin
                if c.mathlete is not None:
                    c.delete()
            else:
                # team members might have been kicked,
                # so delete the corresponding competitor
                if c.mathlete not in team.mathletes.all():
                    c.delete()
            if exam.exampair is not None:
                dc = DivChoice.objects.filter(exampair=exam.exampair, mathlete=c.mathlete).first()
                if dc is None or dc.division != exam.division:
                    c.delete()


        # make sure all valid competitors exist, and call update_scores
        if exam.is_team_exam:
            c = Competitor.objects.filter(exam=exam, team=team, mathlete=None).first()
            if c is None:
                c = Competitor(exam=exam, team=team, mathlete=None)
                c.save()
            update_scores(c)
        else:
            for m in team.mathletes.all():
                if exam.exampair is not None:
                    dc = DivChoice.objects.filter(exampair=exam.exampair, mathlete=m).first()
                    if dc is None or dc.division != exam.division:
                        continue
                c = Competitor.objects.filter(exam=exam, team=team, mathlete=m).first()
                if c is None:
                    c = Competitor(exam=exam, team=team, mathlete=m)
                    c.save()
                update_scores(c)

# initializes all Competitors, Scores, and TaskScores
# ensures exactly one score for each (problem, competitor) pair,
# and exactly one taskscore for each (task, score) pair
def update_contest(contest):
    log(starting='update_contest')
    default_div1(contest)
    from website.models import MiniRoundQueue
    try:
        for team in contest.teams.all():
            update_competitors(team)
        for exam in contest.exams.all():
            if exam.is_ai:
                for i in range(exam.num_minirounds+1):
                    mrq = MiniRoundQueue.objects.filter(exam=exam, miniround=i).first()
                    if mrq is None:
                        mrq = MiniRoundQueue(exam=exam, miniround=i)
                        if i == 0:
                            mrq.num_games = 0
                        mrq.save()
    except Exception as e:
        log(error=str(e), during='update_contest')
    log(finished='update_contest')



def reset_contest(contest):
    from website.models import MiniRoundQueue
    for team in contest.teams.all():
        for c in team.competitors.all():
            c.delete()
        if contest.locked and team.mathletes.count() == 0:
            team.delete()
    for exam in contest.exams.all():
        if exam.is_ai:
            for p in exam.problems.all():
                aiprob = p.aiproblem.first()
                for g in aiprob.aigames.all():
                    g.delete()
            for i in range(exam.num_minirounds+1):
                mrq = MiniRoundQueue.objects.get(exam=exam, miniround=i)
                if i == 0:
                    mrq.num_games = 0
                else:
                    mrq.num_games = -1
                mrq.save()
            exam.display_miniround = 0
            exam.save()
        if exam.is_optimization:
            for p in exam.problems.all():
                for t in p.tasks.all():
                    t.best_raw_points = None
                    t.save()
    update_contest(contest)


def reset_exam(exam):
    from website.models import MiniRoundQueue
    if exam.is_ai:
        for p in exam.problems.all():
            aiprob = p.aiproblem.first()
            log(aiprob=str(aiprob), p=str(p))
            for g in aiprob.aigames.all():
                g.delete()
        for i in range(exam.num_minirounds+1):
            mrq = MiniRoundQueue.objects.get(exam=exam, miniround=i)
            if i == 0:
                mrq.num_games = 0
            else:
                mrq.num_games = -1
            mrq.save()
        exam.display_miniround = 0
        exam.save()
    if exam.is_optimization:
        for p in exam.problems.all():
            for t in p.tasks.all():
                t.best_raw_points = None
                t.save()



def compute_weighted_avg(score, m):
    from website.models import MiniRoundScore
    grace = score.problem.exam.num_grace_minirounds
    if m < grace:
        return 0
    else:
        num = 0.0
        den = 0.0
        for i in range(m+1):
            mrs = MiniRoundScore.objects.get(score=score, miniround=i)
            w = math.sqrt(max(i-grace+1, 0))
            num += w * mrs.avg_points
            den += w
        return num / den


def update_ai_leaderboard(exam, m):
    from website.models import Score, MiniRoundScore, MiniRoundTotal

    max_dict = {}
    for p in exam.problems.all():
        max_w_avg = 0.0
        for c in exam.competitors.all():
            s = Score.objects.get(problem=p, competitor=c)
            mrs = MiniRoundScore.objects.get(score=s, miniround=m)
            mrs.weighted_avg = compute_weighted_avg(s, m)
            mrs.save()
            max_w_avg = max(max_w_avg, mrs.weighted_avg)
        max_dict[p.problem_number] = max_w_avg

    for c in exam.competitors.all():
        mrt = MiniRoundTotal.objects.get(competitor=c, miniround=m)
        mrt.total_score = 0

        for p in exam.problems.all():
            max_w_avg = max_dict[p.problem_number]
            s = Score.objects.get(problem=p, competitor=c)
            mrs = MiniRoundScore.objects.get(score=s, miniround=m)
            if max_w_avg > 0:
                mrs.norm_w_avg = mrs.weighted_avg / max_w_avg * 100
            else:
                mrs.norm_w_avg = 0
            mrs.save()
            mrt.total_score += mrs.norm_w_avg
        mrt.save()
    exam.display_miniround = m
    exam.save()


def regrade_games():
    from website.models import AIGame
    games = AIGame.objects.filter(status=3)
    for g in games:
        g.status = 0
        g.history = None
        g.save()

def recheck_games():
    from website.models import AIGame
    from website.tasks import init_all_tasks
    games = AIGame.objects.filter(status=-1)
    for g in games:
        g.status = 0
        g.save()
    init_all_tasks()



# temporary
def scores_from_csv(text):
    from website.models import Team, Problem, Competitor, Score, TaskScore
    lines = text.splitlines()
    data = [line.split(',') for line in lines]
    n = len(data)
    for i in range(n):
        team_id, prob_name, task_num, score = data[i][0], data[i][1], data[i][2], data[i][3]
        team_id = int(team_id)
        team = Team.objects.get(pk=team_id)
        prob = Problem.objects.get(name=prob_name)
        task_num = int(task_num)
        task = prob.tasks.get(task_number=task_num)
        comp = Competitor.objects.get(exam=prob.exam, team=team, mathlete=None)
        if score == '':
            score = None
        else:
            score = int(score)
        s = Score.objects.get(problem=prob, competitor=comp)
        ts = TaskScore.objects.get(task=task, score=s)
        g = prob.grader
        if g is None:
            log(BAD='g is None')
        if g.better(score, ts.raw_points):
            ts.raw_points = score
            ts.save()
        

def recompute_leaderboard(exam):
    log(msg='start recomputing')
    for p in exam.problems.all():
        g = p.grader
        for t in p.tasks.all():
            t.best_raw_points = None        # reset
            for ts in t.taskscores.all():
                if g.better(ts.raw_points, t.best_raw_points):
                    t.best_raw_points = ts.raw_points
            t.save()
            for ts in t.taskscores.all():
                if ts.raw_points is not None:
                    ts.norm_points = g.normalize(ts.raw_points, t.best_raw_points)
                    ts.save()
    for c in exam.competitors.all():
        c.total_score = 0                   # reset
        for s in c.scores.all():
            s.points = 0                    # reset
            for ts in s.taskscores.all():
                s.points += ts.norm_points
            s.points /= s.taskscores.count()
            s.save()
            c.total_score += s.points
        c.save()
    log(msg='done recomputing')


def reset_problem(p):
    for s in p.scores.all():
        s.points = 0
        s.save()
        for ts in s.taskscores.all():
            ts.raw_points = None
            ts.norm_points = 0
            ts.save()
    for sub in p.submissions.all():
        sub.points = None
        sub.status = 0
        sub.save()


def per_page(n):
    return 50


def default_div1(contest):
    from website.models import DivChoice
    log(starting='default_div1')
    try:
        for team in contest.teams.all():
            for m in team.mathletes.all():
                for exampair in contest.exampairs.all():
                    dc = DivChoice.objects.filter(exampair=exampair, mathlete=m).first()
                    if dc is None:
                        dc = DivChoice(exampair=exampair, mathlete=m, division=1)
                        dc.save()
                    elif dc.division is None:
                        dc.division = 1
                        dc.save()
    except Exception as e:
        log(error=str(e), during='default_div1')
    log(finished='default_div1')


def math_indiv_results_from_csv(exam, text):
    from website.models import Team, Competitor, Score, User, Mathlete
    log(start=f'math_indiv_results_from_csv, exam = {exam}')
    try:
        lines = text.splitlines()
        data = [line.split(',') for line in lines]
        n = len(data)
        problems = exam.problem_list

        for i in range(1, n):       # ignore the first line
            team_id = data[i][0]
            indiv_id = data[i][1]
            team = Team.objects.get(pk=team_id)
            user = User.objects.get(pk=indiv_id)
            mathlete = Mathlete.objects.get(user=user)
            comp = Competitor.objects.get(exam=exam, team=team, mathlete=mathlete)
            
            for p in problems:
                s = Score.objects.get(competitor=comp, problem=p)
                s.points = float(data[i][2*p.problem_number + 1])
                s.save()
            comp.total_score = float(data[i][30]) # total score is the 30th column
            comp.save()
        
        # Set problem weights
        for p in problems:
            p.weight = float(data[3][p.problem_number + 18])
            p.save()

    except Exception as e:
        log(error=str(e), during=f'math_indiv_results_from_csv, exam = {exam}')
    log(finished=f'math_indiv_results_from_csv, exam = {exam}')


def math_team_results_from_csv(exam, text):
    from website.models import Team, Competitor, Score, User, Mathlete
    log(start=f'math_team_results_from_csv, exam = {exam}')
    try:
        lines = text.splitlines()
        data = [line.split(',') for line in lines]
        n = len(data)
        problems = exam.problem_list

        for i in range(1, n):       # ignore the first line
            team_id = data[i][0]
            team = Team.objects.get(pk=team_id)
            comp = Competitor.objects.get(exam=exam, team=team, mathlete=None)
            
            for p in problems:
                s = Score.objects.get(competitor=comp, problem=p)
                s.points = float(data[i][2*p.problem_number])
                s.save()
            comp.total_score = float(data[i][49]) # total score is the 30th column
            comp.save()
        
        # Set problem weights
        for p in problems:
            p.weight = float(data[3][p.problem_number + 31])
            p.save()

    except Exception as e:
        log(error=str(e), during=f'math_team_results_from_csv, exam = {exam}')
    log(finished=f'math_team_results_from_csv, exam = {exam}')


def math_tcs_results_from_csv(exam, text):
    from website.models import Team, Competitor, Score, User, Mathlete
    log(start=f'math_tcs_results_from_csv, exam = {exam}')
    try:
        lines = text.splitlines()
        data = [line.split(',') for line in lines]
        n = len(data)
        problems = exam.problem_list

        for i in range(1, n):       # ignore the first line
            team_id = data[i][7]
            team = Team.objects.get(pk=team_id)
            comp = Competitor.objects.get(exam=exam, team=team, mathlete=None)
            
            for p in problems:
                s = Score.objects.get(competitor=comp, problem=p)
                try:
                    s.points = float(data[i][p.problem_number + 8])
                except ValueError:
                    log(error=f'i = {i}, prob {p.problem_number}, str = {data[i][p.problem_number + 8]}')
                s.save()

            try:
                comp.total_score = float(data[i][12]) # total score is the 30th column
            except ValueError:
                log(error=f'i = {i}, str = {data[i][12]}')
            comp.save()
       
    except Exception as e:
        log(error=str(e), during=f'math_tcs_results_from_csv, exam = {exam}')
    log(finished=f'math_tcs_results_from_csv, exam = {exam}')


def exam_results_from_csv(exam, text):
    if exam.is_math:
        if exam.is_team_exam:
            math_team_results_from_csv(exam, text)
        else:
            math_indiv_results_from_csv(exam, text)
    elif exam.is_power:
        math_tcs_results_from_csv(exam, text)
    else:
        log(error=f'exam_results_from_csv called with bad exam {exam}')
         

def calc_indiv_sweepstakes(contest):
    from website.models import IndivSweepstake
    log(start='calc_indiv_sweepstakes')
    for team in contest.teams.all():
        for mathlete in team.mathletes.all():
            iss = IndivSweepstake.objects.filter(team=team, mathlete=mathlete).first()
            if iss is None:
                iss = IndivSweepstake(team=team, mathlete=mathlete)
                iss.save()
            iss.update_total_score()
    log(finished='calc_indiv_sweepstakes')


def calc_sweepstakes(contest):
    from website.models import Sweepstake, Exam
    from django.db.models import Max
    log(start='calc_sweepstakes')
    for team in contest.teams.all():
        ss = Sweepstake.objects.filter(team=team).first()
        if ss is None:
            ss = Sweepstake(team=team)
            ss.save()
        ss.update_indiv_total()

    power_exam = contest.exams.filter(is_team_exam=True, show_results=True, exam_type=Exam.POWER).first()
    if power_exam:
        max_power = power_exam.competitors.aggregate(m=Max('total_score'))['m']
    team_exam = contest.exams.filter(is_team_exam=True, show_results=True, exam_type=Exam.MATH).first()
    if team_exam:
        max_team = team_exam.competitors.aggregate(m=Max('total_score'))['m']
    max_indiv = Sweepstake.objects.filter(team__contest=contest).aggregate(m=Max('indiv_total'))['m']

    for team in contest.teams.all():
        ss = team.sweepstake
        if power_exam:
            power_comp = team.competitors.filter(exam=power_exam).first()
            if power_comp is not None and max_power > 0:
                ss.norm_power = power_comp.total_score / max_power * 200
        if team_exam:
            team_comp = team.competitors.filter(exam=team_exam).first()
            if team_comp is not None and max_team > 0:
                ss.norm_team = team_comp.total_score / max_team * 200
        if max_indiv > 0:
            ss.norm_indiv = ss.indiv_total / max_indiv * 600
        ss.total_score = ss.norm_power + ss.norm_team + ss.norm_indiv
        ss.save()
    log(finished='calc_sweepstakes')

