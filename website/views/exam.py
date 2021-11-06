from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from website.models import Exam, Competitor, Score, MiniRoundScore, Problem, AISubmission, Submission
from website.utils import miniround_sub, per_page, log
from django.core.paginator import Paginator 
from sympy.parsing.latex import parse_latex
from sympy import simplify
import signal

def all_problems_power(request, user, exam):
    try:
        problems = exam.problem_list
        if user.is_mathlete:
            competitor = Competitor.objects.getCompetitor(exam, user.mathlete)
            password = competitor.team.invite_code
        else:
            password = 'N/A (You are not a contestant)'

        context = {
            'exam': exam,
            'password': password,
            'problems': problems,
        }
        return render(request, 'exam/all_problems_power.html', context)
    except Exception as e:
        log(ERROR=str(e), during='all_problems_power')


'''
@background
def eq(l1, l2):


def handler(signum, fram):
    print('timeout in handler')
    raise TimeoutError()
'''

def all_problems_math(request, user, exam):
    try:
        problems = exam.problem_list
        if user.is_mathlete:
            competitor = Competitor.objects.getCompetitor(exam, user.mathlete)


        if request.method == "POST":
            if not user.can_submit(exam):
                raise PermissionDenied("You are not allowed to submit to this problem")
            if 'save' in request.POST:
                num = request.POST['save']
                p = problems.get(problem_number=num)
                latex = request.POST[f'input-{num}']
                '''
                print('latex: ', latex)
                expr = parse_latex(latex)
                print('sympy expr: ', expr)
                print('ans latex: ', p.answer)
                ans_expr = parse_latex(p.answer)
                print('ans expr: ', ans_expr)
                '''

                '''
                signal.signal(signal.SIGALRM, handler)
                signal.alarm(5)
                try:
                    print(expr.equals(ans_expr))
                except:
                    print("timeout!")
                signal.alarm(0)
                '''

                sub = Submission(problem=p, competitor=competitor, text=latex)
                sub.save()
                score = Score.objects.get(problem=p, competitor=competitor)
                score.latest_sub = sub
                score.save()
                return redirect('all_problems', exam_id=exam.id)
            elif 'password' in request.POST:
                competitor.password = request.POST['password']
                competitor.save()
                return redirect('all_problems', exam_id=exam.id)

        prob_info = []
        for p in problems:
            if user.is_mathlete:
                score = Score.objects.get(problem=p, competitor=competitor)
                if score.latest_sub:
                    text = score.latest_sub.text
                else:
                    text = None
            else:
                text = None
            prob_info.append({
                'p': p,
                'n': p.problem_number,
                'latest_sub': text,
            })

        can_submit = False
        can_enter_password = False
        if user.is_mathlete:
            if competitor.password == exam.password:
                can_submit = True
            elif exam.password != '' and competitor.password != exam.password:
                can_enter_password = True


        context = {
            'exam': exam,
            'prob_info': prob_info,
            'can_submit': can_submit,
            'can_enter_password': can_enter_password,
        }
        return render(request, 'exam/all_problems_math.html', context)
    except Exception as e:
        log(ERROR=str(e), during='all_problems_math')

@login_required
def all_problems(request, exam_id):
    user = request.user
    exam = get_object_or_404(Exam, pk=exam_id)
    if not user.can_view_exam(exam):
        raise PermissionDenied('You do not have access to this page')

    if exam.is_math:
        return all_problems_math(request, user, exam)
    elif exam.is_power:
        return all_problems_power(request, user, exam)

    problems = exam.problem_list

    prob_score_task_rank = []
    if user.is_mathlete:
        competitor = Competitor.objects.getCompetitor(exam, user.mathlete)

        num_comps = Competitor.objects.filter(exam=exam).count()
        for problem in problems:
            score = Score.objects.get(problem=problem, competitor=competitor)
            rank = Score.objects.filter(problem=problem, points__gt=score.points).count() + 1
            g = problem.grader
            if exam.is_optimization:
                task_str = ', '.join([ts.display_raw() for ts in score.taskscores.all()])
            else:
                task_str = ''
            score_str = score.display_points
            rank_str = '{0} out of {1}'.format(str(rank), str(num_comps))
            prob_score_task_rank.append((problem, score_str, task_str, rank_str))

    context = {
        'exam': exam,
        'prob_score_task_rank': prob_score_task_rank,
    }
    return render(request, 'exam/all_problems.html', context)


@login_required
def miniround_scores(request, exam_id):
    user = request.user
    exam = get_object_or_404(Exam, pk=exam_id)
    if not user.can_view_exam(exam) or not user.is_mathlete:
        raise PermissionDenied('You do not have access to this page')

    c = Competitor.objects.getCompetitor(exam=exam, mathlete=user.mathlete)
    problems = exam.problem_list

    # TODO: let coaches see all their teams' miniround pages via tabs at the top
    rows = []
    for m in range(exam.display_miniround, 0, -1):
        scores = []
        for p in problems:
            s = Score.objects.get(problem=p, competitor=c)
            mrs = MiniRoundScore.objects.get(score=s, miniround=m)
            scores.append(round(mrs.avg_points, 2))
        rows.append({
            "miniround": m,
            "scores": scores,
        })

    context = {
        "rows": rows,
        "exam": exam,
        "problems": problems,
    } 
    return render(request, 'exam/miniround_scores.html', context)


@login_required
def match_results(request, exam_id, problem_number):
    user = request.user
    exam = get_object_or_404(Exam, pk=exam_id)
    if not user.can_view_exam(exam) or not user.is_mathlete:
        raise PermissionDenied('You do not have access to this page')

    problems = exam.problem_list
    p = get_object_or_404(Problem, exam=exam, problem_number=problem_number)
    c = Competitor.objects.getCompetitor(exam=exam, mathlete=user.mathlete)
    s = Score.objects.get(problem=p, competitor=c)

    mrs = s.matchresults.order_by('-time_played')
    items_per_page = per_page(mrs.count())
    paginator = Paginator(mrs, items_per_page)
    page_number = request.GET.get('page', default=1)
    page_obj = paginator.get_page(page_number)

    context = {
        "exam": exam,
        "problems": problems,
        "problem": p,
        "aiprob": p.aiproblem.first(),
        'page_obj': page_obj,
        'all_pages': [paginator.page(i) for i in paginator.page_range]
    } 
    return render(request, 'exam/match_results.html', context)




