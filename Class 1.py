responses = []
print("What is your name human?")
a = (input(">>"))
print("Who...")
b = (input(">>"))
if a == b:
    print("...asked?")
else:
    print("...are you? You inconsistent person.")

print("Are you offended little (wo)man? Yes or no")
a = input(">>")
if a.lower() == "yes":
    print("Softer than a pillow, both physically and mentally!")
    a = input(">>")
    print("Sorry, couldn't hear you over my sick BURN!")
    print("CHAT ENDED")
elif a.lower() == "no":
    print("Skin of an elephant and the size of one!")
    a = input(">>")
    print("Bro, don't get too angry, if you jump it might cause an earthquake!")
    print("What is your weight?")
    a = int(input(">>"))
    if a > 50:
        print("Elephant family!")
        print("CHAT ENDED")
    elif a<50 and a>0:
        print("EAT PROTEIN YOU SMALL FRY! WILL YOU OR WILL YOU NOT! YES OR NO!")
        a = input(">>")
        if a.lower() == "yes":
            print("Okay, at least you'll be able to be classified as a grasshopper and not an ant.")
            print("CHAT ENDED")
        elif a.lower() == "no":
            print("I need to watch my step. I might squish you")
            print("CHAT ENDED")
        else:
            print("Error 404 braincells not found.")
            print("CHAT ENDED")
    else:
        print("Antimatter.")
        print("CHAT ENDED")
else:
    print("Broz tuff withh hiz shpellingz.")
    print("CHAT ENDED")