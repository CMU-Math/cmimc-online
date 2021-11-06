from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import ugettext_lazy as _
from django.db import models
from website.utils import log


class UserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        print("creating user")
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        print("creating user")
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)

class CompetitorManager(models.Manager):
    def getCompetitor(self, exam, mathlete):
        try:
            team = mathlete.teams.filter(contest=exam.contest).first()
            if exam.is_team_exam:
                return self.get(exam=exam, team=team, mathlete=None)
            else:
                return self.get(exam=exam, team=team, mathlete=mathlete)
        except Exception as e:
            log(error=str(e), during='getCompetitor', exam=str(exam), mathlete=str(mathlete))
