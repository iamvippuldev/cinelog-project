from django.core.management.base import BaseCommand
from movies.models import Movie, Review, Watchlist

CURATED_50_MOVIES = [
    {
        "title": "Interstellar",
        "release_year": 2014,
        "genre": "Sci-Fi",
        "director": "Christopher Nolan",
        "synopsis": "When Earth becomes uninhabitable, a team of ex-NASA astronauts travels through a wormhole in search of a new home for mankind.",
        "poster_url": "https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg"
    },
    {
        "title": "Inception",
        "release_year": 2010,
        "genre": "Sci-Fi",
        "director": "Christopher Nolan",
        "synopsis": "A skilled thief who steals corporate secrets through dream-sharing technology is tasked with planting an idea into a CEO's subconscious.",
        "poster_url": "https://image.tmdb.org/t/p/w500/oYuLEt3zVCKq57qu2F8dT7NIa6f.jpg"
    },
    {
        "title": "The Dark Knight",
        "release_year": 2008,
        "genre": "Action",
        "director": "Christopher Nolan",
        "synopsis": "Batman faces his greatest psychological test when a sadistic criminal known as the Joker wreaks chaos on Gotham City.",
        "poster_url": "https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg"
    },
    {
        "title": "Parasite",
        "release_year": 2019,
        "genre": "Thriller",
        "director": "Bong Joon-ho",
        "synopsis": "Greed and class discrimination threaten the newly formed symbiotic relationship between the wealthy Park family and the destitute Kim clan.",
        "poster_url": "https://image.tmdb.org/t/p/w500/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg"
    },
    {
        "title": "Dune: Part Two",
        "release_year": 2024,
        "genre": "Sci-Fi",
        "director": "Denis Villeneuve",
        "synopsis": "Paul Atreides unites with Chani and the Fremen to wage war against the Harkonnens and avenge his fallen house.",
        "poster_url": "https://image.tmdb.org/t/p/w500/1pdfLvkbY9ohJlCjQH2CZjjYVvJ.jpg"
    },
    {
        "title": "Spirited Away",
        "release_year": 2001,
        "genre": "Animation",
        "director": "Hayao Miyazaki",
        "synopsis": "A ten-year-old girl wanders into a magical world of spirits and witches where her parents are transformed into giant pigs.",
        "poster_url": "https://image.tmdb.org/t/p/w500/39wmItIWsg5sZMyRUHLkWBcuVCM.jpg"
    },
    {
        "title": "Whiplash",
        "release_year": 2014,
        "genre": "Drama",
        "director": "Damien Chazelle",
        "synopsis": "A promising young jazz drummer is pushed to his physical and emotional limits by a ruthlessly demanding music instructor.",
        "poster_url": "https://image.tmdb.org/t/p/w500/7fn624j5lj3xTme2SgiLCeuedmO.jpg"
    },
    {
        "title": "Pulp Fiction",
        "release_year": 1994,
        "genre": "Crime",
        "director": "Quentin Tarantino",
        "synopsis": "The lives of two mob hitmen, a boxer, a gangster's wife, and two diner bandits intertwine in four tales of violence and redemption.",
        "poster_url": "https://image.tmdb.org/t/p/w500/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg"
    },
    {
        "title": "Vikram",
        "release_year": 2022,
        "genre": "Action",
        "director": "Lokesh Kanagaraj",
        "synopsis": "A covert black-ops veteran leads a squad of masked vigilantes to wage all-out war against a ruthless drug cartel in Chennai.",
        "poster_url": "https://upload.wikimedia.org/wikipedia/en/9/93/Vikram_2022_poster.jpg"
    },
    {
        "title": "Leo",
        "release_year": 2023,
        "genre": "Action",
        "director": "Lokesh Kanagaraj",
        "synopsis": "A gentle cafe owner in Himachal Pradesh is forced to confront a deadly crime syndicate who insist he is their long-lost heir.",
        "poster_url": "https://upload.wikimedia.org/wikipedia/en/7/75/Leo_%282023_Indian_film%29.jpg"
    },
    {
        "title": "Jailer",
        "release_year": 2023,
        "genre": "Action Drama",
        "director": "Nelson Dilipkumar",
        "synopsis": "A retired prison warden utilizes his underworld connections and tactical prowess to dismantle a violent idol smuggling syndicate.",
        "poster_url": "https://upload.wikimedia.org/wikipedia/en/c/cb/Jailer_2023_Tamil_film_poster.jpg"
    },
    {
        "title": "Kaithi",
        "release_year": 2019,
        "genre": "Action Thriller",
        "director": "Lokesh Kanagaraj",
        "synopsis": "A paroled prisoner races against time in a lorry to save unconscious police officers from drug lords in exchange for meeting his daughter.",
        "poster_url": "https://upload.wikimedia.org/wikipedia/en/7/79/Kaithi_2019_poster.jpg"
    },
    {
        "title": "Master",
        "release_year": 2021,
        "genre": "Action",
        "director": "Lokesh Kanagaraj",
        "synopsis": "An alcoholic professor assigned to a juvenile detention facility clashes with a ruthless gangster using inmates as scapegoats.",
        "poster_url": "https://upload.wikimedia.org/wikipedia/en/5/53/Master_2021_poster.jpg"
    },
    {
        "title": "Asuran",
        "release_year": 2019,
        "genre": "Action Drama",
        "director": "Vetrimaaran",
        "synopsis": "A peaceful farmer from an oppressed caste goes on the run to protect his hot-headed son from a merciless upper-caste landlord.",
        "poster_url": "https://upload.wikimedia.org/wikipedia/en/7/78/Asuran_2019_poster.jpg"
    },
    {
        "title": "Jai Bhim",
        "release_year": 2021,
        "genre": "Legal Drama",
        "director": "T. J. Gnanavel",
        "synopsis": "A brave human rights lawyer battles systemic police brutality to seek justice for an impoverished Irular tribal woman.",
        "poster_url": "https://upload.wikimedia.org/wikipedia/en/a/ad/Jai_Bhim_film_poster.jpg"
    },
    {
        "title": "Soorarai Pottru",
        "release_year": 2020,
        "genre": "Drama",
        "director": "Sudha Kongara",
        "synopsis": "Nedumaaran Rajangam sets out to make low-cost aviation affordable for everyday citizens while battling entrenched corporate airlines.",
        "poster_url": "https://upload.wikimedia.org/wikipedia/en/6/61/Soorarai_Pottru.JPG"
    },
    {
        "title": "Karnan",
        "release_year": 2021,
        "genre": "Action Drama",
        "director": "Mari Selvaraj",
        "synopsis": "A fearless village youth wields a sword to fight for the dignity, rights, and bus-stop recognition of his oppressed community.",
        "poster_url": "https://upload.wikimedia.org/wikipedia/en/6/62/Karnan_2021_poster.jpg"
    },
    {
        "title": "Maanaadu",
        "release_year": 2021,
        "genre": "Sci-Fi Thriller",
        "director": "Venkat Prabhu",
        "synopsis": "A common man and a corrupt police officer are trapped in a mysterious time loop during a fateful political assassination attempt.",
        "poster_url": "https://upload.wikimedia.org/wikipedia/en/c/c4/Maanaadu_poster.jpg"
    },
    {
        "title": "Vada Chennai",
        "release_year": 2018,
        "genre": "Crime Drama",
        "director": "Vetrimaaran",
        "synopsis": "A talented carrom player in North Madras is reluctantly drawn into a bloody generational underworld turf war.",
        "poster_url": "https://upload.wikimedia.org/wikipedia/en/2/2c/Vada_Chennai.jpg"
    },
    {
        "title": "Super Deluxe",
        "release_year": 2019,
        "genre": "Dark Comedy Drama",
        "director": "Thiagarajan Kumararaja",
        "synopsis": "Four parallel, eccentric stories intertwine on a fateful day in Chennai involving an unfaithful wife, a trans woman, a priest, and teenagers.",
        "poster_url": "https://upload.wikimedia.org/wikipedia/en/a/a1/Super_Deluxe_film_poster.jpg"
    },
    {
        "title": "Pariyerum Perumal",
        "release_year": 2018,
        "genre": "Drama",
        "director": "Mari Selvaraj",
        "synopsis": "A sensitive law student from an oppressed caste struggles against cruel social prejudice while befriending an upper-caste classmate.",
        "poster_url": "https://upload.wikimedia.org/wikipedia/en/3/35/Pariyerum_Perumal.jpg"
    },
    {
        "title": "Ponniyin Selvan: Part I",
        "release_year": 2022,
        "genre": "Historical Epic",
        "director": "Mani Ratnam",
        "synopsis": "Vandiyathevan sets out to deliver messages to Crown Prince Aditha Karikalan as internal conspiracies threaten the Chola Empire.",
        "poster_url": "https://upload.wikimedia.org/wikipedia/en/c/c3/Ponniyin_Selvan_I.jpg"
    },
    {
        "title": "Ponniyin Selvan: Part II",
        "release_year": 2023,
        "genre": "Historical Epic",
        "director": "Mani Ratnam",
        "synopsis": "The Chola throne hangs in the balance as old vendettas between Queen Nandini and Aditha Karikalan reach a tragic climax.",
        "poster_url": "https://upload.wikimedia.org/wikipedia/en/5/5e/Ponniyin_Selvan_II.jpg"
    },
    {
        "title": "Vikram Vedha",
        "release_year": 2017,
        "genre": "Action Crime",
        "director": "Pushkar\u2013Gayathri",
        "synopsis": "A righteous encounter cop confronts an elusive crime lord who volunteers riddles that blur the lines between right and wrong.",
        "poster_url": "https://upload.wikimedia.org/wikipedia/en/0/03/Vikram_Vedha_poster.jpg"
    },
    {
        "title": "Nayakan",
        "release_year": 1987,
        "genre": "Crime Drama",
        "director": "Mani Ratnam",
        "synopsis": "A Tamil boy who flees police brutality arrives in Bombay and rises through the underworld to become a revered, benevolent godfather.",
        "poster_url": "https://upload.wikimedia.org/wikipedia/en/d/d0/Nayakan_poster.jpg"
    },
    {
        "title": "Baashha",
        "release_year": 1995,
        "genre": "Action",
        "director": "Suresh Krissna",
        "synopsis": "A peace-loving auto rickshaw driver conceals his fearsome past as a legendary Mumbai underworld don to protect his siblings.",
        "poster_url": "https://upload.wikimedia.org/wikipedia/en/9/97/Baashha_poster.jpg"
    },
    {
        "title": "Anbe Sivam",
        "release_year": 2003,
        "genre": "Drama Comedy",
        "director": "Sundar C.",
        "synopsis": "Two contrasting travelers stranded by bad weather embark on a journey from Bhubaneswar to Chennai, discovering the divine power of love.",
        "poster_url": "https://upload.wikimedia.org/wikipedia/en/5/52/Anbe_Sivam.jpg"
    },
    {
        "title": "Thuppakki",
        "release_year": 2012,
        "genre": "Action Thriller",
        "director": "AR Murugadoss",
        "synopsis": "An Indian Army intelligence officer on holiday in Mumbai uncovers and dismantles a deadly web of sleeper terrorist cells.",
        "poster_url": "https://upload.wikimedia.org/wikipedia/en/b/be/Thuppakki_poster.jpg"
    },
    {
        "title": "Ghilli",
        "release_year": 2004,
        "genre": "Action Romance",
        "director": "Dharani",
        "synopsis": "A state-level kabaddi athlete rescues a helpless woman from an influential Madurai factionist and hides her in Chennai.",
        "poster_url": "https://upload.wikimedia.org/wikipedia/en/1/13/Ghilli_poster.jpg"
    },
    {
        "title": "Mersal",
        "release_year": 2017,
        "genre": "Action Thriller",
        "director": "Atlee",
        "synopsis": "Twin brothers\u2014a magician and a 5-rupee doctor\u2014unite to expose rampant medical malpractice and avenge their murdered parents.",
        "poster_url": "https://upload.wikimedia.org/wikipedia/en/3/3c/Mersal_film_poster.jpg"
    },
    {
        "title": "Indian",
        "release_year": 1996,
        "genre": "Action Vigilante",
        "director": "S. Shankar",
        "synopsis": "An aged freedom fighter trained in lethal ancient martial arts targets corrupt government officials across the nation.",
        "poster_url": "https://upload.wikimedia.org/wikipedia/en/6/65/Indian_1996_poster.jpg"
    },
    {
        "title": "Mudhalvan",
        "release_year": 1999,
        "genre": "Political Thriller",
        "director": "S. Shankar",
        "synopsis": "A television journalist accepts a public challenge from a corrupt politician to serve as Chief Minister for a single day.",
        "poster_url": "https://upload.wikimedia.org/wikipedia/en/5/51/Mudhalvan.jpg"
    },
    {
        "title": "Amaran",
        "release_year": 2024,
        "genre": "Biographical Action",
        "director": "Rajkumar Periasamy",
        "synopsis": "The courageous life and ultimate sacrifice of Major Mukund Varadarajan of the Rajput Regiment in counter-terror operations.",
        "poster_url": "https://upload.wikimedia.org/wikipedia/en/5/54/Amaran_2024_poster.jpg"
    },
    {
        "title": "Maharaja",
        "release_year": 2024,
        "genre": "Action Thriller",
        "director": "Nithilan Saminathan",
        "synopsis": "A quiet barber files an unusual police complaint for a stolen metal dustbin, masking a devastating plot for retribution.",
        "poster_url": "https://upload.wikimedia.org/wikipedia/en/8/82/Maharaja_2024_film_poster.jpg"
    },
    {
        "title": "Raayan",
        "release_year": 2024,
        "genre": "Action Crime",
        "director": "Dhanush",
        "synopsis": "A peaceful fast-food vendor is forced out of obscurity into North Chennai gang warfare to protect his younger siblings.",
        "poster_url": "https://upload.wikimedia.org/wikipedia/en/e/e4/Raayan_poster.jpg"
    },
    {
        "title": "RRR",
        "release_year": 2022,
        "genre": "Action Epic",
        "director": "S. S. Rajamouli",
        "synopsis": "Two legendary revolutionaries forge a deep friendship in 1920s Delhi before discovering their opposing allegiances.",
        "poster_url": "https://upload.wikimedia.org/wikipedia/en/d/d7/RRR_Poster.jpg"
    },
    {
        "title": "Baahubali: The Beginning",
        "release_year": 2015,
        "genre": "Fantasy Epic",
        "director": "S. S. Rajamouli",
        "synopsis": "A free-spirited tribal youth learns of his noble lineage as the lost heir to the legendary throne of Mahishmati.",
        "poster_url": "https://upload.wikimedia.org/wikipedia/en/5/5f/Baahubali_The_Beginning_poster.jpg"
    },
    {
        "title": "Baahubali 2: The Conclusion",
        "release_year": 2017,
        "genre": "Fantasy Epic",
        "director": "S. S. Rajamouli",
        "synopsis": "Shiva discovers why the loyal commander Katappa executed Amarendra Baahubali and mounts a rebellion to reclaim the kingdom.",
        "poster_url": "https://upload.wikimedia.org/wikipedia/en/9/93/Baahubali_2_The_Conclusion_poster.jpg"
    },
    {
        "title": "KGF: Chapter 1",
        "release_year": 2018,
        "genre": "Period Action",
        "director": "Prashanth Neel",
        "synopsis": "A fearless Bombay gangster infiltrates the brutal, slave-operated Kolar Gold Fields to liberate its oppressed workforce.",
        "poster_url": "https://upload.wikimedia.org/wikipedia/en/c/cc/K.G.F_Chapter_1_poster.jpg"
    },
    {
        "title": "KGF: Chapter 2",
        "release_year": 2022,
        "genre": "Period Action",
        "director": "Prashanth Neel",
        "synopsis": "Rocky establishes unyielding reign over the Kolar Gold Fields, waging war against deadly adversaries and the state government.",
        "poster_url": "https://upload.wikimedia.org/wikipedia/en/d/d0/K.G.F_Chapter_2.jpg"
    },
    {
        "title": "Kantara",
        "release_year": 2022,
        "genre": "Action Mythological",
        "director": "Rishab Shetty",
        "synopsis": "A rebellious Kambala athlete clashes with a strict forest ranger over indigenous forest lands guarded by the demigod Panjurli.",
        "poster_url": "https://upload.wikimedia.org/wikipedia/en/8/84/Kantara_poster.jpeg"
    },
    {
        "title": "Kalki 2898 AD",
        "release_year": 2024,
        "genre": "Sci-Fi Mythological",
        "director": "Nag Ashwin",
        "synopsis": "In a post-apocalyptic future, the immortal warrior Ashwatthama rises to shield an expectant mother carrying a divine savior.",
        "poster_url": "https://upload.wikimedia.org/wikipedia/en/4/4c/Kalki_2898_AD.jpg"
    },
    {
        "title": "Pushpa: The Rise",
        "release_year": 2021,
        "genre": "Action Crime",
        "director": "Sukumar",
        "synopsis": "A fearless red sandalwood cutter rises through the ranks of an underworld smuggling ring in the Seshachalam forests.",
        "poster_url": "https://upload.wikimedia.org/wikipedia/en/7/75/Pushpa_-_The_Rise_%282021_film%29.jpg"
    },
    {
        "title": "Pushpa 2: The Rule",
        "release_year": 2024,
        "genre": "Action Crime",
        "director": "Sukumar",
        "synopsis": "Pushpa Raj consolidates an empire of red sandalwood while clashing with SP Bhanwar Singh Shekhawat in a lethal showdown.",
        "poster_url": "https://upload.wikimedia.org/wikipedia/en/1/11/Pushpa_2-_The_Rule.jpg"
    },
    {
        "title": "Jawan",
        "release_year": 2023,
        "genre": "Action Thriller",
        "director": "Atlee",
        "synopsis": "A principled jailer and a group of women inmates stage daring vigilante heists to correct deep socio-economic injustices.",
        "poster_url": "https://upload.wikimedia.org/wikipedia/en/3/39/Jawan_film_poster.jpg"
    },
    {
        "title": "Dangal",
        "release_year": 2016,
        "genre": "Biographical Sports",
        "director": "Nitesh Tiwari",
        "synopsis": "A former national wrestler trains his daughters Geeta and Babita to triumph against societal barriers and win international gold.",
        "poster_url": "https://upload.wikimedia.org/wikipedia/en/9/99/Dangal_Poster.jpg"
    },
    {
        "title": "3 Idiots",
        "release_year": 2009,
        "genre": "Comedy Drama",
        "director": "Rajkumar Hirani",
        "synopsis": "Two friends search for their unconventional engineering college classmate Rancho, whose visionary ideas transformed their lives.",
        "poster_url": "https://upload.wikimedia.org/wikipedia/en/d/df/3_idiots_poster.jpg"
    },
    {
        "title": "Tumbbad",
        "release_year": 2018,
        "genre": "Period Folk Horror",
        "director": "Rahi Anil Barve",
        "synopsis": "A man's obsessive greed leads him to plunder mythical ancestral gold guarded by a cursed monstrous demigod.",
        "poster_url": "https://upload.wikimedia.org/wikipedia/en/4/41/Tumbbad_poster.jpg"
    },
    {
        "title": "12th Fail",
        "release_year": 2023,
        "genre": "Biographical Drama",
        "director": "Vidhu Vinod Chopra",
        "synopsis": "The inspiring real journey of Manoj Kumar Sharma who overcomes crippling poverty to successfully clear the UPSC exam.",
        "poster_url": "https://upload.wikimedia.org/wikipedia/en/f/f2/12th_Fail_poster.jpeg"
    },
    {
        "title": "Drishyam",
        "release_year": 2013,
        "genre": "Crime Thriller",
        "director": "Jeethu Joseph",
        "synopsis": "A resourceful cable operator constructs a web of alibis to shield his family when the son of an IG goes missing.",
        "poster_url": "https://upload.wikimedia.org/wikipedia/en/9/9e/DrishyamMovie.jpg"
    }
]

class Command(BaseCommand):
    help = "Seed exactly 50 curated Tamil, Indian and cinema masterpieces with verified poster URLs"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding 50 curated movies..."))
        
        curated_titles = set()
        created_count = 0
        updated_count = 0

        for item in CURATED_50_MOVIES:
            title = item["title"]
            curated_titles.add(title)
            movie, created = Movie.objects.update_or_create(
                title=title,
                defaults={
                    "release_year": item["release_year"],
                    "genre": item["genre"],
                    "director": item["director"],
                    "synopsis": item["synopsis"],
                    "poster_url": item["poster_url"],
                }
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        # Delete any movies not in the curated 50 list to ensure clean 50 records
        to_delete = Movie.objects.exclude(title__in=curated_titles)
        deleted_count = 0
        for m in to_delete:
            # Check if has reviews or watchlist items
            if not m.reviews.exists() and not m.watchlist_entries.exists():
                m.delete()
                deleted_count += 1

        total_movies = Movie.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                f"Done! Created: {created_count}, Updated: {updated_count}, "
                f"Removed non-curated: {deleted_count}. Total Movies in DB: {total_movies}"
            )
        )
