print("Hello! I am the Popcornometer! Which movie genre do you want to watch? I have many recommendations!")

import random

genres = ["Horror", "Action", "Sci-Fi", "Anime", "Thriller", "Documentary"]
genre = []

horror = [
    "The Conjuring",
    "The Exorcist",
    "Hereditary",
    "A Quiet Place",
    "It",
    "Insidious",
    "The Shining",
    "Scream"
]

action = [
    "Mad Max: Fury Road",
    "John Wick",
    "The Dark Knight",
    "Die Hard",
    "Gladiator",
    "Top Gun: Maverick",
    "Mission: Impossible – Fallout",
    "Avengers: Endgame"
]

sci_fi = [
    "Interstellar",
    "Inception",
    "The Matrix",
    "Dune",
    "Avatar",
    "Blade Runner 2049",
    "The Martian",
    "Star Wars: A New Hope"
]

anime = [
    "Spirited Away",
    "Your Name",
    "Akira",
    "Howl's Moving Castle",
    "Princess Mononoke",
    "A Silent Voice",
    "Weathering with You",
    "My Neighbor Totoro"
]

thriller = [
    "Se7en",
    "Gone Girl",
    "Prisoners",
    "Shutter Island",
    "The Silence of the Lambs",
    "Zodiac",
    "Memento",
    "The Prestige"
]

documentary = [
    "Free Solo",
    "Our Planet",
    "The Social Dilemma",
    "13th",
    "March of the Penguins",
    "Won't You Be My Neighbor?",
    "My Octopus Teacher",
    "The Last Dance"
]


# Put all movie lists into one dictionary
movies = {
    "Horror": horror,
    "Action": action,
    "Sci-Fi": sci_fi,
    "Anime": anime,
    "Thriller": thriller,
    "Documentary": documentary
}


# Ask for genre
a = input(">> ")

for i in genres:
    if i.lower() in a.lower():
        genre.append(i)


# Check if a genre was selected
if len(genre) != 0:

    if random.randint(1, 3) == 1:
        print(f"That's a good selection! I love {random.choice(genre)}!")

    elif random.randint(1, 2) == 1:
        print("Okay! That is a nice choice!")

    else:
        print("Okay, we can work with that!")

else:
    print("You haven't selected any genres yet. Maybe we watch something sometime else or maybe you spelt the genre wrong!")
    print("You can always try again, just refresh the terminal.")
    exit()


# Get the movie list for the selected genre
movie_list = movies[genre[0]]

print("Do you like any of these?")
print(movie_list)

a = input(">> ")


# Find movies the user mentioned
selections = []

for movie in movie_list:
    if movie.lower() in a.lower():
        selections.append(movie)


# Choose a movie
if len(selections) == 0:

    movie = random.choice(movie_list)

    print(f"Okay, then let me choose for you!\nHow about {movie}?")

else:

    print(f"Good choice! I like {random.choice(selections)} a lot!")


print("Let's watch it!")