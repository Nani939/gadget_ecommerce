from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import CustomUserCreationForm, AddressForm, UserForm, UserProfileForm
from .models import UserProfile

def signup_view(request):
    """
    Handle user signup.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically log in user after signup
            messages.success(request, "Account created successfully!")
            return redirect('shop:home')  # Redirect to homepage or desired URL
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'users/signup.html', {'form': form})

@login_required
def add_address(request):
    """
    Allow logged-in users to add a new address.
    """
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, "Address added successfully!")
            return redirect('shop:checkout')  # Redirect to checkout or desired URL
    else:
        form = AddressForm()
    
    return render(request, 'users/add_address.html', {'form': form})

@login_required
def profile_view(request):
    """
    Display and update user profile and related address/profile info.
    """
    user = request.user

    # Get or create user profile linked to user
    profile_instance, created = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, instance=profile_instance)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()

            profile = profile_form.save(commit=False)
            profile.user = user  # ensure user is set explicitly
            profile.save()

            messages.success(request, "Your profile has been updated!")
            return redirect('users:profile')  # Use app namespace here
    else:
        user_form = UserForm(instance=user)
        profile_form = UserProfileForm(instance=profile_instance)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'users/profile.html', context)
