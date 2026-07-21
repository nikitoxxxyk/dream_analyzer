from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from dream_api.models import Dream
from .forms import RegisterForm
from django.contrib.auth import login

def home(request):
	return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

@login_required
def dashboard(request):
	# Получаем сны текущего пользователя
	dreams = Dream.objects.filter(user_id=request.user.id).order_by('-created_at')[:10]
	return render(request, 'dashboard.html', {'dreams': dreams})

@login_required
def dream_detail(request, dream_id):
	dream = Dream.objects.get(id=dream_id, user_id=request.user.id)
	return render(request, 'dream_detail.html', {'dream':dream})


