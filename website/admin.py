from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin

from website.forms import UserCreationForm, UserChangeForm
from website.models import Contest, Exam, Problem, User, Mathlete, Team, Competitor, Submission, Score, Task


class UserAdmin(DefaultUserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = User
    list_display = ('full_name', 'email', 'role', 'is_staff', 'is_active',)
    list_filter = ('role', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('full_name', 'alias', 'email', 'password', 'role')}),
        ('Permissions', {'fields': ('is_superuser', 'is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('full_name', 'alias', 'email', 'password1', 'password2', 'role', 'is_superuser', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('full_name',)
    ordering = ('full_name',)


class TeamAdmin(admin.ModelAdmin):
    list_display = ('team_name', 'mathlete_list', 'coach', 'is_finalized',)
    list_filter = ('is_finalized',)

admin.site.register(Contest)
admin.site.register(Exam)
admin.site.register(Problem)
admin.site.register(User, UserAdmin)
admin.site.register(Mathlete)
admin.site.register(Team, TeamAdmin)
admin.site.register(Competitor)
admin.site.register(Submission)
admin.site.register(Score)
admin.site.register(Task)

