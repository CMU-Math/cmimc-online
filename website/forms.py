from django.contrib.auth.forms import UserCreationForm as DefaultUserCreationForm
from django.contrib.auth.forms import UserChangeForm as DefaultUserChangeForm
from website.models import User
import datetime
from django import forms
from django_ace import AceWidget


class UserCreationForm(DefaultUserCreationForm):
    CHOICES = [
        (User.MATHLETE, 'Student'),
        (User.COACH, 'Coach'),
    ]
    role = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES, label=' ')

    class Meta(DefaultUserCreationForm):
        model = User
        fields = ('full_name', 'email', 'role')

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.fields['password1'].help_text = '<ul>' \
                '<li>8 characters minimum</li></ul>'
        self.fields['full_name'].help_text = None
        self.fields['password2'].help_text = None
        self.fields['full_name'].widget.attrs['autofocus'] = ''


class UserChangeForm(DefaultUserChangeForm):
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'full_name', 'alias', 'role')

class EditorForm(forms.Form):
    text = forms.CharField(
        widget=AceWidget(
            mode='python',
            theme='xcode',
            fontsize='18px',
            width="100%",
            height="50vh",
            toolbar=False,
        ),
        label='Code Here!',
        required=False,
    )

class ViewOnlyEditorForm(forms.Form):
    text = forms.CharField(
        widget=AceWidget(
            mode='python',
            theme='katzenmilch',
            fontsize='18px',
            width="100%",
            height="50vh",
            toolbar=False,
            readonly=True,
            showgutter=False,
        ),
        label='Note: Read-Only!',
        required=False,
    )

class TncForm(forms.Form):
    signature = forms.CharField(min_length = 2, max_length = 100)
    guardian_signature = forms.CharField(required = False, min_length = 2, max_length = 100)
    guardian_email = forms.EmailField(required = False)
    date = forms.DateField(initial=datetime.date.today)
