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
        widgets ={

            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control","rows": 5}),
            "priority": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "assigned_to": forms.Select(attrs={"class": "form-select"}),
        }


class TicketUpdateForm(forms.ModelForm):

    class Meta:
        model = Ticket

        fields = [
            "status",
            "assigned_to"
        ]

        widgets = {
            "status": forms.Select(attrs={"class": "form-select"}),
            "assigned_to": forms.Select(attrs={"class": "form-select"}),
        }


class TicketCommentForm(forms.ModelForm):

    class Meta:
        model = TicketComment

        fields = ["comment"]

        widgets = {
            "comment": forms.Textarea(attrs={"class": "form-control","rows": 4,"placeholder": "Add update notes..."}),
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