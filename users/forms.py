from django import forms
from django.contrib.auth import authenticate
from .models import User


class RegisterForm(forms.ModelForm):
    """
    Form for new user registration.
    Handles user data collection and ensures secure password storage using hashing.
    """
    password  = forms.CharField(widget=forms.PasswordInput, min_length=8)

    class Meta:
        model  = User
        fields = ['full_name', 'email', 'password']

    def save(self, commit=True):
        """
        Overrides the save method to hash the password before saving the user 
        to the database.
        """
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    """
    Form for user authentication.
    Validates credentials against the database using Django's authentication system.
    """
    email    = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        """
        Authenticates the user based on provided email and password.
        Raises a validation error if authentication fails.
        """
        email    = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        self.user = authenticate(username=email, password=password)
        if self.user is None:
            raise forms.ValidationError("Invalid email or password. Please try again.")
        return self.cleaned_data