from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

class ProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email')  # add your user fields here
# users/views.py

from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # or wherever you want to redirect after signup
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/signup.html', {'form': form})
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import CustomUser  # your custom user model

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email')  # or any fields your CustomUser has
