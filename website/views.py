from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from website.models import Contest, Exam, Problem, Task, User, Mathlete, Competitor, Submission, Score, Team
from website.forms import UserCreationForm


def home(request):
    return render(request, 'home.html')

def info(request):
    return render(request, 'info.html')

def schedule(request):
    return render(request, 'schedule.html')

def reg_info(request):
    return render(request, 'reg_info.html')

def faq(request):
    return render(request, 'faq.html')

def resources(request):
    return render(request, 'resources.html')

# TODO: handle error when user submits a duplicate team name
# TODO: check registration period to see if new teams can still be made
@login_required
def new_team(request, contest_id):
    user = request.user
    contest = get_object_or_404(Contest, pk=contest_id)
    if user.is_mathlete:
        mathlete = user.mathlete
        if user.has_team(contest):
            team = mathlete.get_team(contest)
            return redirect('team_info', team_id=team.id)
        elif request.method == 'GET':
            return render(request, 'new_team.html')
        else:
            team = Team.create(contest=contest, team_name=request.POST['teamName'], coach=None)
            team.save()
            team.mathletes.add(mathlete)
            return redirect('team_info', team_id=team.id)
    elif user.is_coach:
        if request.method == 'GET':
            return render(request, 'new_team.html')
        else:
            team = Team.create(contest=contest, team_name=request.POST['teamName'], coach=user)
            team.save()
            return redirect('team_info', team_id=team.id)



# TODO: prevent joining after team is registered
@login_required
def join_team(request, team_id, invite_code):
    user = request.user
    team = get_object_or_404(Team, pk=team_id, invite_code=invite_code)
    contest = team.contest
    if user.is_mathlete:
        mathlete = user.mathlete
        if user.has_team(contest):
            real_team = mathlete.get_team(contest)
            return redirect('team_info', team_id=real_team.id)
        elif team.is_registered:
            return redirect('contest_list')
        else:
            team.mathletes.add(mathlete)
            return redirect('team_info', team_id=team.id)


@login_required
def contest_list(request):
    user = request.user
    all_contests = Contest.objects.all()
    tuples = []
    for contest in all_contests:
        if user.is_mathlete:
            if user.has_team(contest):
                team = user.mathlete.get_team(contest)
                tuples.append({'contest':contest, 'has_team':True, 'team':team})
            else:
                tuples.append({'contest':contest, 'has_team':False, 'team':None})
        else:
            tuples.append({'contest':contest, 'has_team':user.has_team(contest), 'team':None})

    # Temporary email list (only visible to staff)
    all_users = User.objects.all()
    all_emails = []
    for user in all_users:
        all_emails.append(user.email)

    context = {
        'tuples': tuples,
        'emaillist': ', '.join(all_emails),
    }
    return render(request, 'contest_list.html', context)


@login_required
def team_info(request, team_id):
    user = request.user
    team = get_object_or_404(Team, pk=team_id)
    if not team.can_see_info(user):
        return redirect('contest_list')

    if request.method == 'POST':
        if request.POST['submit'] == 'leaveTeam' and user.is_mathlete and not team.is_registered:
            mathlete = user.mathlete
            team.mathletes.remove(mathlete)
            return redirect('contest_list')
        elif request.POST['submit'] == 'deleteTeam' and (user.is_coach or user.is_staff):
            team.delete()
            return redirect('contest_list')
        elif request.POST['submit'] == 'register':
            team.register()

    context = {
        'team': team,
        'invite_link': request.build_absolute_uri(
            reverse('join_team', args=[team_id, team.invite_code])
        ),
        'too_large': len(team.mathletes.all()) > team.contest.max_team_size,
        'reg_permission': user != team.coach,
    }
    return render(request, 'team.html', context)


@login_required
def coach_teams(request, contest_id):
    user = request.user
    contest = get_object_or_404(Contest, pk=contest_id)
    if not user.is_coach:
        return redirect('home')

    teams = Team.objects.filter(contest=contest, coach=user)
    context = {
        'teams': teams,
        'contest': contest,
    }
    return render(request, 'coach_teams.html', context)


@login_required
def problem_info(request, exam_id, problem_number):
    user = request.user
    exam = get_object_or_404(Exam, pk=exam_id)
    if not exam.can_see_problems(user):
        raise PermissionDenied("You must be registered for the contest to see \
                the problems")

    problem = get_object_or_404(Problem, exam=exam, problem_number=problem_number)
    try:
        get_object_or_404(Problem, exam=exam, problem_number=str(int(problem_number) + 1))
        next_problem_number = str(int(problem_number)+1)
    except:
        next_problem_number = None

    # TODO: needs to work for coaches too (except they can't submit)
    if user.is_mathlete:
        if exam.is_optimization:
            mathlete = user.mathlete
            competitor = Competitor.objects.getCompetitor(exam, mathlete)
            score = Score.objects.getScore(problem, competitor)
            task_scores = {} # dictionary with tasks as key and scores as value
            for i in range(problem.num_tasks):
                task = Task.objects.get(problem=problem, task_number=i+1)
                pts = score.task_scores[i]
                task_scores[task] = pts

    context = {
        'problem': problem,
        'next_problem_number': next_problem_number,
        'task_scores': task_scores,
        'exam': exam,
    }
    return render(request, 'problem_info.html', context)


@login_required
def submit(request, exam_id, problem_number, task_number=None):
    user = request.user
    exam = get_object_or_404(Exam, pk=exam_id)
    if not exam.is_in_exam(user):
        raise PermissionDenied("You must be registered for the contest to access \
                the submission page")

    problem = get_object_or_404(Problem, exam=exam, problem_number=problem_number)

    if request.method == 'POST':
        if 'codeFile' in request.FILES:
            text = request.FILES['codeFile'].read().decode('utf-8')
        else:
            text = request.POST['codeText']
        competitor = Competitor.objects.getCompetitor(exam, user.mathlete)
        if exam.is_optimization:
            task = Task.objects.get(problem=problem, task_number=task_number)
        else:
            task = None
        submission = Submission(
            problem=problem,
            competitor=competitor,
            text=text,
            task=task,
        )
        submission.save()
        submission.grade()
        return redirect('exam_status', exam_id=exam_id)
    else: # request.method == 'GET'
        if exam.is_optimization:
            task = Task.objects.get(problem=problem, task_number=task_number)
            return submit_opt(request, exam, problem, task)
        elif exam.is_ai:
            return submit_ai(request, exam, problem)
        else:
            return HttpResponse('Error: Only optimization and AI rounds are supported right now')


# pretty basic right now, but we might add more to it later
@login_required
def submit_opt(request, exam, problem, task):
    context = {
        'problem': problem,
        'task': task,
    }
    return render(request, 'submit_opt.html', context)


@login_required
def submit_ai(request, exam, problem, text=None):
    context = {
        'problem': problem,
        'text': text, # if text is not None, insert it into the IDE
    }
    return render(request, 'submit_ai.html', context)


@login_required
def exam_status(request, exam_id):
    user = request.user
    exam = get_object_or_404(Exam, pk=exam_id)
    if not exam.can_see_status(user):
        raise PermissionDenied('You do not have access to this page')
    problems = exam.problems.order_by('problem_number')
    if user.is_mathlete:
        competitor = Competitor.objects.getCompetitor(exam, user.mathlete)
        scores = []
        for problem in problems:
            scores.append(Score.objects.getScore(problem, competitor))
    else:
        scores = []
        for problem in problems:
            scores.append(None)

    context = {
        'exam': exam,
        'all_problems_scores': zip(problems, scores),
    }
    return render(request, 'exam_status.html', context)


@login_required
def submit_view(request, exam_id):
    user = request.user

    exam = get_object_or_404(Exam, pk=exam_id)

    submissions = []
    if user.is_mathlete:
        competitor = Competitor.objects.getCompetitor(exam, user.mathlete)
        submissions = Submission.objects.filter(competitor=competitor).order_by('-submit_time')

    context = {
        'exam': exam,
        'submissions': submissions,
    }
    return render(request, 'submit_view.html', context)

@login_required
def submit_text(request, exam_id, submit_id):
    user = request.user

    exam = get_object_or_404(Exam, pk=exam_id)

    submission = get_object_or_404(Submission, pk=submit_id)

    context = {
        'submission': submission
    }
    return render(request, 'submit_text.html', context)

# User Account Signup
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=email, password=raw_password)
            login(request, user)
            print(form.cleaned_data)
            if form.cleaned_data.get('role') == User.MATHLETE:
                mathlete = Mathlete(user=user)
                mathlete.save()
            return redirect('contest_list')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})
