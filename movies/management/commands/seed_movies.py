import datetime
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from movies.models import Movie, Review

User = get_user_model()

MOVIES_DATA = [
    {
        "title": "Interstellar",
        "release_year": 2014,
        "genre": "Sci-Fi",
        "director": "Christopher Nolan",
        "synopsis": "When Earth becomes uninhabitable in the future, a farmer and ex-NASA pilot, Joseph Cooper, is tasked to pilot a spacecraft along with a team of researchers to find a new planet for humans.",
        "poster_url": "https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg",
    },
    {
        "title": "Inception",
        "release_year": 2010,
        "genre": "Sci-Fi",
        "director": "Christopher Nolan",
        "synopsis": "A skilled thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.",
        "poster_url": "https://image.tmdb.org/t/p/w500/oYuLEt3zVCKq57qu2F8dT7NIa6f.jpg",
    },
    {
        "title": "The Dark Knight",
        "release_year": 2008,
        "genre": "Action",
        "director": "Christopher Nolan",
        "synopsis": "When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.",
        "poster_url": "https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg",
    },
    {
        "title": "Vikram",
        "release_year": 2022,
        "genre": "Action",
        "director": "Lokesh Kanagaraj",
        "synopsis": "A special agent investigates a murder committed by a masked group of serial killers. However, a tangled maze of clues leads him to the drug kingpin of Chennai.",
        "poster_url": "https://upload.wikimedia.org/wikipedia/en/9/93/Vikram_2022_poster.jpg",
    },
    {
        "title": "Leo",
        "release_year": 2023,
        "genre": "Action",
        "director": "Lokesh Kanagaraj",
        "synopsis": "Parthiban is a mild-mannered cafe owner in Kashmir who fends off a gang of murderous thugs. His newfound fame inadvertently brings him to the attention of a ruthless crime syndicate who believe he is their estranged son.",
        "poster_url": "https://upload.wikimedia.org/wikipedia/en/7/75/Leo_%282023_Indian_film%29.jpg",
    },
    {
        "title": "Parasite",
        "release_year": 2019,
        "genre": "Thriller",
        "director": "Bong Joon-ho",
        "synopsis": "Greed and class discrimination threaten the newly formed symbiotic relationship between the wealthy Park family and the destitute Kim clan.",
        "poster_url": "https://image.tmdb.org/t/p/w500/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg",
    },
    {
        "title": "Dune: Part Two",
        "release_year": 2024,
        "genre": "Sci-Fi",
        "director": "Denis Villeneuve",
        "synopsis": "Paul Atreides unites with Chani and the Fremen while seeking revenge against the conspirators who destroyed his family. Facing a choice between the love of his life and the fate of the universe.",
        "poster_url": "https://image.tmdb.org/t/p/w500/1pdfLvkbY9ohJlCjQH2CZjjYVvJ.jpg",
    },
    {
        "title": "Spirited Away",
        "release_year": 2001,
        "genre": "Animation",
        "director": "Hayao Miyazaki",
        "synopsis": "During her family's move to the suburbs, a sullen 10-year-old girl wanders into a world ruled by gods, witches and spirits, a world where humans are changed into beasts.",
        "poster_url": "https://image.tmdb.org/t/p/w500/39wmItIWsg5sZMyRUHLkWBcuVCM.jpg",
    },
    {
        "title": "Whiplash",
        "release_year": 2014,
        "genre": "Drama",
        "director": "Damien Chazelle",
        "synopsis": "A promising young drummer enrolls at a cut-throat music conservatory where his dreams of greatness are mentored by an instructor who will stop at nothing to realize a student's potential.",
        "poster_url": "https://image.tmdb.org/t/p/w500/7fn624j5lj3xTme2SgiLCeuedmO.jpg",
    },
    {
        "title": "Pulp Fiction",
        "release_year": 1994,
        "genre": "Crime",
        "director": "Quentin Tarantino",
        "synopsis": "The lives of two mob hitmen, a boxer, a gangster and his wife, and a pair of diner bandits intertwine in four tales of violence and redemption.",
        "poster_url": "https://image.tmdb.org/t/p/w500/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg",
    },
]


class Command(BaseCommand):
    help = "Seed popular movies and initial review data into the database"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Starting movie seeding..."))

        created_count = 0
        for item in MOVIES_DATA:
            movie, created = Movie.objects.update_or_create(
                title=item["title"],
                release_year=item["release_year"],
                defaults={
                    "genre": item["genre"],
                    "director": item["director"],
                    "synopsis": item["synopsis"],
                    "poster_url": item["poster_url"],
                },
            )
            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully seeded {len(MOVIES_DATA)} movies ({created_count} newly created)."
            )
        )

        # Seed sample user and reviews if none exist
        demo_user, _ = User.objects.get_or_create(
            username="cinephile",
            defaults={"email": "cinephile@cinelog.app"},
        )

        sample_reviews = [
            ("Interstellar", 5.0, "An emotional, breathtaking cosmic journey with Zimmer's greatest score.", datetime.date(2026, 8, 10)),
            ("The Dark Knight", 5.0, "Heath Ledger gives an iconic, timeless performance. Peak superhero cinema.", datetime.date(2026, 8, 12)),
            ("Vikram", 4.5, "Lokesh Kanagaraj crafts a high-octane cinematic universe thriller with Kamal Haasan in top form.", datetime.date(2026, 8, 20)),
            ("Parasite", 5.0, "Flawless screenwriting and direction. Masterclass in tension and social satire.", datetime.date(2026, 9, 1)),
            ("Inception", 4.5, "Complex, gripping narrative that stays with you long after the spinning top drops.", datetime.date(2026, 9, 5)),
        ]

        for title, rating, text, watched in sample_reviews:
            try:
                m = Movie.objects.get(title=title)
                Review.objects.update_or_create(
                    user=demo_user,
                    movie=m,
                    defaults={
                        "rating": rating,
                        "review_text": text,
                        "watched_date": watched,
                    },
                )
            except Movie.DoesNotExist:
                pass

        self.stdout.write(self.style.SUCCESS("Sample reviews loaded successfully."))
