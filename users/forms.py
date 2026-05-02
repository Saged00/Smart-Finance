from django import forms
from django.contrib.auth import authenticate
from .models import User


class RegisterForm(forms.ModelForm):
    password  = forms.CharField(widget=forms.PasswordInput, min_length=8)

    class Meta:
        model  = User
        fields = ['full_name', 'email', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email    = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        email    = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        self.user = authenticate(username=email, password=password)
        if self.user is None:
            raise forms.ValidationError("Invalid email or password. Please try again.")
        return self.cleaned_data