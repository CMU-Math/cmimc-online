from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin

from website.forms import UserCreationForm, UserChangeForm
from website.models import Contest, Exam, Problem, User, Mathlete, Team, Competitor, Submission, Score, Task, TaskScore, AIGrader, AIProblem, AIGame, AISubmission, MiniRoundScore, MiniRoundQueue, MiniRoundTotal, MatchResult, ExamPair, DivChoice, IndivSweepstake


class UserAdmin(DefaultUserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = User
    list_display = ('email', 'name', 'role', 'is_staff', 'is_tester', 'tnc_signature')
    list_filter = ('role', 'is_staff', 'is_tester')
    fieldsets = (
        (None, {'fields': ('first_name', 'last_name', 'email', 'full_name', 'alias', 'password', 'role', 'tnc_signature')}),
        ('Permissions', {'fields': ('is_superuser', 'is_staff', 'is_tester', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'email', 'full_name', 'alias', 'password1', 'password2', 'role', 'is_superuser', 'is_staff', 'is_tester', 'is_active')}
        ),
    )
    search_fields = ('email', 'first_name', 'last_name', 'full_name')
    ordering = ('email',)


class TeamAdmin(admin.ModelAdmin):
    list_display = ('team_name', 'mathlete_list', 'coach', 'contest', 'email_list',)
    list_filter = ('contest', 'wants_merge')
    search_fields = ('team_name', 'mathletes__user__first_name', 'mathletes__user__last_name', 'mathletes__user__full_name', 'coach__first_name', 'coach__last_name', 'coach__full_name',)


class CompetitorAdmin(admin.ModelAdmin):
    list_display = ('team', 'exam', 'mathlete', 'total_score',)
    list_filter = ('exam',)
    search_fields = ('team__team_name', 'mathlete__user__first_name', 'mathlete__user__last_name', 'mathlete__user__full_name',)


class ScoreAdmin(admin.ModelAdmin):
    list_display = ('competitor', 'problem', 'points',)
    list_filter = ('competitor__exam', 'problem',)


class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('problem', 'task', 'status', 'competitor')
    list_filter = ('problem', 'task', 'status')
    autocomplete_fields = ['competitor']


class AIGameAdmin(admin.ModelAdmin):
    list_display = ('aiproblem', 'status', 'time')
    list_filter = ('aiproblem', 'status')


class IndivSweepstakeAdmin(admin.ModelAdmin):
    list_display = ('mathlete', 'team', 'total_score',)
    list_filter = ('mathlete__user__first_name', 'mathlete__user__last_name', 'mathlete__user__full_name', 'team')




admin.site.register(Contest)
admin.site.register(Exam)
admin.site.register(Problem)
admin.site.register(User, UserAdmin)
admin.site.register(Mathlete)
admin.site.register(Team, TeamAdmin)
admin.site.register(Competitor, CompetitorAdmin)
admin.site.register(Submission, SubmissionAdmin)
admin.site.register(Score)
admin.site.register(Task)
admin.site.register(TaskScore)
admin.site.register(AIGrader)
admin.site.register(AIProblem)
admin.site.register(AIGame, AIGameAdmin)
admin.site.register(AISubmission)
admin.site.register(MiniRoundScore)
admin.site.register(MiniRoundQueue)
admin.site.register(MiniRoundTotal)
admin.site.register(MatchResult)
admin.site.register(ExamPair)
admin.site.register(DivChoice)
admin.site.register(IndivSweepstake, IndivSweepstakeAdmin)
