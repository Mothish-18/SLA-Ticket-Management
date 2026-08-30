from django import forms
from .models import Ticket,TicketComment
from django.contrib.auth.models import User
from django.contrib.auth.forms import *

class TicketForm(forms.ModelForm):

    class Meta:
        model = Ticket

        fields = [
            "title",
            "description",
            "priority",
            "assigned_to",
        ]

        widgets = {

            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter ticket title"
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 6,
                    "placeholder": "Describe the issue in detail..."
                }
            ),

            "priority": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "assigned_to": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        user = kwargs.pop("user", None)

        super().__init__(*args, **kwargs)

        self.fields["assigned_to"].queryset = (
            User.objects.filter(
                groups__name__iexact="Support Engineer"
            ).distinct()
        )

        self.fields["assigned_to"].empty_label = (
            "Select Engineer"
        )

        if (
            user and
            user.groups.filter(
                name__iexact="Support Engineer"
            ).exists()
        ):

            self.fields["assigned_to"].queryset = (
                self.fields["assigned_to"]
                .queryset
                .exclude(id=user.id)
            )

class TicketUpdateForm(forms.ModelForm):

    class Meta:

        model = Ticket

        fields = [
            "status",
            "assigned_to"
        ]

        widgets = {

            "status": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "assigned_to": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["assigned_to"].queryset = (
            User.objects.filter(
                groups__name__iexact="Support Engineer"
            ).distinct()
        )

        self.fields["assigned_to"].empty_label = (
            "Select Engineer"
        )
        
class TicketCommentForm(forms.ModelForm):

    class Meta:

        model = TicketComment

        fields = ["comment"]

        widgets = {

            "comment": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Add update, investigation notes, or resolution details..."
                }
            ),

        }
class RegisterForm(UserCreationForm):

    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control"}))

    class Meta:
        model = User

        fields = [
            "username",
            "email",
            "password1",
            "password2"
        ]

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["username"].widget.attrs.update(
            {
                "class": "form-control"
            }
        )

        self.fields["password1"].widget.attrs.update(
            {
                "class": "form-control"
            }
        )

        self.fields["password2"].widget.attrs.update(
            {
                "class": "form-control"
            }
        )