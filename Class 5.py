import time
import random

fun_facts = {

    # 1–10: Space 🚀
    1: {
        "genre": "Space",
        "title": "A Day on Venus",
        "content": "A day on Venus lasts longer than a year on Venus!\nVenus takes about 243 Earth days to rotate but only 225 days to orbit the Sun."
    },
    2: {
        "genre": "Space",
        "title": "The Smell of Space",
        "content": "Astronauts have described the smell of their spacesuits after a spacewalk as being similar to burnt metal or gunpowder.\nThe smell comes from compounds that cling to their suits."
    },
    3: {
        "genre": "Space",
        "title": "The Largest Volcano",
        "content": "Olympus Mons on Mars is the largest known volcano in the Solar System.\nIt is about 22 km high, nearly three times the height of Mount Everest!"
    },
    4: {
        "genre": "Space",
        "title": "A Starry Sky",
        "content": "There are more stars in the observable universe than grains of sand on all of Earth's beaches.\nScientists estimate there may be hundreds of billions of galaxies."
    },
    5: {
        "genre": "Space",
        "title": "Moon Footprints",
        "content": "Footprints left by Apollo astronauts on the Moon could remain for millions of years.\nThere is no wind or rain on the Moon to erase them."
    },
    6: {
        "genre": "Space",
        "title": "Saturn's Rings",
        "content": "Saturn's rings are mostly made of pieces of ice and rock.\nSome pieces are as tiny as dust while others can be several metres wide."
    },
    7: {
        "genre": "Space",
        "title": "A Giant Space Cloud",
        "content": "The Boomerang Nebula is one of the coldest known natural places in the universe.\nIts temperature is even lower than the natural background temperature of space."
    },
    8: {
        "genre": "Space",
        "title": "Jupiter's Great Spot",
        "content": "Jupiter's Great Red Spot is a gigantic storm that has existed for centuries.\nIt is larger than Earth, although it has been shrinking over time."
    },
    9: {
        "genre": "Space",
        "title": "Floating Astronauts",
        "content": "Astronauts appear weightless in orbit because they and their spacecraft are constantly falling around Earth.\nThey are actually experiencing continuous free fall."
    },
    10: {
        "genre": "Space",
        "title": "The Sun's Size",
        "content": "About 1.3 million Earths could fit inside the Sun by volume.\nThe Sun contains almost all of the mass in our Solar System."
    },


    # 11–20: Animals 🐾
    11: {
        "genre": "Animals",
        "title": "Octopus Superpowers",
        "content": "Octopuses have three hearts and blue blood.\nTheir blood is blue because it uses copper-based hemocyanin to carry oxygen."
    },
    12: {
        "genre": "Animals",
        "title": "A Crow's Memory",
        "content": "Crows are incredibly intelligent birds and can remember human faces.\nThey can even learn to recognize people who have treated them badly."
    },
    13: {
        "genre": "Animals",
        "title": "Elephant Communication",
        "content": "Elephants can communicate using very low-frequency sounds called infrasound.\nThese sounds can travel over surprisingly long distances."
    },
    14: {
        "genre": "Animals",
        "title": "Sharks Are Ancient",
        "content": "Sharks existed before trees appeared on Earth.\nTheir ancestors have been swimming in Earth's oceans for hundreds of millions of years."
    },
    15: {
        "genre": "Animals",
        "title": "A Snail's Sleep",
        "content": "Some snails can sleep for extremely long periods of time.\nCertain species can remain inactive for months when conditions are unfavorable."
    },
    16: {
        "genre": "Animals",
        "title": "Dolphin Names",
        "content": "Bottlenose dolphins develop individual signature whistles.\nThese whistles work somewhat like names and help dolphins identify each other."
    },
    17: {
        "genre": "Animals",
        "title": "The Immortal Jellyfish",
        "content": "Turritopsis dohrnii is sometimes called the 'immortal jellyfish.'\nIt can potentially return to an earlier life stage instead of dying from old age."
    },
    18: {
        "genre": "Animals",
        "title": "Goats' Eyes",
        "content": "Goats have rectangular-shaped pupils.\nThis unusual shape gives them a wide field of vision, helping them spot predators."
    },
    19: {
        "genre": "Animals",
        "title": "Penguin Proposals",
        "content": "Some penguin species use pebbles as part of courtship.\nA male may offer a carefully chosen pebble to a potential mate."
    },
    20: {
        "genre": "Animals",
        "title": "Butterfly Taste Buds",
        "content": "Butterflies taste using sensors on their feet.\nThis helps them identify suitable plants for laying their eggs."
    },


    # 21–30: Science 🔬
    21: {
        "genre": "Science",
        "title": "Hot Water Can Freeze Faster",
        "content": "Under certain conditions, hot water can freeze faster than cold water.\nThis surprising phenomenon is called the Mpemba effect."
    },
    22: {
        "genre": "Science",
        "title": "Glass Is Not a Slow Liquid",
        "content": "Old windows are sometimes thicker at the bottom, but this is not because glass slowly flows like a liquid.\nThe unevenness usually came from older manufacturing methods."
    },
    23: {
        "genre": "Science",
        "title": "Your Body Glows",
        "content": "Humans actually emit tiny amounts of visible light.\nThe light is far too weak for our eyes to see and comes from chemical reactions in our cells."
    },
    24: {
        "genre": "Science",
        "title": "DNA Is Tiny",
        "content": "If all the DNA in one human cell were stretched out, it would be roughly two metres long.\nYet it fits inside a microscopic cell nucleus."
    },
    25: {
        "genre": "Science",
        "title": "Lightning Is Hot",
        "content": "A lightning bolt can heat the surrounding air to temperatures hotter than the surface of the Sun.\nThe rapid expansion of this hot air creates thunder."
    },
    26: {
        "genre": "Science",
        "title": "Water Can Boil and Freeze",
        "content": "At a specific pressure called the triple point, water can exist as a solid, liquid and gas simultaneously.\nThis happens under carefully controlled conditions."
    },
    27: {
        "genre": "Science",
        "title": "Your Bones Are Strong",
        "content": "Bone is remarkably strong for its weight.\nIts combination of minerals and flexible collagen makes it both hard and somewhat resilient."
    },
    28: {
        "genre": "Science",
        "title": "Bananas Are Slightly Radioactive",
        "content": "Bananas contain potassium, including a tiny amount of radioactive potassium-40.\nThe amount is harmless and extremely small."
    },
    29: {
        "genre": "Science",
        "title": "Sound Needs Matter",
        "content": "Sound cannot travel through empty space.\nIt needs particles, such as air, water or solids, to carry its vibrations."
    },
    30: {
        "genre": "Science",
        "title": "Ice Is Less Dense",
        "content": "Ice floats because solid water is less dense than liquid water.\nThis unusual property helps aquatic ecosystems survive cold winters."
    },


    # 31–40: History 🏛️
    31: {
        "genre": "History",
        "title": "Cleopatra's Timeline",
        "content": "Cleopatra lived closer in time to the Moon landing than to the construction of the Great Pyramid.\nThe Great Pyramid was already ancient when Cleopatra lived."
    },
    32: {
        "genre": "History",
        "title": "The Shortest War",
        "content": "The Anglo-Zanzibar War of 1896 lasted less than an hour.\nIt is commonly considered the shortest recorded war in history."
    },
    33: {
        "genre": "History",
        "title": "Ancient Roman Concrete",
        "content": "Some ancient Roman concrete structures have survived for nearly 2,000 years.\nResearchers continue studying why some Roman concrete became stronger over time."
    },
    34: {
        "genre": "History",
        "title": "Viking Helmets",
        "content": "There is no good evidence that Viking warriors commonly wore helmets with horns.\nThe horned helmet image became popular much later."
    },
    35: {
        "genre": "History",
        "title": "Oxford Is Very Old",
        "content": "Teaching was taking place at Oxford by the late 11th century.\nThat makes the university older than the Aztec Empire."
    },
    36: {
        "genre": "History",
        "title": "Ancient Egyptians and Cats",
        "content": "Cats were highly valued in ancient Egyptian society.\nThey were associated with several gods and were sometimes mummified."
    },
    37: {
        "genre": "History",
        "title": "The Great Fire",
        "content": "The Great Fire of London happened in 1666.\nIt destroyed thousands of buildings, but relatively few deaths were officially recorded."
    },
    38: {
        "genre": "History",
        "title": "Roman Concrete Underwater",
        "content": "Some Roman concrete structures were built underwater and have survived remarkably well.\nSeawater reactions helped strengthen certain types of the concrete."
    },
    39: {
        "genre": "History",
        "title": "Napoleon's Height",
        "content": "Napoleon was not exceptionally short for his time.\nThe famous image of him as extremely tiny was partly caused by differences between French and British measurement systems and later propaganda."
    },
    40: {
        "genre": "History",
        "title": "The First Computer Bug",
        "content": "In 1947, engineers found a moth trapped in a relay of the Harvard Mark II computer.\nThey taped the moth into their logbook and described it as the first actual case of 'debugging.'"
    },


    # 41–50: Technology 💻
    41: {
        "genre": "Technology",
        "title": "The First Website",
        "content": "The world's first website was created by Tim Berners-Lee.\nIt explained what the World Wide Web was and how people could use it."
    },
    42: {
        "genre": "Technology",
        "title": "The First Mouse",
        "content": "The first computer mouse was made from wood.\nIt was created by Douglas Engelbart and demonstrated in the 1960s."
    },
    43: {
        "genre": "Technology",
        "title": "QWERTY's Design",
        "content": "The QWERTY keyboard layout was designed for mechanical typewriters.\nOne goal was to reduce certain key-jamming problems."
    },
    44: {
        "genre": "Technology",
        "title": "Emoji History",
        "content": "The first widely used emoji set was created in Japan in the late 1990s.\nToday, emojis are used around the world in digital communication."
    },
    45: {
        "genre": "Technology",
        "title": "A Computer's Brain",
        "content": "The CPU is often called the 'brain' of a computer.\nIt performs instructions and carries out calculations needed by programs."
    },
    46: {
        "genre": "Technology",
        "title": "The First Video Game",
        "content": "One of the earliest electronic video games was 'Tennis for Two,' created in 1958.\nIt displayed a simple tennis-like game on an oscilloscope."
    },
    47: {
        "genre": "Technology",
        "title": "Tiny Transistors",
        "content": "Modern computer chips can contain billions of transistors.\nThese tiny electronic switches are fundamental building blocks of digital technology."
    },
    48: {
        "genre": "Technology",
        "title": "GPS Satellites",
        "content": "GPS works by measuring signals from multiple satellites.\nThe receiver uses differences in signal timing to calculate its position."
    },
    49: {
        "genre": "Technology",
        "title": "QR Codes",
        "content": "QR codes were originally developed in Japan for tracking automobile parts.\nTheir ability to store information in two dimensions made them very useful."
    },
    50: {
        "genre": "Technology",
        "title": "The Internet and Space",
        "content": "The Internet is not the same thing as the World Wide Web.\nThe Internet is the underlying network, while the Web is one service that runs on it."
    },


    # 51–60: Geography 🌍
    51: {
        "genre": "Geography",
        "title": "The Largest Country",
        "content": "Russia is the world's largest country by area.\nIt stretches across Europe and Asia and covers more than 17 million square kilometres."
    },
    52: {
        "genre": "Geography",
        "title": "The Deepest Ocean",
        "content": "The Mariana Trench contains the deepest known point in Earth's oceans.\nChallenger Deep reaches almost 11 kilometres below sea level."
    },
    53: {
        "genre": "Geography",
        "title": "The Smallest Country",
        "content": "Vatican City is the world's smallest country by both area and population.\nIt is located entirely within the city of Rome."
    },
    54: {
        "genre": "Geography",
        "title": "A Desert of Ice",
        "content": "Antarctica is technically a desert because it receives very little precipitation.\nIt is also the coldest continent on Earth."
    },
    55: {
        "genre": "Geography",
        "title": "The Longest Mountain Range",
        "content": "The Mid-Ocean Ridge is the longest mountain system on Earth.\nMost of it lies beneath the world's oceans."
    },
    56: {
        "genre": "Geography",
        "title": "Africa's Size",
        "content": "Africa is much larger than it often appears on common world maps.\nSome map projections distort the relative sizes of continents."
    },
    57: {
        "genre": "Geography",
        "title": "A Country in Two Continents",
        "content": "Turkey lies in both Europe and Asia.\nThe Bosporus Strait separates its European and Asian portions."
    },
    58: {
        "genre": "Geography",
        "title": "The Amazon River",
        "content": "The Amazon carries more water than any other river in the world.\nIts basin covers a huge portion of South America."
    },
    59: {
        "genre": "Geography",
        "title": "Mount Everest Moves",
        "content": "Mount Everest is slowly changing because the Himalayas are still being pushed upward by tectonic activity.\nThe mountain also experiences erosion and weathering."
    },
    60: {
        "genre": "Geography",
        "title": "Four Hemispheres",
        "content": "Kiribati is one of the few countries whose territory lies in all four hemispheres.\nIts islands stretch across both the equator and the International Date Line region."
    },


    # 61–70: Food 🍕
    61: {
        "genre": "Food",
        "title": "Honey Lasts Forever",
        "content": "Properly stored honey can remain edible for an extremely long time.\nIts low water content and acidity make it difficult for many microorganisms to grow."
    },
    62: {
        "genre": "Food",
        "title": "Chocolate and Dogs",
        "content": "Chocolate can be dangerous for dogs because it contains theobromine.\nDogs process this compound much more slowly than humans do."
    },
    63: {
        "genre": "Food",
        "title": "Pineapple and Your Tongue",
        "content": "Fresh pineapple contains bromelain, a group of enzymes that can break down proteins.\nThis is one reason pineapple can sometimes make your mouth feel strange."
    },
    64: {
        "genre": "Food",
        "title": "Carrots Weren't Always Orange",
        "content": "Early cultivated carrots came in colors including purple, yellow and white.\nOrange carrots became especially popular in Europe much later."
    },
    65: {
        "genre": "Food",
        "title": "Banana Berries",
        "content": "Botanically speaking, bananas are berries.\nStrawberries, surprisingly, are not true botanical berries."
    },
    66: {
        "genre": "Food",
        "title": "The World's Spiciest",
        "content": "Capsaicin is the chemical responsible for the burning sensation from chilli peppers.\nIt activates pain and heat receptors rather than actually burning your mouth."
    },
    67: {
        "genre": "Food",
        "title": "Popcorn Pops",
        "content": "A popcorn kernel contains a small amount of water trapped inside its starch.\nWhen heated, the water becomes steam and causes the kernel to explode outward."
    },
    68: {
        "genre": "Food",
        "title": "Apples Float",
        "content": "Apples float in water because they contain a surprisingly large amount of air.\nAir pockets make the fruit less dense than water."
    },
    69: {
        "genre": "Food",
        "title": "Cheese and Holes",
        "content": "The holes in some cheeses are created by carbon dioxide produced by bacteria.\nSwiss-style cheeses are famous for their large holes."
    },
    70: {
        "genre": "Food",
        "title": "Vanilla Comes From an Orchid",
        "content": "Vanilla comes from the pods of an orchid species.\nIt is one of the most labour-intensive spices to produce."
    },


    # 71–80: Animals: Weird & Wonderful 🦎
    71: {
        "genre": "Weird Animals",
        "title": "Axolotl Regeneration",
        "content": "Axolotls can regenerate limbs and several other body parts.\nScientists study them to better understand how regeneration works."
    },
    72: {
        "genre": "Weird Animals",
        "title": "A Shrimp's Punch",
        "content": "Mantis shrimp can strike with incredibly high-speed appendages.\nTheir attacks can create powerful shockwaves in the surrounding water."
    },
    73: {
        "genre": "Weird Animals",
        "title": "Platypus Glow",
        "content": "Platypus fur can fluoresce under ultraviolet light.\nScientists discovered this unusual feature relatively recently."
    },
    74: {
        "genre": "Weird Animals",
        "title": "Goose Teeth",
        "content": "Geese don't have true teeth, but they have tooth-like structures along their bills.\nThese structures help them tear and grip food."
    },
    75: {
        "genre": "Weird Animals",
        "title": "A Frog That Freezes",
        "content": "The wood frog can survive having much of its body freeze during winter.\nIts body uses special chemicals that protect its cells."
    },
    76: {
        "genre": "Weird Animals",
        "title": "Starfish Aren't Fish",
        "content": "Starfish are actually called sea stars because they are not fish.\nThey are echinoderms, related to sea urchins and sand dollars."
    },
    77: {
        "genre": "Weird Animals",
        "title": "Cows Have Best Friends",
        "content": "Studies suggest cows can form social bonds with particular companions.\nThey may become more stressed when separated from preferred companions."
    },
    78: {
        "genre": "Weird Animals",
        "title": "Goats Have Accents",
        "content": "Goats can develop different vocal patterns depending on their social environment.\nTheir calls can vary between groups."
    },
    79: {
        "genre": "Weird Animals",
        "title": "A Fish That Walks",
        "content": "Some fish can move across land using specialized fins and body movements.\nMudskippers are a famous example."
    },
    80: {
        "genre": "Weird Animals",
        "title": "The Tardigrade",
        "content": "Tardigrades are microscopic animals famous for surviving extreme conditions.\nThey can enter a dormant state that helps them withstand radiation, dehydration and extreme temperatures."
    },


    # 81–90: Inventions & Discoveries 💡
    81: {
        "genre": "Inventions",
        "title": "The Microwave Oven",
        "content": "The microwave oven was discovered partly because an engineer noticed that radar equipment had melted a chocolate bar in his pocket.\nThis led to experiments with heating food using microwaves."
    },
    82: {
        "genre": "Inventions",
        "title": "Velcro's Inspiration",
        "content": "Velcro was inspired by burrs sticking to clothing and animal fur.\nEngineer George de Mestral studied the burrs under a microscope."
    },
    83: {
        "genre": "Inventions",
        "title": "The Safety Pin",
        "content": "The modern safety pin was patented by Walter Hunt in 1849.\nHe reportedly invented it while trying to pay a debt."
    },
    84: {
        "genre": "Inventions",
        "title": "The Post-it Note",
        "content": "Post-it Notes came from an adhesive that was initially considered a failure because it was not very strong.\nIts ability to stick lightly and peel away became its biggest advantage."
    },
    85: {
        "genre": "Inventions",
        "title": "The Frisbee Connection",
        "content": "The modern Frisbee became popular after people started throwing pie tins made by the Frisbie Pie Company.\nThe name eventually became associated with flying discs."
    },
    86: {
        "genre": "Inventions",
        "title": "The Barcode",
        "content": "The first product scanned using a commercial barcode was a pack of chewing gum.\nThe scan took place in 1974 in an American supermarket."
    },
    87: {
        "genre": "Inventions",
        "title": "The Pencil Eraser",
        "content": "Before rubber erasers became common, people often used pieces of bread to erase pencil marks.\nRubber eventually became much more practical."
    },
    88: {
        "genre": "Inventions",
        "title": "The Traffic Light",
        "content": "Early traffic signals existed before modern electric traffic lights.\nOne early system used gas lamps and was installed in London in the 19th century."
    },
    89: {
        "genre": "Inventions",
        "title": "The First Photograph",
        "content": "One of the earliest surviving photographs required an exposure lasting many hours.\nModern cameras can capture images in fractions of a second."
    },
    90: {
        "genre": "Inventions",
        "title": "Bubble Wrap Wasn't for Packing",
        "content": "Bubble Wrap was originally invented as a type of textured wallpaper.\nIt became packaging material only after its original idea failed."
    },


    # 91–100: Random Facts 🎉
    91: {
        "genre": "Random",
        "title": "A Day Isn't Exactly 24 Hours",
        "content": "Earth's rotation does not take exactly 24 hours every day.\nThe length varies slightly, although 24 hours is a useful average for our clocks."
    },
    92: {
        "genre": "Random",
        "title": "Wombat Poop Is Cubes",
        "content": "Wombats produce cube-shaped poop.\nThe unusual shape is created inside their intestines and helps the poop stay where it is placed."
    },
    93: {
        "genre": "Random",
        "title": "A Group of Flamingos",
        "content": "A group of flamingos can be called a 'flamboyance.'\nThe name fits their famously bright pink appearance."
    },
    94: {
        "genre": "Random",
        "title": "Scotland's National Animal",
        "content": "Scotland's national animal is the unicorn.\nThe mythical creature has been associated with Scottish heraldry for centuries."
    },
    95: {
        "genre": "Random",
        "title": "The Eiffel Tower Changes Height",
        "content": "The Eiffel Tower can become slightly taller during hot weather.\nMetal expands when heated, causing the tower to grow by several centimetres."
    },
    96: {
        "genre": "Random",
        "title": "A Cloud Can Weigh a Lot",
        "content": "A large fluffy cloud can contain hundreds of tonnes of water droplets.\nIt stays in the sky because the water is spread across a huge volume and supported by rising air."
    },
    97: {
        "genre": "Random",
        "title": "Your Nose and Ears Keep Growing",
        "content": "Your nose and ears may appear to get larger as you age.\nThis is partly due to changes in cartilage and soft tissues over time."
    },
    98: {
        "genre": "Random",
        "title": "The Moon Has Quakes",
        "content": "The Moon experiences moonquakes.\nSome are caused by Earth's gravitational pull, while others result from temperature changes and impacts."
    },
    99: {
        "genre": "Random",
        "title": "A Day on Mercury",
        "content": "Mercury rotates very slowly compared with Earth.\nOne solar day on Mercury lasts about 176 Earth days."
    },
    100: {
        "genre": "Random",
        "title": "Lightning Strikes Earth",
        "content": "Lightning strikes somewhere on Earth many times every second.\nThousands of thunderstorms are happening around the planet at any given time."
    }
}
import random
import time

print("Welcome to Youtube Facts!")
time.sleep(1)

print("Let's get your feed ready")
time.sleep(1)
print("---------------------------")

x = random.randint(1, 100)

def type_text(text, speed=0.01):
    print(fun_facts[x]["title"])

    for i in text:
        print(i, end="", flush=True)
        time.sleep(speed)

def showreel():
    global x

    genres = []

    while True:

        # Show the current fact
        print()
        type_text(fun_facts[x]["content"])

        # Start timer AFTER the fact has finished
        start = time.time()

        a = input("\n")

        end = time.time()
        t = end - start

        current_genre = fun_facts[x]["genre"]

        # FAST response = show something different
        if t <= 5:
            y = random.randint(1, 100)

            while fun_facts[y]["genre"] == current_genre:
                y = random.randint(1, 100)

            x = y

        # MEDIUM response = somewhat similar feed
        elif t <= 10:
            y = random.randint(1, 100)

            if random.randint(1, 2) == 1:
                # Prefer the same genre
                same_genre = [
                    number
                    for number in fun_facts
                    if fun_facts[number]["genre"] == current_genre
                ]

                x = random.choice(same_genre)

            else:
                x = y

        # SLOW response = strongly recommend this genre
        else:
            genres.append(current_genre)

            same_genre = [
                number
                for number in fun_facts
                if fun_facts[number]["genre"] == current_genre
            ]

            x = random.choice(same_genre)

        print("---------------------------")


showreel()