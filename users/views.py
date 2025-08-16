from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .forms import CustomUserCreationForm  # Make sure this form is defined in forms.py

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically log in user after signup
            messages.success(request, "Account created successfully!")
            return redirect('shop:home')  # Redirect to your homepage or desired URL
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'users/signup.html', {'form': form})


# You can add more views like login, logout, profile, etc. here as needed.
