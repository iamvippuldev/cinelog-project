import datetime
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.db import IntegrityError
from django.test import Client, TestCase
from django.urls import reverse

from .models import Movie, Review, Watchlist

User = get_user_model()


class MovieModelTests(TestCase):
    def setUp(self):
        self.movie = Movie.objects.create(
            title="Interstellar",
            release_year=2014,
            genre="Sci-Fi",
            director="Christopher Nolan",
            synopsis="A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival.",
            poster_url="https://example.com/interstellar.jpg",
        )

    def test_movie_str(self):
        self.assertEqual(str(self.movie), "Interstellar (2014)")

    def test_movie_ordering(self):
        older_movie = Movie.objects.create(
            title="Memento",
            release_year=2000,
            director="Christopher Nolan",
        )
        movies = list(Movie.objects.all())
        self.assertEqual(movies[0], self.movie)
        self.assertEqual(movies[1], older_movie)


class ReviewModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="filmfan", password="securepassword123")
        self.movie = Movie.objects.create(
            title="Parasite",
            release_year=2019,
            genre="Thriller",
            director="Bong Joon-ho",
        )

    def test_create_review(self):
        review = Review.objects.create(
            user=self.user,
            movie=self.movie,
            rating=5.0,
            review_text="Absolute cinema.",
            watched_date=datetime.date(2026, 1, 15),
        )
        self.assertEqual(str(review), "filmfan - Parasite (5.0/5)")
        self.assertEqual(self.user.reviews.count(), 1)
        self.assertEqual(self.movie.reviews.count(), 1)

    def test_rating_validation(self):
        review_high = Review(
            user=self.user,
            movie=self.movie,
            rating=5.5,
        )
        with self.assertRaises(ValidationError):
            review_high.full_clean()

        review_low = Review(
            user=self.user,
            movie=self.movie,
            rating=0.5,
        )
        with self.assertRaises(ValidationError):
            review_low.full_clean()


class WatchlistModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="viewer", password="password")
        self.movie = Movie.objects.create(
            title="Dune: Part Two",
            release_year=2024,
            genre="Sci-Fi",
            director="Denis Villeneuve",
        )

    def test_add_to_watchlist(self):
        item = Watchlist.objects.create(user=self.user, movie=self.movie)
        self.assertEqual(str(item), "viewer -> Dune: Part Two")
        self.assertIn(item, self.user.watchlist.all())
        self.assertIn(item, self.movie.watchlist_entries.all())

    def test_duplicate_watchlist_entry_forbidden(self):
        Watchlist.objects.create(user=self.user, movie=self.movie)
        with self.assertRaises(IntegrityError):
            Watchlist.objects.create(user=self.user, movie=self.movie)


class AuthAndTemplateTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="cinemabuff", password="ValidPassword123#")

    def test_base_template_anonymous_navbar(self):
        response = self.client.get(reverse('movie_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'CineLog')
        self.assertContains(response, 'Movies')
        self.assertContains(response, 'Watchlist')
        self.assertContains(response, 'Login')
        self.assertContains(response, 'Register')
        self.assertNotContains(response, 'Logout')

    def test_base_template_authenticated_navbar(self):
        self.client.login(username="cinemabuff", password="ValidPassword123#")
        response = self.client.get(reverse('movie_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'cinemabuff')
        self.assertContains(response, 'Logout')
        self.assertNotContains(response, '>Login<')

    def test_login_page_get_and_post(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Welcome Back')

        # Successful login redirects to '/'
        post_response = self.client.post(reverse('login'), {
            'username': 'cinemabuff',
            'password': 'ValidPassword123#',
        })
        self.assertRedirects(post_response, '/')

    def test_logout_post(self):
        self.client.login(username="cinemabuff", password="ValidPassword123#")
        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, '/')

    def test_register_page_get_and_post(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Join CineLog')

        post_response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'StrongPassword2026!',
            'password2': 'StrongPassword2026!',
        })
        self.assertRedirects(post_response, '/')
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_watchlist_requires_login(self):
        response = self.client.get(reverse('watchlist'))
        self.assertRedirects(response, '/login/?next=/watchlist/')

        self.client.login(username="cinemabuff", password="ValidPassword123#")
        auth_response = self.client.get(reverse('watchlist'))
        self.assertEqual(auth_response.status_code, 200)
        self.assertContains(auth_response, 'My Watchlist')


class Step3FeatureTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="critic", password="Password123!")
        self.movie = Movie.objects.create(
            title="Inception",
            release_year=2010,
            genre="Sci-Fi",
            director="Christopher Nolan",
            synopsis="Dream heist thriller.",
            poster_url="https://image.tmdb.org/t/p/w500/oYuLEt3zVCKq57qu2F8dT7NIa6f.jpg",
        )
        self.movie2 = Movie.objects.create(
            title="Vikram",
            release_year=2022,
            genre="Action",
            director="Lokesh Kanagaraj",
            synopsis="A gritty action thriller in the LCU.",
        )

    def test_seed_movies_command(self):
        call_command('seed_movies')
        self.assertGreaterEqual(Movie.objects.count(), 10)
        self.assertTrue(Movie.objects.filter(title="Interstellar").exists())
        self.assertTrue(Movie.objects.filter(title="Leo").exists())
        self.assertTrue(Review.objects.exists())

    def test_movie_list_search(self):
        # Search by title
        response = self.client.get(reverse('movie_list'), {'q': 'Inception'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Inception')
        self.assertNotContains(response, 'Vikram')

        # Search by genre
        response = self.client.get(reverse('movie_list'), {'q': 'Action'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Vikram')
        self.assertNotContains(response, 'Inception')

        # Non-matching search
        response = self.client.get(reverse('movie_list'), {'q': 'NonExistentTitle999'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No Movies Found')

    def test_movie_detail_view_anonymous(self):
        response = self.client.get(reverse('movie_detail', kwargs={'pk': self.movie.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Inception')
        self.assertContains(response, 'Christopher Nolan')
        self.assertContains(response, 'Log in to Add to Watchlist')
        self.assertContains(response, 'Sign in to rate, log, and write a review')

    def test_movie_detail_view_authenticated(self):
        self.client.login(username="critic", password="Password123!")
        response = self.client.get(reverse('movie_detail', kwargs={'pk': self.movie.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Add to Watchlist')
        self.assertContains(response, 'Log & Review This Film')

    def test_review_submission_and_update(self):
        self.client.login(username="critic", password="Password123!")
        url = reverse('movie_detail', kwargs={'pk': self.movie.pk})

        # Submit initial review
        post_response = self.client.post(url, {
            'rating': '4.5',
            'review_text': 'A mind-bending cinematic puzzle!',
            'watched_date': '2026-09-01',
        })
        self.assertRedirects(post_response, url)
        review = Review.objects.get(movie=self.movie, user=self.user)
        self.assertEqual(review.rating, 4.5)
        self.assertEqual(review.review_text, 'A mind-bending cinematic puzzle!')

        # Updating existing review
        update_response = self.client.post(url, {
            'rating': '5.0',
            'review_text': 'Even better on rewatch. Perfect 5 stars.',
            'watched_date': '2026-09-10',
        })
        self.assertRedirects(update_response, url)
        review.refresh_from_db()
        self.assertEqual(review.rating, 5.0)
        self.assertEqual(review.review_text, 'Even better on rewatch. Perfect 5 stars.')
        self.assertEqual(Review.objects.filter(movie=self.movie, user=self.user).count(), 1)

    def test_watchlist_toggle(self):
        toggle_url = reverse('toggle_watchlist', kwargs={'pk': self.movie.pk})

        # Unauthenticated toggle redirects to login
        anon_response = self.client.post(toggle_url)
        self.assertRedirects(anon_response, f'/login/?next={toggle_url}')

        # Authenticated toggle adds to watchlist
        self.client.login(username="critic", password="Password123!")
        add_response = self.client.post(toggle_url)
        self.assertRedirects(add_response, reverse('movie_detail', kwargs={'pk': self.movie.pk}))
        self.assertTrue(Watchlist.objects.filter(user=self.user, movie=self.movie).exists())

        # Second toggle removes from watchlist
        remove_response = self.client.post(toggle_url)
        self.assertRedirects(remove_response, reverse('movie_detail', kwargs={'pk': self.movie.pk}))
        self.assertFalse(Watchlist.objects.filter(user=self.user, movie=self.movie).exists())


class Step4ProfileTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="filmbuff", password="BuffPassword123!")
        self.movie = Movie.objects.create(
            title="Spirited Away",
            release_year=2001,
            genre="Animation",
            director="Hayao Miyazaki",
            synopsis="Magical adventure.",
            poster_url="https://image.tmdb.org/t/p/w500/39wmItIWsg5sZMyRUHLkWBcuVCM.jpg",
        )
        self.review = Review.objects.create(
            user=self.user,
            movie=self.movie,
            rating=5.0,
            review_text="An unforgettable animation masterpiece.",
            watched_date=datetime.date(2026, 9, 12),
        )
        self.watchlist = Watchlist.objects.create(
            user=self.user,
            movie=self.movie,
        )

    def test_profile_requires_login(self):
        # Unauthenticated request redirects to login
        response = self.client.get(reverse('profile'))
        self.assertRedirects(response, '/login/?next=/profile/')

        # my_diary alias also requires login
        alias_response = self.client.get(reverse('my_diary'))
        self.assertRedirects(alias_response, '/login/?next=/my-diary/')

    def test_profile_authenticated_view(self):
        self.client.login(username="filmbuff", password="BuffPassword123!")
        # Profile view redirects to public_profile for the user
        response = self.client.get(reverse('profile'))
        self.assertRedirects(response, reverse('public_profile', kwargs={'username': 'filmbuff'}))

        # Follow to public profile
        public_resp = self.client.get(reverse('public_profile', kwargs={'username': 'filmbuff'}))
        self.assertEqual(public_resp.status_code, 200)

        # User stats
        self.assertContains(public_resp, 'filmbuff')
        self.assertContains(public_resp, 'Films')
        self.assertContains(public_resp, 'Film Collection')
        self.assertContains(public_resp, 'Reviews')

        # Details
        self.assertContains(public_resp, 'Spirited Away')
        self.assertContains(public_resp, 'An unforgettable animation masterpiece.')

        # Watchlist section for own profile
        self.assertContains(public_resp, 'Watchlist')

    def test_navbar_profile_link(self):
        # Anonymous navbar should not have profile link
        anon_resp = self.client.get(reverse('movie_list'))
        self.assertNotContains(anon_resp, 'My Profile / Diary')

        # Authenticated navbar has profile and dropdown links
        self.client.login(username="filmbuff", password="BuffPassword123!")
        auth_resp = self.client.get(reverse('movie_list'))
        self.assertContains(auth_resp, 'Profile')
        self.assertContains(auth_resp, 'My Profile / Diary')
        self.assertContains(auth_resp, reverse('public_profile', kwargs={'username': 'filmbuff'}))


class PublicProfileAndLetterboxdHomeTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username="director_fan", password="FanPassword123!")
        self.user2 = User.objects.create_user(username="viewer_two", password="FanPassword123!")
        self.movie1 = Movie.objects.create(
            title="Interstellar",
            release_year=2014,
            genre="Sci-Fi",
            director="Christopher Nolan",
            synopsis="A journey beyond the stars to save mankind.",
            poster_url="https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg",
        )
        self.movie2 = Movie.objects.create(
            title="Pulp Fiction",
            release_year=1994,
            genre="Crime",
            director="Quentin Tarantino",
            synopsis="Intertwining stories in LA underworld.",
        )
        self.review1 = Review.objects.create(
            user=self.user1,
            movie=self.movie1,
            rating=5.0,
            review_text="Absolute perfection in sound and scale.",
            watched_date=datetime.date(2026, 9, 1),
        )
        self.review2 = Review.objects.create(
            user=self.user1,
            movie=self.movie2,
            rating=4.5,
            review_text="Endlessly quotable dialogue.",
            watched_date=datetime.date(2026, 9, 5),
        )

    def test_home_page_unauthenticated_state(self):
        response = self.client.get(reverse('movie_list'))
        self.assertEqual(response.status_code, 200)

        # Hero section for unauthenticated visitor
        self.assertContains(response, 'Track films you’ve watched. Save those you want to see.')
        self.assertContains(response, 'Get started — it’s free')
        self.assertContains(response, 'Sign In')

        # Showcase of latest films
        self.assertContains(response, 'Latest Films Added to CineLog')
        self.assertContains(response, 'Interstellar')
        self.assertContains(response, 'Pulp Fiction')

    def test_home_page_authenticated_returning_user(self):
        self.client.login(username="director_fan", password="FanPassword123!")
        response = self.client.get(reverse('movie_list'))
        self.assertEqual(response.status_code, 200)

        # Returning user center header
        self.assertContains(response, 'Welcome back, director_fan. Here’s what we’ve been watching...')
        self.assertContains(response, 'This homepage will become customized as you follow active members on CineLog.')

        # LATEST ADDED FILMS carousel
        self.assertContains(response, 'LATEST ADDED FILMS')
        self.assertContains(response, 'Recently added to the collection')
        self.assertContains(response, 'Interstellar')
        self.assertContains(response, 'Pulp Fiction')
        self.assertContains(response, reverse('movie_detail', kwargs={'pk': self.movie1.pk}))
        # No review text or reviewer username in this dedicated movie carousel
        self.assertNotContains(response, 'NEW ON CINELOG')

    def test_home_page_authenticated_new_user(self):
        self.client.login(username="viewer_two", password="FanPassword123!")
        response = self.client.get(reverse('movie_list'))
        self.assertEqual(response.status_code, 200)

        # Brand new user center header
        self.assertContains(response, 'Welcome to CineLog, viewer_two! Start by logging your first film.')

    def test_letterboxd_profile_layout(self):
        self.client.login(username="director_fan", password="FanPassword123!")
        response = self.client.get(reverse('public_profile', kwargs={'username': 'director_fan'}))
        self.assertEqual(response.status_code, 200)

        # Header 100x100 avatar & Edit profile button
        self.assertContains(response, 'profile-avatar-100')
        self.assertContains(response, 'director_fan')
        self.assertContains(response, 'Edit Profile')

        # Counters: Films, Following, Followers
        self.assertContains(response, 'Films')
        self.assertContains(response, 'Following')
        self.assertContains(response, 'Followers')

        # Favorite films placeholder
        self.assertContains(response, 'Favorite Films')
        self.assertContains(response, 'select your favorite films!')
        self.assertIn("Don't forget to select your favorite films!", response.content.decode('utf-8'))

        # Recent activity row
        self.assertContains(response, 'Recent Activity')
        self.assertContains(response, 'Interstellar')
        self.assertContains(response, 'Pulp Fiction')

        # Right sidebar: Ratings histogram, Activity list (PRO card removed)
        self.assertNotContains(response, 'CINELOG PRO')
        self.assertNotContains(response, 'Need an upgrade?')
        self.assertContains(response, 'Ratings')
        self.assertContains(response, 'histogram-container')
        self.assertContains(response, 'Activity')

        # Modal trigger present
        self.assertContains(response, 'data-bs-toggle="modal"')
        self.assertContains(response, 'data-bs-target="#editProfileModal"')

    def test_public_profile_view_for_other_user(self):
        self.client.login(username="viewer_two", password="FanPassword123!")
        response = self.client.get(reverse('public_profile', kwargs={'username': 'director_fan'}))
        self.assertEqual(response.status_code, 200)

        # User stats
        self.assertContains(response, 'director_fan')
        self.assertContains(response, 'Follow')
        self.assertContains(response, '2')  # 2 films logged
        self.assertContains(response, '4.8')  # avg rating

        # Other user's watchlist should be private
        self.assertContains(response, 'Private Watchlist')

    def test_movie_detail_review_links_to_public_profile(self):
        response = self.client.get(reverse('movie_detail', kwargs={'pk': self.movie1.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('public_profile', kwargs={'username': 'director_fan'}))

    def test_public_profile_404_for_nonexistent_user(self):
        response = self.client.get(reverse('public_profile', kwargs={'username': 'ghost_user_999'}))
        self.assertEqual(response.status_code, 404)

    def test_edit_profile_submission_and_redirect(self):
        self.client.login(username="director_fan", password="FanPassword123!")

        # Edit profile with new username, display name, avatar, bio
        edit_data = {
            'first_name': 'Christopher',
            'last_name': 'Nolan',
            'username': 'nolan_fan',
            'avatar_url': 'https://example.com/avatar.jpg',
            'bio': 'Cinema is a mirror of our dreams.',
        }
        response = self.client.post(reverse('edit_profile'), data=edit_data)
        # Should redirect to the new username's profile URL
        self.assertRedirects(response, reverse('public_profile', kwargs={'username': 'nolan_fan'}))

        # Check DB updates
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.username, 'nolan_fan')
        self.assertEqual(self.user1.first_name, 'Christopher')
        self.assertEqual(self.user1.last_name, 'Nolan')
        self.assertEqual(self.user1.profile.avatar_url, 'https://example.com/avatar.jpg')
        self.assertEqual(self.user1.profile.bio, 'Cinema is a mirror of our dreams.')

        # Follow redirect and verify display on profile page
        profile_page = self.client.get(reverse('public_profile', kwargs={'username': 'nolan_fan'}))
        self.assertEqual(profile_page.status_code, 200)
        self.assertContains(profile_page, 'Christopher Nolan')
        self.assertContains(profile_page, '@nolan_fan')
        self.assertContains(profile_page, 'Cinema is a mirror of our dreams.')
        self.assertContains(profile_page, 'https://example.com/avatar.jpg')

    def test_navbar_smooth_scroll_and_carousel(self):
        self.client.login(username="director_fan", password="FanPassword123!")
        response = self.client.get(reverse('movie_list'))
        self.assertEqual(response.status_code, 200)

        # Check navbar link to #explore-films with id
        self.assertContains(response, 'href="/#explore-films"')
        self.assertContains(response, 'id="nav-movies-link"')
        self.assertContains(response, 'sticky-top')
        self.assertContains(response, 'navbar-cinelog')

        # Check explore-films section id and scroll-margin-top
        self.assertContains(response, 'id="explore-films"')
        self.assertContains(response, 'scroll-margin-top: 90px;')

        # Check html/body scroll freeze fix
        self.assertContains(response, 'overflow-y: auto !important;')

        # Check carousel attributes for auto-sliding every 3s
        self.assertContains(response, 'id="latestMoviesCarousel"')
        self.assertContains(response, 'data-bs-ride="carousel"')
        self.assertContains(response, 'data-bs-interval="3000"')
        self.assertContains(response, 'data-bs-pause="hover"')
        self.assertContains(response, 'carousel-indicators')
        self.assertContains(response, 'carousel-control-prev')
        self.assertContains(response, 'carousel-control-next')

        # Check subtle dark border on carousel card
        self.assertContains(response, 'border: 1px solid #2a3440;')


class AIRecommendationsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="ai_cinephile", password="Password123!")

        # Create movies with varied genres and directors
        self.interstellar = Movie.objects.create(
            title="Interstellar",
            release_year=2014,
            genre="Sci-Fi",
            director="Christopher Nolan",
            synopsis="A team of explorers travel through a wormhole in space to save humanity.",
            poster_url="https://example.com/interstellar.jpg"
        )
        self.inception = Movie.objects.create(
            title="Inception",
            release_year=2010,
            genre="Sci-Fi",
            director="Christopher Nolan",
            synopsis="A thief who steals corporate secrets through dream-sharing technology.",
            poster_url="https://example.com/inception.jpg"
        )
        self.dune = Movie.objects.create(
            title="Dune: Part Two",
            release_year=2024,
            genre="Sci-Fi",
            director="Denis Villeneuve",
            synopsis="Paul Atreides unites with Chani and the Fremen to seek revenge against the Harkonnens.",
            poster_url="https://example.com/dune2.jpg"
        )
        self.the_hangover = Movie.objects.create(
            title="The Hangover",
            release_year=2009,
            genre="Comedy",
            director="Todd Phillips",
            synopsis="Three buddies wake up from a bachelor party in Las Vegas with no memory.",
            poster_url="https://example.com/hangover.jpg"
        )

    def test_recommendations_triggered_by_high_ratings(self):
        from .recommendations import get_movie_recommendations

        # Rate Interstellar 5.0 stars (Sci-Fi, Christopher Nolan)
        Review.objects.create(
            user=self.user,
            movie=self.interstellar,
            rating=5.0,
            review_text="Absolute masterpiece!"
        )

        recs = get_movie_recommendations(self.user, limit=3)
        self.assertTrue(len(recs) > 0)

        # Inception (Christopher Nolan + Sci-Fi) should rank highest among unreviewed films
        top_rec = recs[0]
        self.assertEqual(top_rec['movie'], self.inception)
        self.assertIn("Interstellar", top_rec['reason'])
        self.assertGreaterEqual(top_rec['match_percentage'], 80)
        self.assertIn("% Match", top_rec['match_score_str'])

    def test_already_watched_movies_excluded(self):
        from .recommendations import get_movie_recommendations

        # User has reviewed both Interstellar and Inception
        Review.objects.create(user=self.user, movie=self.interstellar, rating=5.0)
        Review.objects.create(user=self.user, movie=self.inception, rating=4.5)

        recs = get_movie_recommendations(self.user, limit=5)
        rec_movies = [r['movie'] for r in recs]

        # Neither Interstellar nor Inception should appear in recommendations
        self.assertNotIn(self.interstellar, rec_movies)
        self.assertNotIn(self.inception, rec_movies)

    def test_watchlist_fallback_when_no_high_ratings(self):
        from .recommendations import get_movie_recommendations

        # User rates a movie low (2.0 stars), but has Dune: Part Two in Watchlist
        Review.objects.create(user=self.user, movie=self.the_hangover, rating=2.0)
        Watchlist.objects.create(user=self.user, movie=self.dune)

        recs = get_movie_recommendations(self.user, limit=3)
        self.assertTrue(len(recs) > 0)

        # Recommendation reason should reflect Watchlist origin
        matched_reasons = [r['reason'] for r in recs]
        self.assertTrue(any("Watchlist" in r or "Dune" in r for r in matched_reasons))

    def test_community_fallback_for_anonymous_or_new_user(self):
        from .recommendations import get_movie_recommendations

        # No ratings, no watchlist
        recs = get_movie_recommendations(None, limit=3)
        self.assertTrue(len(recs) > 0)
        self.assertIn("% Match", recs[0]['match_score_str'])

    def test_home_page_ai_recommendation_section(self):
        # Create 5.0 star review to trigger personalized recommendations
        Review.objects.create(user=self.user, movie=self.interstellar, rating=5.0)
        self.client.login(username="ai_cinephile", password="Password123!")

        response = self.client.get(reverse('movie_list'))
        self.assertEqual(response.status_code, 200)

        # Check AI Recommended section headers
        self.assertContains(response, '🤖 AI RECOMMENDED FOR YOU')
        self.assertContains(response, 'Tailored from your 4★ &amp; 5★ watch history')
        self.assertContains(response, 'View All AI Picks &amp; Explanations')
        self.assertContains(response, 'Inception')

    def test_dedicated_recommendations_page(self):
        Review.objects.create(user=self.user, movie=self.interstellar, rating=5.0)
        self.client.login(username="ai_cinephile", password="Password123!")

        response = self.client.get(reverse('recommendations'))
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, 'AI Movie Recommendations')
        self.assertContains(response, 'WHY THIS WAS RECOMMENDED')
        self.assertContains(response, 'Scikit-Learn')
        self.assertContains(response, 'Inception')

    def test_navbar_ai_picks_link(self):
        response = self.client.get(reverse('movie_list'))
        self.assertEqual(response.status_code, 200)

        # Navbar should have AI Picks link
        self.assertContains(response, 'href="/recommendations/"')
        self.assertContains(response, 'AI Picks')


class AvatarFileUploadTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="avatar_tester",
            password="SecurePassword123!",
            first_name="Avatar",
            last_name="Tester"
        )
        self.client = Client()

    def _create_test_image(self, name="avatar.png", color=(0, 224, 84)):
        import io
        from PIL import Image
        from django.core.files.uploadedfile import SimpleUploadedFile

        img_io = io.BytesIO()
        image = Image.new("RGB", (100, 100), color=color)
        image.save(img_io, format="PNG")
        img_io.seek(0)
        return SimpleUploadedFile(name, img_io.getvalue(), content_type="image/png")

    def test_avatar_file_upload_success(self):
        self.client.login(username="avatar_tester", password="SecurePassword123!")
        test_file = self._create_test_image("my_new_avatar.png")

        response = self.client.post(
            reverse('public_profile', kwargs={'username': 'avatar_tester'}),
            {
                'edit_profile_submit': '1',
                'first_name': 'UpdatedAvatar',
                'last_name': 'Tester',
                'username': 'avatar_tester',
                'bio': 'Film director with uploaded picture.',
                'avatar': test_file,
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.user.profile.refresh_from_db()

        # Check avatar field saved
        self.assertTrue(bool(self.user.profile.avatar))
        self.assertIn('/media/avatars/', self.user.profile.avatar.url)
        self.assertIn(self.user.profile.avatar.url, self.user.profile.avatar_display_url)

        # Check HTML renders the uploaded image
        self.assertContains(response, self.user.profile.avatar.url)

    def test_edit_profile_modal_renders_enctype_and_file_input(self):
        self.client.login(username="avatar_tester", password="SecurePassword123!")
        response = self.client.get(reverse('public_profile', kwargs={'username': 'avatar_tester'}))
        self.assertEqual(response.status_code, 200)

        # Verify form has enctype="multipart/form-data"
        self.assertContains(response, 'enctype="multipart/form-data"')
        # Verify file input is present
        self.assertContains(response, '<input type="file" name="avatar"')
        self.assertContains(response, 'accept="image/*"')

    def test_avatar_silhouette_fallback_when_no_image(self):
        self.client.login(username="avatar_tester", password="SecurePassword123!")
        response = self.client.get(reverse('public_profile', kwargs={'username': 'avatar_tester'}))
        self.assertEqual(response.status_code, 200)

        # When no avatar is uploaded, fallback icon is rendered
        self.assertContains(response, 'bi-person-fill')





