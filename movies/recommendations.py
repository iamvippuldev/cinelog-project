"""
movies/recommendations.py

AI-Powered Content-Based Movie Recommendation Engine using scikit-learn.
Analyzes user watch and rating history (specifically 4★ and 5★ films),
falls back to Watchlist items or top-rated community films,
computes TF-IDF metadata feature soups, and determines cosine similarity.
"""

from typing import List, Dict, Any, Optional, Set
import numpy as np
from django.db.models import Avg, Count
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from movies.models import Movie, Review, Watchlist


def create_movie_soup(movie: Movie) -> str:
    """
    Constructs a rich text soup combining genre, director, title, and synopsis.
    Important categorical features (genre, director) are repeated to give them
    higher weight in TF-IDF vector space.
    """
    genre = (movie.genre or '').strip()
    director = (movie.director or '').strip()
    synopsis = (movie.synopsis or '').strip()
    title = (movie.title or '').strip()

    # Weight genre 3x, director 2x, title 1x, synopsis 1x
    return f"{genre} {genre} {genre} {director} {director} {title} {synopsis}".strip()


def calculate_match_percentage(sim: float, base_min: int = 72, target_max: int = 98) -> int:
    """
    Maps raw cosine similarity score (typically between 0.05 and 0.45)
    to a realistic user-facing AI match percentage (72% - 98%).
    """
    if sim <= 0.01:
        return base_min
    # Assume 0.40+ raw similarity represents near-perfect genre/director/thematic overlap
    ratio = min(1.0, sim / 0.40)
    pct = round(base_min + (ratio * (target_max - base_min)))
    return int(max(base_min, min(target_max, pct)))


def get_movie_recommendations(user=None, limit: int = 6) -> List[Dict[str, Any]]:
    """
    Generates content-based AI movie recommendations tailored for the given user.

    Steps:
    1. Identify watched movies to exclude.
    2. Collect seed movies (rated >= 4.0 by user -> watchlist -> community top-rated).
    3. Build TF-IDF feature matrix from all movie metadata soups.
    4. Compute cosine similarity between candidate movies and seed movies.
    5. Formulate human-readable AI explanation reasons and match percentages.
    6. Return top `limit` recommendations.
    """
    all_movies = list(
        Movie.objects.annotate(
            avg_rating=Avg('reviews__rating'),
            review_count=Count('reviews'),
        ).all()
    )

    if not all_movies:
        return []

    watched_ids: Set[int] = set()
    watchlist_ids: Set[int] = set()
    seed_movies: List[Movie] = []
    seed_ratings: Dict[int, float] = {}
    source_type = 'trending'

    if user and user.is_authenticated:
        watched_ids = set(user.reviews.values_list('movie_id', flat=True))
        watchlist_ids = set(user.watchlist.values_list('movie_id', flat=True))

        # 1. Primary: Movies rated >= 4 stars by user
        high_reviews = user.reviews.filter(rating__gte=4.0).select_related('movie')
        if high_reviews.exists():
            seed_movies = [r.movie for r in high_reviews]
            seed_ratings = {r.movie_id: r.rating for r in high_reviews}
            source_type = 'ratings'
        else:
            # 2. Fallback: Watchlist movies
            user_watchlist = user.watchlist.select_related('movie')
            if user_watchlist.exists():
                seed_movies = [w.movie for w in user_watchlist]
                seed_ratings = {w.movie_id: 4.5 for w in user_watchlist}
                source_type = 'watchlist'

    # 3. Final fallback: If no high ratings and no watchlist items, or anonymous user
    if not seed_movies:
        # Fallback to top-rated / trending community films
        top_community = [
            m for m in sorted(
                all_movies,
                key=lambda x: (x.avg_rating or 0, x.review_count or 0, x.release_year),
                reverse=True
            )
            if m.id not in watched_ids
        ]
        # Use top 3-4 as seeds
        seed_movies = top_community[:4]
        seed_ratings = {m.id: 5.0 for m in seed_movies}
        source_type = 'trending'

    # Candidates are all movies not already watched by the user
    candidates = [m for m in all_movies if m.id not in watched_ids]
    if not candidates:
        return []

    # If seed_movies has no overlap with candidate movies (normal case)
    # Build corpus of all movies
    corpus = [create_movie_soup(m) for m in all_movies]
    movie_to_idx = {m.id: i for i, m in enumerate(all_movies)}

    tfidf = TfidfVectorizer(stop_words='english', min_df=1)
    tfidf_matrix = tfidf.fit_transform(corpus)

    seed_indices = [movie_to_idx[s.id] for s in seed_movies if s.id in movie_to_idx]
    if not seed_indices:
        # Emergency fallback: just return candidates sorted by rating
        candidates.sort(
            key=lambda x: (x.avg_rating or 0, x.review_count or 0, x.release_year),
            reverse=True
        )
        return [
            {
                'movie': m,
                'match_percentage': 95 - (i * 2),
                'match_score_str': f"{95 - (i * 2)}% Match",
                'reason': "CineLog Community Masterpiece",
                'explanation_detail': "Consistently ranked among the highest-rated films by the CineLog community.",
                'in_watchlist': m.id in watchlist_ids,
            }
            for i, m in enumerate(candidates[:limit])
        ]

    seed_vectors = tfidf_matrix[seed_indices]

    scored_candidates = []
    for candidate in candidates:
        c_idx = movie_to_idx[candidate.id]
        c_vector = tfidf_matrix[c_idx]

        sims = cosine_similarity(c_vector, seed_vectors)[0]
        best_seed_idx = int(np.argmax(sims))
        raw_sim = float(sims[best_seed_idx])
        matched_seed = seed_movies[best_seed_idx]
        seed_rating = seed_ratings.get(matched_seed.id, 4.0)

        # Weighted similarity score accounting for seed rating and director/genre exact match
        weighted_score = raw_sim * (seed_rating / 4.5)

        # Build informative explanation based on source_type
        if source_type == 'ratings':
            if candidate.director and candidate.director.lower() == matched_seed.director.lower():
                reason = f"Because you loved {matched_seed.title} by {candidate.director}"
                explanation = (
                    f"Strong cinematic match: Shares director {candidate.director} "
                    f"and {candidate.genre} style with your {seed_rating:g}★ rated {matched_seed.title}."
                )
            elif candidate.genre and matched_seed.genre and any(g in matched_seed.genre for g in candidate.genre.split()):
                reason = f"Because you liked {matched_seed.title} ({matched_seed.genre})"
                explanation = (
                    f"Thematic match: Highly aligned {candidate.genre} narrative and tone "
                    f"similar to {matched_seed.title}."
                )
            else:
                reason = f"Because you liked {matched_seed.title}"
                explanation = f"Recommended based on content similarity with {matched_seed.title}."
        elif source_type == 'watchlist':
            reason = f"Based on {matched_seed.title} in your Watchlist"
            explanation = (
                f"Shares core {candidate.genre} genre traits and storytelling elements "
                f"with {matched_seed.title} from your watchlist."
            )
        else:
            reason = "CineLog Community Top-Rated Pick"
            explanation = "Curated based on acclaim, high ratings, and thematic popularity on CineLog."

        match_pct = calculate_match_percentage(raw_sim)

        scored_candidates.append({
            'movie': candidate,
            'raw_sim': raw_sim,
            'weighted_score': weighted_score,
            'match_percentage': match_pct,
            'match_score_str': f"{match_pct}% Match",
            'reason': reason,
            'explanation_detail': explanation,
            'matched_seed': matched_seed,
            'in_watchlist': candidate.id in watchlist_ids,
        })

    # Sort descending by weighted score and raw similarity
    scored_candidates.sort(
        key=lambda x: (x['weighted_score'], x['raw_sim'], x['movie'].avg_rating or 0),
        reverse=True
    )

    # Ensure match percentages are in neat descending order
    # (e.g. 96%, 94%, 91%, 88%, 85%, 83%)
    results = scored_candidates[:limit]
    if results:
        max_pct = max(r['match_percentage'] for r in results)
        cur_pct = max(max_pct, 94)
        for i, item in enumerate(results):
            if i > 0 and item['match_percentage'] >= results[i - 1]['match_percentage']:
                item['match_percentage'] = max(70, results[i - 1]['match_percentage'] - 2)
            item['match_score_str'] = f"{item['match_percentage']}% Match"

    return results


def get_recommendations_context(user) -> Dict[str, Any]:
    """
    Returns full recommendation context for the dedicated /recommendations/ page.
    """
    recommendations = get_movie_recommendations(user=user, limit=12)

    has_high_ratings = False
    has_watchlist = False
    favorite_seeds = []

    if user and user.is_authenticated:
        high_reviews = user.reviews.filter(rating__gte=4.0).select_related('movie')
        has_high_ratings = high_reviews.exists()
        if has_high_ratings:
            favorite_seeds = [r.movie for r in high_reviews[:4]]
        else:
            wl = user.watchlist.select_related('movie')
            has_watchlist = wl.exists()
            if has_watchlist:
                favorite_seeds = [w.movie for w in wl[:4]]

    return {
        'recommendations': recommendations,
        'has_high_ratings': has_high_ratings,
        'has_watchlist': has_watchlist,
        'favorite_seeds': favorite_seeds,
    }
