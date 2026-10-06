from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt

from .forms import EditProfileForm, RegisterForm, ReviewForm
from .models import Movie, Profile, Review, Watchlist
from .recommendations import get_movie_recommendations, get_recommendations_context

User = get_user_model()


def movie_list(request):
    query = request.GET.get('q', '').strip()
    movies = Movie.objects.annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews'),
    )

    if query:
        movies = movies.filter(
            Q(title__icontains=query) |
            Q(genre__icontains=query) |
            Q(director__icontains=query)
        )

    # 5 latest movies for home carousel and showcase
    latest_movies = Movie.objects.order_by('-created_at')[:5]

    # Authenticated user review count
    user_reviews_count = 0
    if request.user.is_authenticated:
        user_reviews_count = request.user.reviews.count()

    # 6 most recent community reviews for "NEW ON CINELOG"
    new_on_cinelog = (
        Review.objects.select_related('user', 'movie')
        .order_by('-created_at')[:6]
    )
    new_on_cinelog_list = list(new_on_cinelog)
    new_on_cinelog_chunks = []
    if new_on_cinelog_list:
        chunk_size = 3
        for i in range(0, len(new_on_cinelog_list), chunk_size):
            new_on_cinelog_chunks.append(new_on_cinelog_list[i:i + chunk_size])

    # Highest-rated film for fallback/spotlight
    spotlight_movie = (
        Movie.objects.annotate(
            avg_rating=Avg('reviews__rating'),
            review_count=Count('reviews'),
        )
        .filter(avg_rating__isnull=False)
        .order_by('-avg_rating', '-release_year')
        .first()
    )
    if not spotlight_movie:
        spotlight_movie = Movie.objects.first()

    # AI-powered recommendations for logged-in users
    ai_recommendations = []
    if request.user.is_authenticated:
        ai_recommendations = get_movie_recommendations(request.user, limit=6)

    return render(request, 'movies/movie_list.html', {
        'movies': movies,
        'query': query,
        'spotlight_movie': spotlight_movie,
        'latest_movies': latest_movies,
        'user_reviews_count': user_reviews_count,
        'new_on_cinelog': new_on_cinelog,
        'new_on_cinelog_chunks': new_on_cinelog_chunks,
        'recent_reviews': new_on_cinelog,
        'ai_recommendations': ai_recommendations,
    })


def recommendations_view(request):
    """
    Dedicated AI Movie Recommendations page with comprehensive similarity
    explanations, seed film origins, and match percentages.
    """
    context = get_recommendations_context(request.user)
    return render(request, 'movies/recommendations.html', context)


@csrf_exempt
def movie_detail(request, pk):
    movie = get_object_or_404(
        Movie.objects.annotate(
            avg_rating=Avg('reviews__rating'),
            review_count=Count('reviews'),
        ),
        pk=pk,
    )
    reviews = movie.reviews.select_related('user').order_by('-created_at')

    in_watchlist = False
    user_review = None
    form = None

    if request.user.is_authenticated:
        in_watchlist = request.user.watchlist.filter(movie=movie).exists()
        user_review = movie.reviews.filter(user=request.user).first()

        if request.method == 'POST':
            form = ReviewForm(request.POST, instance=user_review)
            if form.is_valid():
                review = form.save(commit=False)
                review.user = request.user
                review.movie = movie
                review.save()
                messages.success(
                    request,
                    "Your review has been updated!" if user_review else "Your review has been posted!"
                )
                return redirect('movie_detail', pk=movie.pk)
        else:
            form = ReviewForm(instance=user_review)

    return render(request, 'movies/movie_detail.html', {
        'movie': movie,
        'reviews': reviews,
        'in_watchlist': in_watchlist,
        'user_review': user_review,
        'form': form,
    })


@csrf_exempt
@login_required
def toggle_watchlist(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    if request.method == 'POST':
        item = Watchlist.objects.filter(user=request.user, movie=movie)
        if item.exists():
            item.delete()
            messages.info(request, f"Removed '{movie.title}' from your watchlist.")
        else:
            Watchlist.objects.create(user=request.user, movie=movie)
            messages.success(request, f"Added '{movie.title}' to your watchlist.")

    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER')
    if next_url:
        return redirect(next_url)
    return redirect('movie_detail', pk=movie.pk)


@login_required
def watchlist_view(request):
    watchlist_items = request.user.watchlist.select_related('movie').all()
    return render(request, 'movies/watchlist.html', {'watchlist_items': watchlist_items})


@csrf_exempt
def register_view(request):
    if request.user.is_authenticated:
        return redirect('movie_list')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to CineLog, {user.username}! Your account has been created.")
            return redirect(settings.LOGIN_REDIRECT_URL)
    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {'form': form})


@csrf_exempt
def login_view(request):
    if request.user.is_authenticated:
        return redirect(settings.LOGIN_REDIRECT_URL)

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.POST.get('next') or request.GET.get('next') or settings.LOGIN_REDIRECT_URL
            return redirect(next_url)
    else:
        form = AuthenticationForm(request)

    return render(request, 'registration/login.html', {
        'form': form,
        'next': request.GET.get('next', ''),
    })


@csrf_exempt
def logout_view(request):
    logout(request)
    return redirect(settings.LOGOUT_REDIRECT_URL)


@login_required
def profile_view(request):
    return redirect('public_profile', username=request.user.username)


@csrf_exempt
def public_profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    Profile.objects.get_or_create(user=profile_user)

    is_own_profile = bool(request.user.is_authenticated and request.user == profile_user)
    edit_form = None

    if is_own_profile:
        if request.method == 'POST' and ('edit_profile_submit' in request.POST or 'username' in request.POST):
            edit_form = EditProfileForm(request.POST, request.FILES, user=request.user)
            if edit_form.is_valid():
                updated_user = edit_form.save()
                messages.success(request, "Your profile has been updated successfully!")
                return redirect('public_profile', username=updated_user.username)
        else:
            edit_form = EditProfileForm(user=request.user)

    user_reviews = profile_user.reviews.select_related('movie').order_by('-watched_date', '-created_at')

    films_watched_count = user_reviews.values('movie').distinct().count()
    total_reviews_count = user_reviews.count()
    avg_rating_agg = user_reviews.aggregate(Avg('rating'))['rating__avg']
    avg_rating_given = round(avg_rating_agg, 1) if avg_rating_agg is not None else None

    watchlist_items = profile_user.watchlist.select_related('movie').order_by('-added_at') if is_own_profile else None
    watchlist_count = profile_user.watchlist.count()

    # 4 most recent reviews by user for "RECENT ACTIVITY"
    recent_user_reviews = list(user_reviews[:4])

    # Calculate rating distribution for histogram (1 to 5 stars)
    histogram_data = []
    # Count reviews grouped by rounded star rating (1 to 5)
    counts_by_star = {star: 0 for star in range(1, 6)}
    for r in user_reviews:
        star = max(1, min(5, round(r.rating)))
        counts_by_star[star] += 1

    max_star_count = max(counts_by_star.values()) if counts_by_star.values() else 0
    for star in range(1, 6):
        cnt = counts_by_star[star]
        pct = int((cnt / max_star_count) * 100) if max_star_count > 0 else 0
        histogram_data.append({
            'star': star,
            'count': cnt,
            'pct': pct,
        })

    # Favorite films: empty list so placeholder "Don't forget to select your favorite films!" renders
    favorite_films = []

    return render(request, 'movies/public_profile.html', {
        'profile_user': profile_user,
        'user_reviews': user_reviews,
        'recent_user_reviews': recent_user_reviews,
        'films_watched_count': films_watched_count,
        'total_reviews_count': total_reviews_count,
        'avg_rating_given': avg_rating_given,
        'is_own_profile': is_own_profile,
        'watchlist_items': watchlist_items,
        'watchlist_count': watchlist_count,
        'histogram_data': histogram_data,
        'favorite_films': favorite_films,
        'following_count': 0,
        'followers_count': 0,
        'edit_form': edit_form,
    })


@csrf_exempt
@login_required
def edit_profile_view(request):
    Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            updated_user = form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('public_profile', username=updated_user.username)
        else:
            for error_list in form.errors.values():
                for err in error_list:
                    messages.error(request, err)
    return redirect('public_profile', username=request.user.username)

