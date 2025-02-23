from django.core.mail import send_mail
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import views as auth_views
from .forms import CustomUserCreationForm  # If you're using a custom form

from django.shortcuts import render, get_object_or_404
from .utils import get_spotify_client
from django.shortcuts import render, redirect
from .utils import get_song_details

from django.shortcuts import render, redirect
from .models import Song
from .forms import SongForm
from django.shortcuts import redirect
from django.http import JsonResponse
from django.conf import settings
import spotipy
from spotipy.oauth2 import SpotifyOAuth


def spotify_callback(request):
    code = request.GET.get("code")

    if not code:
        return JsonResponse({"error": "Authorization code not found"}, status=400)

    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI,
        scope="user-library-read"
    )

    token_info = sp_oauth.get_access_token(code)
    request.session["spotify_token"] = token_info  # Store token in session

    return redirect("/callback/")  # Redirect to home page or a success page


def upload_song(request):
    if request.method == 'POST':
        form = SongForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = SongForm()
    return render(request, 'upload.html', {'form': form})


def home(request):
    songs = [
        {
            "id": "7KtC4pUL3kI1EUXt29m1vU",
            "title": "Butta Bomma",
            "artist": "Armaan Malik",
            "image": "https://i.scdn.co/image/ab67616d00004851b6e6e7f60e97e3c67ebd2dc8",
            "spotify_url": "https://open.spotify.com/track/7KtC4pUL3kI1EUXt29m1vU"
        },
        {
            "id": "2dpaYNEQHiRxtZbfNsse99",
            "title": "Tum Hi Ho",
            "artist": "Arijit Singh",
            "image": "https://i.scdn.co/image/ab67616d0000485154df6075b34e019dca9a5b53",
            "spotify_url": "https://open.spotify.com/track/2dpaYNEQHiRxtZbfNsse99"
        }
    ]
    return render(request, "index.html", {"songs": songs})


def play_song(request, song_id):
    song = get_song_details(song_id)
    return render(request, "player.html", {"song": song})


# Registration View
def user_register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Save the user data but don't commit it to the database yet
            user = form.save(commit=False)
            user.save()

            # Send a verification email (simple example)
            send_mail(
                'Verify Your Email Address',
                'Thank you for registering! Please verify your email by clicking the link below.',
                'hasinianem660@gmail.com',  # This should be the email address from which you want to send emails
                [user.email],  # User's email where the verification email will be sent
                fail_silently=False,  # Set to False to raise errors if the email fails to send
            )

            # Inform the user to check their email for the verification link
            messages.success(request, 'Account created successfully! Please check your email for verification.')

            # Redirect to login page after successful registration
            return redirect('user_login')

        else:
            # If the form is not valid, show error messages
            messages.error(request, 'Please correct the errors below.')
    else:
        # Create an empty form if the request is GET
        form = CustomUserCreationForm()

    return render(request, 'register.html', {'form': form})


# views.py
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']  # Assuming you're using 'username' for login
        password = request.POST['password']  # Change this to 'password' instead of 'password1'

        # Check credentials logic here...
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/home')  # Or wherever you want to redirect after successful login
        else:
            # Handle invalid credentials
            messages.error(request, "Invalid login credentials.")
            return redirect('/login')  # Or the appropriate redirect on error
    return render(request, 'login.html')


def dashboard(request):
    return render(request, 'dashboard.html')


def play_song(request, song_id):
    sp = get_spotify_client(request)  # Pass 'request'

    if sp is None:
        return render(request, "error.html", {"message": "Spotify authentication required."})

    song = sp.track(song_id)  # Fetch song details from Spotify
    return render(request, "play.html", {"song": song})
