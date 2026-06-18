import requests
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import SearchHistory
from .forms import RegisterForm # सुनिश्चित करें कि यह फॉर्म आपकी forms.py में बना हुआ है

WEATHER_API = settings.WEATHER_API_KEY

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = RegisterForm()
    return render(request, 'temperature/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'temperature/index.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('user_login')

@login_required(login_url='user_login')
def index(request):
    weather = None
    error = None
    recent_searches = SearchHistory.objects.order_by('-searched_at')[:5]

    if request.method == 'POST':
        query = request.POST.get('query', '').strip()
        category = request.POST.get('category')
        url = f"https://api.openweathermap.org/data/2.5/weather?q={query}&appid={WEATHER_API}&units=metric"
        resp = requests.get(url)

        if resp.status_code == 200:
            data = resp.json()
            if category == 'Map':
                weather = {'city': data['name'], 'lat': data['coord']['lat'], 'lon': data['coord']['lon'], 'is_map': True}
            else:
                weather = {
                    'city': data['name'], 'temperature': data['main']['temp'], 
                    'humidity': data['main']['humidity'], 
                    'description': data['weather'][0]['description'].title(), 
                    'is_map': False
                }
                SearchHistory.objects.create(city_name=weather['city'], temperature=weather['temperature'])
        else:
            error = "City not found!"
            
    return render(request, 'temperature/index.html', {
        'weather': weather, 'error': error, 
        'recent_searches': recent_searches
    })