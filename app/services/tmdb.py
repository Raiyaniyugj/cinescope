import requests
import json
from datetime import datetime, timedelta, timezone
from flask import current_app
from app.models import db, APICache

# Static Mock Dataset for Demo Mode (if no TMDB API Key)
MOCK_DIRECTORS = {
    "525": {
        "id": 525,
        "name": "Christopher Nolan",
        "biography": "Christopher Edward Nolan is a British-American filmmaker. Known for his Hollywood blockbusters with complex storytelling, Nolan is considered a leading filmmaker of the 21st century.",
        "profile_path": "https://image.tmdb.org/t/p/w500/or06M24g4mXTT39Es4tm6YF4JaU.jpg",
        "place_of_birth": "London, England",
        "birthday": "1970-07-30"
    },
    "138": {
        "id": 138,
        "name": "Quentin Tarantino",
        "biography": "Quentin Jerome Tarantino is an American film director, screenwriter, producer, and actor. His films are characterized by stylized violence, razor-sharp dialogue, and pop culture references.",
        "profile_path": "https://image.tmdb.org/t/p/w500/1gjCpAa99bA4U4o1szwV55zFBxW.jpg",
        "place_of_birth": "Knoxville, Tennessee, USA",
        "birthday": "1963-03-27"
    },
    "1032": {
        "id": 1032,
        "name": "Martin Scorsese",
        "biography": "Martin Charles Scorsese is an American film director, producer, and screenwriter. He is one of the major figures of the New Hollywood era and is widely regarded as one of the most significant directors in cinema history.",
        "profile_path": "https://image.tmdb.org/t/p/w500/s8w3aCsy75168g07uCQzgdL665V.jpg",
        "place_of_birth": "Queens, New York City, USA",
        "birthday": "1942-11-17"
    },
    "2710": {
        "id": 2710,
        "name": "James Cameron",
        "biography": "James Francis Cameron is a Canadian filmmaker. Best known for making science fiction and epic films, he first gained recognition for directing The Terminator. He went on to direct Titanic and Avatar.",
        "profile_path": "https://image.tmdb.org/t/p/w500/9q8A62CO4RLcv58U7HsZaR6JIFm.jpg",
        "place_of_birth": "Kapuskasing, Ontario, Canada",
        "birthday": "1954-08-16"
    }
}

MOCK_MOVIES = {
    # Christopher Nolan
    27205: {
        "id": 27205,
        "title": "Inception",
        "overview": "Cobb, a skilled thief who steals valuable secrets from deep within the subconscious during the dream state, is offered a chance to have his criminal history erased as payment for a seemingly impossible task: \"inception\", the implantation of another person's idea into their subconscious.",
        "poster_path": "https://image.tmdb.org/t/p/w500/o01wJy9ZkRjU4j2nDLj761iUi8b.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/w1280/8Zuzn4Z50R7gcyggNTA1719rr7c.jpg",
        "release_date": "2010-07-15",
        "vote_average": 8.4,
        "vote_count": 34000,
        "budget": 160000000,
        "revenue": 836800000,
        "runtime": 148,
        "genres": [{"id": 28, "name": "Action"}, {"id": 878, "name": "Sci-Fi"}, {"id": 12, "name": "Adventure"}],
        "director": {"id": 525, "name": "Christopher Nolan"},
        "cast": [{"name": "Leonardo DiCaprio", "character": "Cobb"}, {"name": "Joseph Gordon-Levitt", "character": "Arthur"}, {"name": "Elliot Page", "character": "Ariadne"}]
    },
    157336: {
        "id": 157336,
        "title": "Interstellar",
        "overview": "The adventures of a group of explorers who make use of a newly discovered wormhole to surpass the limitations on human space travel and conquer the vast distances involved in an interstellar voyage.",
        "poster_path": "https://image.tmdb.org/t/p/w500/gEU2QniE6E7vNIvTa407vzs62mS.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/w1280/p17724sLBFWlzKO2mjpLSCL87wZ.jpg",
        "release_date": "2014-11-05",
        "vote_average": 8.4,
        "vote_count": 32000,
        "budget": 165000000,
        "revenue": 701700000,
        "runtime": 169,
        "genres": [{"id": 12, "name": "Adventure"}, {"id": 18, "name": "Drama"}, {"id": 878, "name": "Sci-Fi"}],
        "director": {"id": 525, "name": "Christopher Nolan"},
        "cast": [{"name": "Matthew McConaughey", "character": "Cooper"}, {"name": "Anne Hathaway", "character": "Brand"}, {"name": "Jessica Chastain", "character": "Murph"}]
    },
    155: {
        "id": 155,
        "title": "The Dark Knight",
        "overview": "Batman raises the stakes in his war on crime. With the help of Lt. Jim Gordon and District Attorney Harvey Dent, Batman sets out to dismantle the remaining criminal organizations that plague the streets. The partnership proves to be effective, but they soon find themselves prey to a reign of chaos unleashed by a rising criminal mastermind known to the terrified citizens of Gotham as the Joker.",
        "poster_path": "https://image.tmdb.org/t/p/w500/qJ2tWw75e1z127aOXbJihUnR9vx.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/w1280/nMKdUUepdz8gflSq5St4TSRj9o1.jpg",
        "release_date": "2008-07-16",
        "vote_average": 8.5,
        "vote_count": 30000,
        "budget": 185000000,
        "revenue": 1006000000,
        "runtime": 152,
        "genres": [{"id": 18, "name": "Drama"}, {"id": 28, "name": "Action"}, {"id": 80, "name": "Crime"}],
        "director": {"id": 525, "name": "Christopher Nolan"},
        "cast": [{"name": "Christian Bale", "character": "Bruce Wayne / Batman"}, {"name": "Heath Ledger", "character": "Joker"}, {"name": "Gary Oldman", "character": "Jim Gordon"}]
    },
    374720: {
        "id": 374720,
        "title": "Dunkirk",
        "overview": "Miraculous evacuation of Allied soldiers from Belgium, Britain, Canada, and France, who were cut off and surrounded by the German army from the beaches and harbor of Dunkirk, France, during the Battle of France in World War II.",
        "poster_path": "https://image.tmdb.org/t/p/w500/ebSnm4rGoaOTop4NWJ5N0gnkh0Y.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/w1280/F2t4JHi6sqj74j0U7r69mA5lsX.jpg",
        "release_date": "2017-07-19",
        "vote_average": 7.5,
        "vote_count": 15000,
        "budget": 100000000,
        "revenue": 527000000,
        "runtime": 106,
        "genres": [{"id": 28, "name": "Action"}, {"id": 18, "name": "Drama"}, {"id": 36, "name": "History"}, {"id": 10752, "name": "War"}],
        "director": {"id": 525, "name": "Christopher Nolan"},
        "cast": [{"name": "Fionn Whitehead", "character": "Tommy"}, {"name": "Tom Hardy", "character": "Farrier"}, {"name": "Cillian Murphy", "character": "Shivering Soldier"}]
    },
    577922: {
        "id": 577922,
        "title": "Tenet",
        "overview": "Armed with only one word - Tenet - and fighting for the survival of the entire world, the Protagonist journeys through a twilight world of international espionage on a mission that will unfold in something beyond real time.",
        "poster_path": "https://image.tmdb.org/t/p/w500/a56ve115g79g6lh456mXg1X693H.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/w1280/wzJRB4MKq1FCg24c45lJ6n4i76B.jpg",
        "release_date": "2020-08-22",
        "vote_average": 7.2,
        "vote_count": 9000,
        "budget": 205000000,
        "revenue": 365300000,
        "runtime": 150,
        "genres": [{"id": 28, "name": "Action"}, {"id": 878, "name": "Sci-Fi"}, {"id": 53, "name": "Thriller"}],
        "director": {"id": 525, "name": "Christopher Nolan"},
        "cast": [{"name": "John David Washington", "character": "Protagonist"}, {"name": "Robert Pattinson", "character": "Neil"}, {"name": "Elizabeth Debicki", "character": "Kat"}]
    },
    872585: {
        "id": 872585,
        "title": "Oppenheimer",
        "overview": "The story of American scientist J. Robert Oppenheimer and his role in the development of the atomic bomb.",
        "poster_path": "https://image.tmdb.org/t/p/w500/8Gxv8gS681J76SvU82jLYjNxt1c.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/w1280/fm6IpvlNY7627a60r36756wzZES.jpg",
        "release_date": "2023-07-19",
        "vote_average": 8.6,
        "vote_count": 8000,
        "budget": 100000000,
        "revenue": 957000000,
        "runtime": 180,
        "genres": [{"id": 18, "name": "Drama"}, {"id": 36, "name": "History"}],
        "director": {"id": 525, "name": "Christopher Nolan"},
        "cast": [{"name": "Cillian Murphy", "character": "J. Robert Oppenheimer"}, {"name": "Emily Blunt", "character": "Kitty Oppenheimer"}, {"name": "Matt Damon", "character": "Leslie Groves"}],
    },

    # Quentin Tarantino
    680: {
        "id": 680,
        "title": "Pulp Fiction",
        "overview": "A burger-loving hitman, his philosophical partner, a drug-addled gangster's moll and a washed-up boxer converge in this sprawling, comedic crime caper. Their adventures unfurl in three stories that ingeniously trip back and forth in time.",
        "poster_path": "https://image.tmdb.org/t/p/w500/d5iLLw2jqpHmYmPLKSRVjfg4nJs.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/w1280/suaEO51Z5f3V7uJ7fgRjOI9ffPR.jpg",
        "release_date": "1994-09-10",
        "vote_average": 8.5,
        "vote_count": 26000,
        "budget": 8000000,
        "revenue": 213900000,
        "runtime": 154,
        "genres": [{"id": 53, "name": "Thriller"}, {"id": 80, "name": "Crime"}],
        "director": {"id": 138, "name": "Quentin Tarantino"},
        "cast": [{"name": "John Travolta", "character": "Vincent Vega"}, {"name": "Samuel L. Jackson", "character": "Jules Winnfield"}, {"name": "Uma Thurman", "character": "Mia Wallace"}]
    },
    68718: {
        "id": 68718,
        "title": "Django Unchained",
        "overview": "With the help of a German bounty hunter, a freed slave sets out to rescue his wife from a brutal Mississippi plantation owner.",
        "poster_path": "https://image.tmdb.org/t/p/w500/7u3U98e2x01bce7qilVY7dd2wQy.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/w1280/2oZJiPz6vjQZ2uxzo4__nB8GBRx.jpg",
        "release_date": "2012-12-25",
        "vote_average": 8.1,
        "vote_count": 24000,
        "budget": 100000000,
        "revenue": 425400000,
        "runtime": 165,
        "genres": [{"id": 18, "name": "Drama"}, {"id": 37, "name": "Western"}],
        "director": {"id": 138, "name": "Quentin Tarantino"},
        "cast": [{"name": "Jamie Foxx", "character": "Django"}, {"name": "Christoph Waltz", "character": "Dr. King Schultz"}, {"name": "Leonardo DiCaprio", "character": "Calvin Candie"}]
    },
    24: {
        "id": 24,
        "title": "Kill Bill: Vol. 1",
        "overview": "An assassin is shot by her ruthless employer, Bill, and other members of their assassination circle. But she lives - and plots her vengeance.",
        "poster_path": "https://image.tmdb.org/t/p/w500/v7TaX8k2tywvlduJZK1BnU6P8vY.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/w1280/a906J63vBt3t1ofIE42glLoJ4N5.jpg",
        "release_date": "2003-10-08",
        "vote_average": 8.0,
        "vote_count": 16000,
        "budget": 30000000,
        "revenue": 180900000,
        "runtime": 111,
        "genres": [{"id": 28, "name": "Action"}, {"id": 80, "name": "Crime"}],
        "director": {"id": 138, "name": "Quentin Tarantino"},
        "cast": [{"name": "Uma Thurman", "character": "The Bride"}, {"name": "Lucy Liu", "character": "O-Ren Ishii"}, {"name": "David Carradine", "character": "Bill"}]
    },
    16869: {
        "id": 16869,
        "title": "Inglourious Basterds",
        "overview": "In Nazi-occupied France during World War II, a plan to assassinate Nazi leaders by a group of Jewish U.S. soldiers coincides with a theatre owner's vengeful plans for the same.",
        "poster_path": "https://image.tmdb.org/t/p/w500/aiwZR8znS5hb3FMzoLiU4CY6f2d.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/w1280/bk9Z94st6Tua8n82aRndnfsU5QZ.jpg",
        "release_date": "2009-08-18",
        "vote_average": 8.2,
        "vote_count": 20000,
        "budget": 70000000,
        "revenue": 321400000,
        "runtime": 153,
        "genres": [{"id": 28, "name": "Action"}, {"id": 18, "name": "Drama"}, {"id": 10752, "name": "War"}],
        "director": {"id": 138, "name": "Quentin Tarantino"},
        "cast": [{"name": "Brad Pitt", "character": "Lt. Aldo Raine"}, {"name": "Mélanie Laurent", "character": "Shosanna Dreyfus"}, {"name": "Christoph Waltz", "character": "Col. Hans Landa"}]
    },

    # Martin Scorsese
    103: {
        "id": 103,
        "title": "Taxi Driver",
        "overview": "A mentally unstable Vietnam War veteran works as a night-time taxi driver in New York City, where the perceived decadence and sleaze feeds his urge for violent action.",
        "poster_path": "https://image.tmdb.org/t/p/w500/ekstTLRP68AdUPT0W6q2nuDLSrt.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/w1280/aY5Oi421X6YmXl4fH99G9W6rG4B.jpg",
        "release_date": "1976-02-09",
        "vote_average": 8.2,
        "vote_count": 11000,
        "budget": 1300000,
        "revenue": 28262574,
        "runtime": 114,
        "genres": [{"id": 18, "name": "Drama"}, {"id": 80, "name": "Crime"}],
        "director": {"id": 1032, "name": "Martin Scorsese"},
        "cast": [{"name": "Robert De Niro", "character": "Travis Bickle"}, {"name": "Jodie Foster", "character": "Iris Steensma"}, {"name": "Albert Brooks", "character": "Tom"}]
    },
    769: {
        "id": 769,
        "title": "Goodfellas",
        "overview": "The true story of Henry Hill and his life in the mob, covering his relationship with his wife Karen Hill and his mob partners Jimmy Conway and Tommy DeVito in the Italian-American crime syndicate.",
        "poster_path": "https://image.tmdb.org/t/p/w500/aKuFiU82mHNDwJ54ZSvO1o0wXFd.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/w1280/sw7mordpZxg44W1aKng7tbkHPPW.jpg",
        "release_date": "1990-09-12",
        "vote_average": 8.5,
        "vote_count": 12000,
        "budget": 25000000,
        "revenue": 46800000,
        "runtime": 145,
        "genres": [{"id": 18, "name": "Drama"}, {"id": 80, "name": "Crime"}],
        "director": {"id": 1032, "name": "Martin Scorsese"},
        "cast": [{"name": "Robert De Niro", "character": "Jimmy Conway"}, {"name": "Ray Liotta", "character": "Henry Hill"}, {"name": "Joe Pesci", "character": "Tommy DeVito"}]
    },
    106646: {
        "id": 106646,
        "title": "The Wolf of Wall Street",
        "overview": "A New York stockbroker refuses to cooperate in a large securities fraud case involving corruption on Wall Street, corporate banking world and mob infiltration.",
        "poster_path": "https://image.tmdb.org/t/p/w500/jtlSVZCL55SjS576q17S4wT7678.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/w1280/kC598gG5n9u25t9xF7uD7vpH5N5.jpg",
        "release_date": "2013-12-25",
        "vote_average": 8.0,
        "vote_count": 22000,
        "budget": 100000000,
        "revenue": 392000000,
        "runtime": 180,
        "genres": [{"id": 80, "name": "Crime"}, {"id": 18, "name": "Drama"}, {"id": 35, "name": "Comedy"}],
        "director": {"id": 1032, "name": "Martin Scorsese"},
        "cast": [{"name": "Leonardo DiCaprio", "character": "Jordan Belfort"}, {"name": "Jonah Hill", "character": "Donnie Azoff"}, {"name": "Margot Robbie", "character": "Naomi Lapaglia"}]
    },
    11324: {
        "id": 11324,
        "title": "Shutter Island",
        "overview": "World War II soldier turned U.S. Marshal Teddy Daniels investigates the disappearance of a patient from Boston's Shutter Island Ashecliffe Hospital. He pushes to find the truth about the asylum, but his investigation takes a darker path.",
        "poster_path": "https://image.tmdb.org/t/p/w500/4EC3t5R6q1c4jK62uVj6vQvM5sY.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/w1280/63hA29zJj37R2V3L371wG8r4R4.jpg",
        "release_date": "2010-02-14",
        "vote_average": 8.2,
        "vote_count": 22000,
        "budget": 80000000,
        "revenue": 294800000,
        "runtime": 138,
        "genres": [{"id": 18, "name": "Drama"}, {"id": 53, "name": "Thriller"}, {"id": 9648, "name": "Mystery"}],
        "director": {"id": 1032, "name": "Martin Scorsese"},
        "cast": [{"name": "Leonardo DiCaprio", "character": "Teddy Daniels"}, {"name": "Mark Ruffalo", "character": "Chuck Aule"}, {"name": "Ben Kingsley", "character": "Dr. John Cawley"}]
    },
    1422: {
        "id": 1422,
        "title": "The Departed",
        "overview": "To take down South Boston's Irish Mafia, the police send in an undercover cop. Simultaneously, a career criminal infiltrates the police department as an informer.",
        "poster_path": "https://image.tmdb.org/t/p/w500/3E5Ibui4e2Yv96g7gG2LPh3b0W0.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/w1280/4k48q8Z3n3pP8v96g7gG2LPh3b0W0.jpg",
        "release_date": "2006-10-05",
        "vote_average": 8.2,
        "vote_count": 13000,
        "budget": 90000000,
        "revenue": 291400000,
        "runtime": 151,
        "genres": [{"id": 18, "name": "Drama"}, {"id": 53, "name": "Thriller"}, {"id": 80, "name": "Crime"}],
        "director": {"id": 1032, "name": "Martin Scorsese"},
        "cast": [{"name": "Leonardo DiCaprio", "character": "Billy Costigan"}, {"name": "Matt Damon", "character": "Colin Sullivan"}, {"name": "Jack Nicholson", "character": "Frank Costello"}]
    },

    # James Cameron
    597: {
        "id": 597,
        "title": "Titanic",
        "overview": "A seventeen-year-old aristocrat falls in love with a kind but poor artist aboard the luxurious, ill-fated R.M.S. Titanic.",
        "poster_path": "https://image.tmdb.org/t/p/w500/9xjUNR9s5hV08t1w7gG2LPh3b0W0.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/w1280/6xK3w9vmc2s2X5chjJ18fXIk9fL.jpg",
        "release_date": "1997-11-18",
        "vote_average": 7.9,
        "vote_count": 23000,
        "budget": 200000000,
        "revenue": 2264000000,
        "runtime": 194,
        "genres": [{"id": 18, "name": "Drama"}, {"id": 10749, "name": "Romance"}, {"id": 53, "name": "Thriller"}],
        "director": {"id": 2710, "name": "James Cameron"},
        "cast": [{"name": "Leonardo DiCaprio", "character": "Jack Dawson"}, {"name": "Kate Winslet", "character": "Rose DeWitt Bukater"}, {"name": "Billy Zane", "character": "Cal Hockley"}]
    },
    19995: {
        "id": 19995,
        "title": "Avatar",
        "overview": "In the 22nd century, a paraplegic Marine is dispatched to the moon Pandora on a unique mission, but becomes torn between following his orders and protecting the world he feels is his home.",
        "poster_path": "https://image.tmdb.org/t/p/w500/kyeE63xttY2Phw0bbq6zP47Z6Fo.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/w1280/amWzJRB4MKq1FCg24c45lJ6n4i76B.jpg",
        "release_date": "2009-12-10",
        "vote_average": 7.5,
        "vote_count": 29000,
        "budget": 237000000,
        "revenue": 2923700000,
        "runtime": 162,
        "genres": [{"id": 28, "name": "Action"}, {"id": 12, "name": "Adventure"}, {"id": 14, "name": "Fantasy"}, {"id": 878, "name": "Sci-Fi"}],
        "director": {"id": 2710, "name": "James Cameron"},
        "cast": [{"name": "Sam Worthington", "character": "Jake Sully"}, {"name": "Zoe Saldana", "character": "Neytiri"}, {"name": "Sigourney Weaver", "character": "Dr. Grace Augustine"}]
    },
    76600: {
        "id": 76600,
        "title": "Avatar: The Way of Water",
        "overview": "Set more than a decade after the events of the first film, learn the story of the Sully family, the trouble that follows them, the lengths they go to keep each other safe, the battles they fight to stay alive, and the tragedies they endure.",
        "poster_path": "https://image.tmdb.org/t/p/w500/t6z8HP702kpk36XJjd4n2KAO17z.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/w1280/ovM06PdLIW8jxIu555v4y4v5Z9P.jpg",
        "release_date": "2022-12-14",
        "vote_average": 7.6,
        "vote_count": 10000,
        "budget": 350000000,
        "revenue": 2320250000,
        "runtime": 192,
        "genres": [{"id": 878, "name": "Sci-Fi"}, {"id": 28, "name": "Action"}, {"id": 12, "name": "Adventure"}],
        "director": {"id": 2710, "name": "James Cameron"},
        "cast": [{"name": "Sam Worthington", "character": "Jake Sully"}, {"name": "Zoe Saldana", "character": "Neytiri"}, {"name": "Sigourney Weaver", "character": "Kiri"}]
    },
    218: {
        "id": 218,
        "title": "The Terminator",
        "overview": "A cyborg assassin is sent back in time to kill Sarah Connor, whose son will lead the human resistance against Skynet.",
        "poster_path": "https://image.tmdb.org/t/p/w500/qvktm0BHJmBz4zUIeqw2vvDPR57.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/w1280/whNwfuiiyv2thVg74t45vj5C1nF.jpg",
        "release_date": "1984-10-26",
        "vote_average": 7.6,
        "vote_count": 12000,
        "budget": 6400000,
        "revenue": 78371200,
        "runtime": 107,
        "genres": [{"id": 28, "name": "Action"}, {"id": 878, "name": "Sci-Fi"}, {"id": 53, "name": "Thriller"}],
        "director": {"id": 2710, "name": "James Cameron"},
        "cast": [{"name": "Arnold Schwarzenegger", "character": "The Terminator"}, {"name": "Linda Hamilton", "character": "Sarah Connor"}, {"name": "Michael Biehn", "character": "Kyle Reese"}]
    },
    679: {
        "id": 679,
        "title": "Aliens",
        "overview": "When Ripley's lifepod is found by a salvage crew 57 years later, she finds that human colonists have settled on the planet where she first encountered the Alien.",
        "poster_path": "https://image.tmdb.org/t/p/w500/v15o4hxZ5ZrtjKl4pa45vj5C1nF.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/w1280/ovNwfuiiyv2thVg74t45vj5C1nF.jpg",
        "release_date": "1986-07-18",
        "vote_average": 7.9,
        "vote_count": 9000,
        "budget": 18500000,
        "revenue": 183300000,
        "runtime": 137,
        "genres": [{"id": 28, "name": "Action"}, {"id": 878, "name": "Sci-Fi"}, {"id": 53, "name": "Thriller"}, {"id": 18, "name": "Drama"}],
        "director": {"id": 2710, "name": "James Cameron"},
        "cast": [{"name": "Sigourney Weaver", "character": "Ellen Ripley"}, {"name": "Carrie Henn", "character": "Rebecca 'Newt' Jorden"}, {"name": "Michael Biehn", "character": "Corporal Dwayne Hicks"}]
    }
}

class TMDBService:
    """Service to handle all interactions with the TMDB API or Fallback Mock Data."""

    def __init__(self):
        self.api_key = None
        self.base_url = None
        self.headers = {}
        self.is_demo_mode = True
        self.last_error = None  # Track last API error for user feedback

    def init_app(self, app):
        self.api_key = app.config['TMDB_API_KEY']
        self.base_url = app.config['TMDB_BASE_URL']
        if self.api_key:
            self.is_demo_mode = False
            # Check if key is a v4 Read Access Token or a v3 API Key
            if len(self.api_key) > 50:
                # v4 authentication token
                self.headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json;charset=utf-8"
                }
            else:
                # v3 api key (appended to URL query params)
                self.headers = {}

    def _get_cached_or_fetch(self, url, params=None):
        """Cache-first strategy: return ANY cached data instantly.
        Only makes an API call when cache is completely empty."""
        if self.is_demo_mode:
            return None

        # Build cache key
        full_url = url
        if params:
            param_str = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
            full_url = f"{url}?{param_str}"
        if not len(self.headers) and self.api_key and "api_key=" not in full_url:
            full_url += f"&api_key={self.api_key}" if "?" in full_url else f"?api_key={self.api_key}"

        # 1. Check cache — return ANY cached data instantly (fresh or stale)
        cached_entry = APICache.query.filter_by(url_key=full_url).first()
        if cached_entry:
            try:
                return json.loads(cached_entry.response_text)
            except Exception:
                pass

        # 2. No cache — must fetch from API (8s timeout for slow networks)
        try:
            req_params = params.copy() if params else {}
            if not self.headers:
                req_params['api_key'] = self.api_key

            response = requests.get(url, headers=self.headers, params=req_params, timeout=8)
            if response.status_code == 200:
                data = response.json()
                try:
                    new_cache = APICache(url_key=full_url, response_text=json.dumps(data))
                    db.session.add(new_cache)
                    db.session.commit()
                except Exception:
                    db.session.rollback()
                self.last_error = None
                return data
            elif response.status_code == 404:
                self.last_error = None
                return None
        except Exception as e:
            self.last_error = str(e)
            print(f"TMDB Fetch Error: {e}")

        return None

    def get_trending_movies(self, page=1):
        """Browse trending movies of the week."""
        # 1. Try Live fetch
        if not self.is_demo_mode:
            url = f"{self.base_url}/trending/movie/week"
            data = self._get_cached_or_fetch(url, params={"page": page})
            if data and 'results' in data:
                return data['results']

        # 2. Fallback to Mock Data
        return [self._minify_movie(movie) for movie in MOCK_MOVIES.values()]

    def get_trending_tv(self, page=1):
        """Browse trending TV shows of the week."""
        if not self.is_demo_mode:
            url = f"{self.base_url}/trending/tv/week"
            data = self._get_cached_or_fetch(url, params={"page": page})
            if data and 'results' in data:
                return data['results']
        return []

    def get_popular_movies(self, page=1):
        """Browse popular movies."""
        if not self.is_demo_mode:
            url = f"{self.base_url}/movie/popular"
            data = self._get_cached_or_fetch(url, params={"page": page})
            if data and 'results' in data:
                return data['results']

        # Sort mock movies by rating for popularity
        sorted_mocks = sorted(MOCK_MOVIES.values(), key=lambda x: x['vote_average'], reverse=True)
        return [self._minify_movie(movie) for movie in sorted_mocks]

    def search_movies(self, query):
        """Search movies by query string."""
        if not query:
            return []

        if not self.is_demo_mode:
            url = f"{self.base_url}/search/movie"
            data = self._get_cached_or_fetch(url, params={"query": query})
            if data and 'results' in data:
                return data['results']

        # Fallback to local regex/substr search
        query = query.lower()
        results = []
        for movie in MOCK_MOVIES.values():
            if query in movie['title'].lower() or query in movie['overview'].lower():
                results.append(self._minify_movie(movie))
        return results

    def get_tv_details(self, tv_id):
        """Fetch full TV show details including cast, crew, genres, and trailers."""
        try:
            tv_id = int(tv_id)
        except ValueError:
            return None

        if not self.is_demo_mode:
            url = f"{self.base_url}/tv/{tv_id}?append_to_response=credits,videos,watch/providers,similar,reviews"
            data = self._get_cached_or_fetch(url)
            if data:
                # Map TV fields to common fields for easier template rendering
                data['title'] = data.get('name')
                data['release_date'] = data.get('first_air_date')
                
                # Extract credits
                credits_data = data.pop('credits', None)
                if credits_data:
                    data['cast'] = credits_data.get('cast', [])
                    data['crew'] = credits_data.get('crew', [])
                    directors = [crew for crew in credits_data.get('crew', []) if crew.get('job') == 'Director']
                    data['director'] = directors[0] if directors else None
                
                # Extract trailers
                videos_data = data.pop('videos', None)
                if videos_data:
                    trailers = [v for v in videos_data.get('results', [])
                               if v.get('site') == 'YouTube' and v.get('type') in ('Trailer', 'Teaser')]
                    data['trailers'] = trailers[:3]
                elif 'trailers' not in data:
                    data['trailers'] = []
                
                # Extract watch providers
                providers_data = data.pop('watch/providers', None)
                if providers_data and 'results' in providers_data:
                    data['watch_providers'] = providers_data['results'].get('US', {})
                elif 'watch_providers' not in data:
                    data['watch_providers'] = {}

                # Map runtime to episode run time if available
                if 'episode_run_time' in data and data['episode_run_time']:
                    data['runtime'] = data['episode_run_time'][0]

                # Extract reviews
                reviews_data = data.pop('reviews', None)
                if reviews_data:
                    data['_reviews'] = reviews_data.get('results', [])[:5]
                elif '_reviews' not in data:
                    data['_reviews'] = []

                return data
        return None

    def search_multi(self, query):
        """Search movies, people, and TV shows (though we focus on movies and people)."""
        if not query:
            return []

        if not self.is_demo_mode:
            url = f"{self.base_url}/search/multi"
            data = self._get_cached_or_fetch(url, params={"query": query})
            results = []
            if data and 'results' in data:
                # Filter to only allow movies, people, and tv shows
                results.extend([r for r in data['results'] if r.get('media_type') in ('movie', 'person', 'tv')])
            
            # Add company search
            comp_url = f"{self.base_url}/search/company"
            comp_data = self._get_cached_or_fetch(comp_url, params={"query": query})
            if comp_data and 'results' in comp_data:
                for idx, c in enumerate(comp_data['results'][:3]):
                    c['media_type'] = 'company'
                    # Fetch basic company movies to enrich the result (top 3 movies and total count)
                    c_movies = self.get_company_movies(c['id'])
                    c['total_movies'] = c_movies.get('total_results', 0)
                    top_movies = [m.get('title') for m in c_movies.get('results', [])[:3]]
                    c['top_movies'] = top_movies
                    results.insert(idx, c) # Insert at top
                    
            return results

        # Fallback to local regex/substr search
        query = query.lower()
        results = []
        for movie in MOCK_MOVIES.values():
            if query in movie['title'].lower() or query in movie['overview'].lower():
                minified = self._minify_movie(movie)
                minified['media_type'] = 'movie'
                results.append(minified)
        for d_id, director in MOCK_DIRECTORS.items():
            if query in director['name'].lower():
                d_copy = director.copy()
                d_copy['media_type'] = 'person'
                results.append(d_copy)
        return results

    def get_company_movies(self, company_id, page=1):
        """Fetch movies belonging to a specific company/studio."""
        if self.is_demo_mode:
            return {"page": 1, "results": [], "total_pages": 1, "total_results": 0}
        
        url = f"{self.base_url}/discover/movie"
        params = {
            "with_companies": company_id,
            "sort_by": "popularity.desc",
            "page": page
        }
        data = self._get_cached_or_fetch(url, params=params)
        return data if data else {"page": 1, "results": [], "total_pages": 1, "total_results": 0}

    def get_movie_details(self, movie_id):
        """Fetch full movie details including cast, crew, genres, and trailers."""
        try:
            movie_id = int(movie_id)
        except ValueError:
            return None

        if not self.is_demo_mode:
            # Single API call — append_to_response baked into URL
            # Cache key stays clean as /movie/{id} for compatibility
            url = f"{self.base_url}/movie/{movie_id}?append_to_response=credits,videos,watch/providers,similar,reviews"
            data = self._get_cached_or_fetch(url)
            if data:
                # Extract credits (may not exist in old cache)
                credits_data = data.pop('credits', None)
                if credits_data:
                    data['cast'] = credits_data.get('cast', [])
                    data['crew'] = credits_data.get('crew', [])
                    directors = [crew for crew in credits_data.get('crew', []) if crew.get('job') == 'Director']
                    data['director'] = directors[0] if directors else data.get('director')
                
                # Extract trailers
                videos_data = data.pop('videos', None)
                if videos_data:
                    trailers = [v for v in videos_data.get('results', [])
                               if v.get('site') == 'YouTube' and v.get('type') in ('Trailer', 'Teaser')]
                    data['trailers'] = trailers[:3]
                elif 'trailers' not in data:
                    data['trailers'] = []

                # Extract watch providers
                wp_data = data.pop('watch/providers', None)
                if wp_data and 'results' in wp_data:
                    for region in ['IN', 'US', 'GB']:
                        if region in wp_data['results']:
                            data['_watch_providers'] = wp_data['results'][region]
                            break
                    else:
                        if wp_data['results']:
                            data['_watch_providers'] = list(wp_data['results'].values())[0]

                # Extract similar movies
                similar_data = data.pop('similar', None)
                if similar_data:
                    data['_similar_movies'] = similar_data.get('results', [])[:8]
                elif '_similar_movies' not in data:
                    data['_similar_movies'] = []

                # Extract reviews
                reviews_data = data.pop('reviews', None)
                if reviews_data:
                    data['_reviews'] = reviews_data.get('results', [])[:5]  # Limit to top 5 reviews
                elif '_reviews' not in data:
                    data['_reviews'] = []

                return data

        # Fallback to local
        return MOCK_MOVIES.get(movie_id)



    def get_now_playing(self, page=1):
        """Fetch movies currently playing in theaters."""
        if not self.is_demo_mode:
            url = f"{self.base_url}/movie/now_playing"
            data = self._get_cached_or_fetch(url, params={"page": page})
            if data and 'results' in data:
                return data['results']
        # Fallback
        return list(MOCK_MOVIES.values())[:6]

    def get_genres_list(self):
        """Fetch the official TMDB genre list."""
        if not self.is_demo_mode:
            url = f"{self.base_url}/genre/movie/list"
            data = self._get_cached_or_fetch(url)
            if data and 'genres' in data:
                return data['genres']
        # Fallback
        return [
            {"id": 28, "name": "Action"}, {"id": 12, "name": "Adventure"},
            {"id": 35, "name": "Comedy"}, {"id": 80, "name": "Crime"},
            {"id": 18, "name": "Drama"}, {"id": 14, "name": "Fantasy"},
            {"id": 27, "name": "Horror"}, {"id": 10749, "name": "Romance"},
            {"id": 878, "name": "Sci-Fi"}, {"id": 53, "name": "Thriller"},
        ]

    def get_person_details(self, person_id):
        """Get details about a person (Actor, Director, Writer)."""
        if not self.is_demo_mode:
            url = f"{self.base_url}/person/{person_id}?append_to_response=movie_credits"
            data = self._get_cached_or_fetch(url)
            if data:
                known_for = data.get('known_for_department')
                if 'movie_credits' in data:
                    for role in ['cast', 'crew']:
                        if role in data['movie_credits']:
                            seen = set()
                            deduped = []
                            for m in data['movie_credits'][role]:
                                if role == 'crew':
                                    if known_for == 'Directing' and m.get('job') != 'Director':
                                        continue
                                    if known_for == 'Writing' and m.get('department') != 'Writing':
                                        continue
                                        
                                m_id = m.get('id')
                                if m_id not in seen:
                                    seen.add(m_id)
                                    deduped.append(m)
                            # Sort by release date descending
                            deduped.sort(key=lambda x: x.get('release_date', ''), reverse=True)
                            data['movie_credits'][role] = deduped
                return data

        # Fallback to local
        person_id_str = str(person_id)
        if person_id_str in MOCK_DIRECTORS:
            person = MOCK_DIRECTORS[person_id_str].copy()
            # Fetch movies directed by them in mock DB
            directed_movies = []
            for movie in MOCK_MOVIES.values():
                if str(movie['director']['id']) == person_id_str:
                    directed_movies.append(self._minify_movie(movie))
            person['movies'] = directed_movies
            person['movie_credits'] = {'crew': directed_movies, 'cast': []}
            return person

        return None

    def search_directors(self, query):
        """Search for a director person record."""
        if not query:
            return []

        if not self.is_demo_mode:
            url = f"{self.base_url}/search/person"
            data = self._get_cached_or_fetch(url, params={"query": query})
            if data and 'results' in data:
                # Keep people whose department is Directing
                return [p for p in data['results'] if p.get('known_for_department') == 'Directing']

        # Fallback
        query = query.lower()
        results = []
        for d in MOCK_DIRECTORS.values():
            if query in d['name'].lower():
                results.append(d)
        return results

    def get_popular_directors(self):
        """Fetch a curated list of well-known directors with their TMDB profile data."""
        # Curated TMDB IDs of famous directors (guaranteed to be directors)
        NOTABLE_DIRECTOR_IDS = [
            525,    # Christopher Nolan
            138,    # Quentin Tarantino
            1032,   # Martin Scorsese
            2710,   # James Cameron
            510,    # Tim Burton
            5655,   # Ridley Scott
            1223,   # Steven Spielberg
            578,    # Wes Anderson
            5174,   # David Fincher
            7467,   # Denis Villeneuve
            11218,  # Bong Joon-ho
            240,    # Stanley Kubrick
            5281,   # Spike Lee
            1884,   # Greta Gerwig
            112,    # Coen Brothers (Joel)
            524,    # Damien Chazelle
            8699,   # Jordan Peele
            17825,  # Guillermo del Toro
            1776,   # Francis Ford Coppola
            7623,   # Park Chan-wook
        ]

        if not self.is_demo_mode:
            directors = []
            for did in NOTABLE_DIRECTOR_IDS:
                url = f"{self.base_url}/person/{did}"
                data = self._get_cached_or_fetch(url)
                if data:
                    directors.append(data)
            return directors

        # Fallback
        return list(MOCK_DIRECTORS.values())

    def get_movies_by_genre(self, genre_id, sort_by=None, page=1):
        """Fetch movies matching a specific genre ID."""
        try:
            genre_id = int(genre_id)
        except ValueError:
            return []

        # Mapping our URL sort string to TMDB API sort values
        sort_map = {
            'name': 'original_title.asc',
            'release-earliest': 'primary_release_date.asc',
            'release-newest': 'primary_release_date.desc',
            'rating-highest': 'vote_average.desc',
            'rating-lowest': 'vote_average.asc',
            'popularity': 'popularity.desc',
            'most-watched': 'vote_count.desc'
        }
        tmdb_sort = sort_map.get(sort_by, 'popularity.desc')

        if not self.is_demo_mode:
            url = f"{self.base_url}/discover/movie"
            params = {"with_genres": genre_id, "page": page, "sort_by": tmdb_sort}
            data = self._get_cached_or_fetch(url, params=params)
            if data and 'results' in data:
                return data['results']

        # Fallback
        results = []
        for movie in MOCK_MOVIES.values():
            genre_ids = [g['id'] for g in movie['genres']]
            if genre_id in genre_ids:
                results.append(self._minify_movie(movie))
        return results

    def get_all_movies(self, sort_by=None, timeframe=None, page=1):
        """Fetch all movies, optionally sorted or filtered by a specific timeframe."""
        sort_map = {
            'name': 'original_title.asc',
            'release-earliest': 'primary_release_date.asc',
            'release-newest': 'primary_release_date.desc',
            'rating-highest': 'vote_average.desc',
            'rating-lowest': 'vote_average.asc',
            'popularity': 'popularity.desc',
            'most-watched': 'vote_count.desc'
        }
        tmdb_sort = sort_map.get(sort_by, 'popularity.desc')

        if not self.is_demo_mode:
            url = f"{self.base_url}/discover/movie"
            params = {
                "sort_by": tmdb_sort,
                "page": page
            }
            
            if timeframe:
                from datetime import datetime, timedelta
                now = datetime.now()
                if timeframe == 'this-year':
                    params["primary_release_date.gte"] = f"{now.year}-01-01"
                elif timeframe == 'this-month':
                    params["primary_release_date.gte"] = f"{now.year}-{now.month:02d}-01"
                elif timeframe == 'this-week':
                    last_week = now - timedelta(days=7)
                    params["primary_release_date.gte"] = last_week.strftime("%Y-%m-%d")
                    
            # Add vote_count filter for rating-highest to avoid obscure movies with 1 rating of 10.
            if sort_by in ['rating-highest', 'rating-lowest']:
                params["vote_count.gte"] = 100

            data = self._get_cached_or_fetch(url, params=params)
            if data and 'results' in data:
                return data['results'], data.get('total_results', len(data['results']))

        # Fallback
        return [self._minify_movie(m) for m in list(MOCK_MOVIES.values())], len(MOCK_MOVIES)

    def get_movies_by_decade(self, decade_start, genre_id=None, sort_by=None, page=1):
        """Fetch movies released within a specific decade, optionally filtered by genre."""
        try:
            decade_start = int(str(decade_start)[:4])
        except ValueError:
            return [], 0

        decade_end = decade_start + 9
        
        sort_map = {
            'name': 'original_title.asc',
            'release-earliest': 'primary_release_date.asc',
            'release-newest': 'primary_release_date.desc',
            'rating-highest': 'vote_average.desc',
            'rating-lowest': 'vote_average.asc',
            'popularity': 'popularity.desc',
            'most-watched': 'vote_count.desc'
        }
        tmdb_sort = sort_map.get(sort_by, 'popularity.desc')

        if not self.is_demo_mode:
            url = f"{self.base_url}/discover/movie"
            params = {
                "primary_release_date.gte": f"{decade_start}-01-01",
                "primary_release_date.lte": f"{decade_end}-12-31",
                "sort_by": tmdb_sort,
                "page": page
            }
            if genre_id:
                params["with_genres"] = genre_id
                
            data = self._get_cached_or_fetch(url, params=params)
            if data and 'results' in data:
                return data['results'], data.get('total_results', len(data['results']))

        # Fallback
        results = []
        for movie in MOCK_MOVIES.values():
            if 'release_date' in movie and movie['release_date']:
                try:
                    year = int(movie['release_date'][:4])
                    if decade_start <= year <= decade_end:
                        if genre_id:
                            movie_genre_ids = [g['id'] for g in movie.get('genres', [])]
                            if int(genre_id) not in movie_genre_ids:
                                continue
                        results.append(self._minify_movie(movie))
                except ValueError:
                    pass
        return results, len(results)

    def get_movies_by_year(self, year, genre_id=None, sort_by=None, page=1):
        """Fetch movies released within a specific year, optionally filtered by genre."""
        try:
            year = int(str(year)[:4])
        except ValueError:
            return [], 0

        sort_map = {
            'name': 'original_title.asc',
            'release-earliest': 'primary_release_date.asc',
            'release-newest': 'primary_release_date.desc',
            'rating-highest': 'vote_average.desc',
            'rating-lowest': 'vote_average.asc',
            'popularity': 'popularity.desc',
            'most-watched': 'vote_count.desc'
        }
        tmdb_sort = sort_map.get(sort_by, 'popularity.desc')

        if not self.is_demo_mode:
            url = f"{self.base_url}/discover/movie"
            params = {
                "primary_release_date.gte": f"{year}-01-01",
                "primary_release_date.lte": f"{year}-12-31",
                "sort_by": tmdb_sort,
                "page": page
            }
            if genre_id:
                params["with_genres"] = genre_id
                
            data = self._get_cached_or_fetch(url, params=params)
            if data and 'results' in data:
                return data['results'], data.get('total_results', len(data['results']))

        # Fallback
        results = []
        for movie in MOCK_MOVIES.values():
            if 'release_date' in movie and movie['release_date']:
                try:
                    movie_year = int(movie['release_date'][:4])
                    if year == movie_year:
                        if genre_id:
                            movie_genre_ids = [g['id'] for g in movie.get('genres', [])]
                            if int(genre_id) not in movie_genre_ids:
                                continue
                        results.append(self._minify_movie(movie))
                except ValueError:
                    pass
        return results, len(results)

    def get_similar_movies(self, movie_id, page=1):
        """Fetch recommended similar movies for item-to-item panels."""
        try:
            movie_id = int(movie_id)
        except ValueError:
            return [], 1

        if not self.is_demo_mode:
            url = f"{self.base_url}/movie/{movie_id}/similar?page={page}"
            data = self._get_cached_or_fetch(url)
            if data and 'results' in data:
                return data['results'], data.get('total_pages', 1)

        # Fallback: find movies sharing at least one genre in common (excluding itself)
        current = MOCK_MOVIES.get(movie_id)
        if not current:
            return [], 1
        current_genres = {g['id'] for g in current['genres']}
        similar = []
        for m_id, movie in MOCK_MOVIES.items():
            if m_id == movie_id:
                continue
            movie_genres = {g['id'] for g in movie['genres']}
            common = current_genres.intersection(movie_genres)
            if common:
                similar.append((len(common), movie))
        
        # Sort by number of common genres descending
        similar = sorted(similar, key=lambda x: x[0], reverse=True)
        return [self._minify_movie(s[1]) for s in similar[:8]], 1

    def get_top_grossing_movies(self, count=10):
        """Fetch top grossing movies for dashboards."""
        if not self.is_demo_mode:
            url = f"{self.base_url}/discover/movie"
            # Discover sorted by revenue
            data = self._get_cached_or_fetch(url, params={"sort_by": "revenue.desc"})
            if data and 'results' in data:
                # Detailed fetch for revenue attributes (discover doesn't always contain budget/revenue on simple results list)
                full_movies = []
                for basic in data['results'][:count]:
                    details = self.get_movie_details(basic['id'])
                    if details:
                        full_movies.append(details)
                return full_movies

        # Fallback
        sorted_mocks = sorted(MOCK_MOVIES.values(), key=lambda x: x.get('revenue', 0), reverse=True)
        return sorted_mocks[:count]

    def _minify_movie(self, movie_details):
        """Converts complete detailed movie object to standard listings format."""
        return {
            "id": movie_details.get("id"),
            "title": movie_details.get("title"),
            "overview": movie_details.get("overview", "")[:150] + "...",
            "poster_path": movie_details.get("poster_path"),
            "backdrop_path": movie_details.get("backdrop_path"),
            "release_date": movie_details.get("release_date"),
            "vote_average": movie_details.get("vote_average"),
            "vote_count": movie_details.get("vote_count"),
            "genre_ids": [g['id'] for g in movie_details.get('genres', [])]
        }

    def get_watch_providers(self, movie_id):
        """Get streaming/watch providers for a movie (JustWatch data via TMDB)."""
        if not self.is_demo_mode:
            url = f"{self.base_url}/movie/{movie_id}/watch/providers"
            data = self._get_cached_or_fetch(url)
            if data and 'results' in data:
                # Try IN (India) first, then US, then first available
                for region in ['IN', 'US', 'GB']:
                    if region in data['results']:
                        return data['results'][region]
                # Return first available
                if data['results']:
                    return list(data['results'].values())[0]
        return None

    def get_movies_by_studio(self, company_id, page=1):
        """Fetch movies from a specific production company/studio."""
        if not self.is_demo_mode:
            url = f"{self.base_url}/discover/movie"
            data = self._get_cached_or_fetch(url, params={
                "with_companies": str(company_id),
                "sort_by": "popularity.desc",
                "page": str(page)
            })
            if data and 'results' in data:
                return data['results']
        return []

    def get_company_details(self, company_id):
        """Fetch details of a production company."""
        if not self.is_demo_mode:
            url = f"{self.base_url}/company/{company_id}"
            data = self._get_cached_or_fetch(url)
            if data:
                return data
        return None

    def get_top_rated(self, page=1):
        """Fetch top rated movies."""
        if not self.is_demo_mode:
            url = f"{self.base_url}/movie/top_rated"
            data = self._get_cached_or_fetch(url, params={"page": str(page)})
            if data and 'results' in data:
                return data['results']
        return list(MOCK_MOVIES.values())[:20]

    def get_upcoming(self):
        """Fetch upcoming movies."""
        if not self.is_demo_mode:
            url = f"{self.base_url}/movie/upcoming"
            data = self._get_cached_or_fetch(url)
            if data and 'results' in data:
                return data['results']
        return []

# Instantiate singleton service
tmdb_service = TMDBService()

