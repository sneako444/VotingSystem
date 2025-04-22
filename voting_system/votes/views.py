# votes/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .models import Candidate, Vote, Result
from django.db.models import Count
from django.http import JsonResponse
from django.db.models import Count, Sum
def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('vote')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'login.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect('home')

@login_required
def vote(request):
    if request.method == 'POST':
        candidate_id = request.POST.get('candidate')
        candidate = Candidate.objects.get(id=candidate_id)
        
        # Check if user already voted for this candidate
        if Vote.objects.filter(user=request.user, candidate=candidate).exists():
            messages.warning(request, 'You have already voted for this candidate!')
        else:
            Vote.objects.create(user=request.user, candidate=candidate)
            messages.success(request, 'Your vote has been recorded!')
        return redirect('vote')
    
    candidates = Candidate.objects.all()
    user_votes = Vote.objects.filter(user=request.user).values_list('candidate', flat=True)
    return render(request, 'vote.html', {'candidates': candidates, 'user_votes': user_votes})


@login_required
# votes/views.py
def results(request):
    # Option 1: If your model already has a votes_count field
    results = Result.objects.filter(is_published=True)\
                  .select_related('candidate')
    total_votes = sum(result.votes_count for result in results) or 1
    
    # OR Option 2: If you need to count votes from related model
    # results = Result.objects.filter(is_published=True)\
    #           .select_related('candidate')\
    #           .annotate(vote_count=Count('vote'))  # Different name
    # total_votes = results.aggregate(total=Sum('vote_count'))['total'] or 1

    context = {
        'results': results,
        'total_votes': total_votes
    }
    return render(request, 'results.html', context)

def is_admin(user):
    return user.is_superuser

@user_passes_test(is_admin)
def admin_dashboard(request):
    candidates = Candidate.objects.annotate(vote_count=Count('vote'))
    
    # Prepare data for charts
    chart_data = {
        'labels': [c.name for c in candidates],
        'data': [c.vote_count for c in candidates],
    }
    
    return render(request, 'dashboard.html', {
        'candidates': candidates,
        'chart_data': chart_data,
        'total_votes': sum(c.vote_count for c in candidates),
    })

def get_vote_data(request):
    candidates = Candidate.objects.annotate(vote_count=Count('vote'))
    data = {
        'labels': [c.name for c in candidates],
        'datasets': [{
            'label': 'Votes',
            'data': [c.vote_count for c in candidates],
            'backgroundColor': [
                'rgba(255, 99, 132, 0.7)',
                'rgba(54, 162, 235, 0.7)',
                'rgba(255, 206, 86, 0.7)',
                'rgba(75, 192, 192, 0.7)',
                'rgba(153, 102, 255, 0.7)',
            ],
        }]
    }
    return JsonResponse(data)