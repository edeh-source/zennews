from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, LoginForm
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth import logout


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST, request.FILES)
        if user_form.is_valid():
            cd = user_form.cleaned_data
            new_user = user_form.save(commit=False)
            new_user.set_password(cd['password'])
            new_user.save()
            messages.success(request, 'ACCOUNT CREATED SUCCESFULLY NOW LOGIN')
            return redirect('login')
        else:
            messages.error(request, 'CORRECT THE ERROR BELOW')
    else:
        user_form = UserRegistrationForm()  
    return render(request, 'news/register.html', {'user_form': user_form })              


def users_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, email=cd['email'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.success(request, 'LOGGED IN SUCCESFULLY')
                    request.session['logged_user'] = str(user)
                    print(user)
                    return redirect('home')
                else:
                    messages.error(request, 'ACCOUNT IS NOT ACTIVE')
            else:
                messages.error(request, 'ACCOUNT DOES NOT EXIST')
        else:
            messages.error(request, 'CORRECT THE ERROR BELOW')
    else:
        form = LoginForm()
    return render(request, 'news/login.html', {'form': form })                                



def logout_view(request):
    logout(request)
    return redirect('login')

