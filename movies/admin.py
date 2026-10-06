from django.contrib import admin
from .models import Movie, Review, Watchlist


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'release_year', 'genre', 'director', 'created_at')
    list_filter = ('genre', 'release_year')
    search_fields = ('title', 'director', 'genre', 'synopsis')
    ordering = ('-release_year', 'title')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('movie', 'user', 'rating', 'watched_date', 'created_at')
    list_filter = ('rating', 'watched_date', 'created_at')
    search_fields = ('movie__title', 'user__username', 'review_text')
    ordering = ('-created_at',)


@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('user__username', 'movie__title')
    ordering = ('-added_at',)


from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'avatar_url', 'bio')
    search_fields = ('user__username', 'bio')
