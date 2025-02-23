from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
import re
from django.core.exceptions import ValidationError
from .models import Song


class SongForm(forms.ModelForm):
    class Meta:
        model = Song
        fields = ['title', 'file']


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    contact_number = forms.CharField(max_length=15, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'contact_number', 'password1', 'password2']

    # Custom validation for username
    def clean_username(self):
        username = self.cleaned_data['username']
        # Check if username contains only allowed characters (letters, digits, @, ., _)
        if not re.match("^[a-zA-Z0-9@._]+$", username):
            raise ValidationError('Username must be alphanumeric or an email address.')
        return username

    # Custom validation for password strength
    def clean_password1(self):
        password = self.cleaned_data['password1']
        # Ensure the password meets the complexity requirements
        if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', password):
            raise ValidationError(
                'Password must be at least 8 characters long and contain at least one letter, one number, and one special character.'
            )
        return password

    # Check if password and username are the same
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        username = cleaned_data.get("username")

        # If passwords match the username, raise validation error
        if password1 and username and password1 == username:
            raise ValidationError('Password and username cannot be the same.')

        # Ensure password and confirm password match
        password2 = cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError('Passwords do not match.')

        return cleaned_data
