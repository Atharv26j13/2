"""
Training samples for the Language Detective.
Every sample says (almost) the SAME thing, so the only difference between
them is the language itself. Want a new language? Add a new paragraph!
"""

SAMPLES = {
    "English": (
        "Every morning I wake up early and drink a glass of water. My school starts at eight, "
        "so I walk there with my friends. We talk about games, music and the homework we did not "
        "finish. In the afternoon I like to play football in the park near my house. When it rains, "
        "I stay inside and read a book or watch a film with my family. My favourite food is pasta, "
        "but my brother thinks pizza is better. At night we eat dinner together and talk about our "
        "day. Tomorrow we are going to visit my grandmother in the countryside."
    ),
    "Spanish": (
        "Todas las mañanas me levanto temprano y bebo un vaso de agua. Mi escuela empieza a las "
        "ocho, así que camino hasta allí con mis amigos. Hablamos de juegos, de música y de los "
        "deberes que no terminamos. Por la tarde me gusta jugar al fútbol en el parque que está "
        "cerca de mi casa. Cuando llueve, me quedo en casa y leo un libro o veo una película con mi "
        "familia. Mi comida favorita es la pasta, pero mi hermano piensa que la pizza es mejor. Por "
        "la noche cenamos juntos y hablamos de nuestro día. Mañana vamos a visitar a mi abuela en "
        "el campo."
    ),
    "Italian": (
        "Ogni mattina mi sveglio presto e bevo un bicchiere d'acqua. La mia scuola comincia alle "
        "otto, quindi ci vado a piedi con i miei amici. Parliamo di giochi, di musica e dei compiti "
        "che non abbiamo finito. Il pomeriggio mi piace giocare a calcio nel parco vicino a casa "
        "mia. Quando piove, resto a casa e leggo un libro o guardo un film con la mia famiglia. Il "
        "mio cibo preferito è la pasta, ma mio fratello pensa che la pizza sia migliore. La sera "
        "ceniamo insieme e parliamo della nostra giornata. Domani andiamo a trovare mia nonna in "
        "campagna."
    ),
    "French": (
        "Chaque matin, je me réveille tôt et je bois un verre d'eau. Mon école commence à huit "
        "heures, alors j'y vais à pied avec mes amis. Nous parlons de jeux, de musique et des "
        "devoirs que nous n'avons pas finis. L'après-midi, j'aime jouer au football dans le parc "
        "près de chez moi. Quand il pleut, je reste à la maison et je lis un livre ou je regarde un "
        "film avec ma famille. Mon plat préféré, ce sont les pâtes, mais mon frère pense que la "
        "pizza est meilleure. Le soir, nous dînons ensemble et nous parlons de notre journée. "
        "Demain, nous allons rendre visite à ma grand-mère à la campagne."
    ),
    "German": (
        "Jeden Morgen stehe ich früh auf und trinke ein Glas Wasser. Meine Schule beginnt um acht "
        "Uhr, deshalb gehe ich mit meinen Freunden zu Fuß dorthin. Wir sprechen über Spiele, Musik "
        "und die Hausaufgaben, die wir nicht fertig gemacht haben. Am Nachmittag spiele ich gern "
        "Fußball im Park in der Nähe von meinem Haus. Wenn es regnet, bleibe ich zu Hause und lese "
        "ein Buch oder schaue mit meiner Familie einen Film. Mein Lieblingsessen ist Pasta, aber "
        "mein Bruder findet Pizza besser. Am Abend essen wir zusammen und sprechen über unseren "
        "Tag. Morgen besuchen wir meine Oma auf dem Land."
    ),
    "Hindi": (
        "हर सुबह मैं जल्दी उठता हूँ और एक गिलास पानी पीता हूँ। मेरा स्कूल आठ बजे शुरू होता है, "
        "इसलिए मैं अपने दोस्तों के साथ पैदल जाता हूँ। हम खेलों, संगीत और उस होमवर्क के बारे में "
        "बात करते हैं जो हमने पूरा नहीं किया। दोपहर में मुझे घर के पास वाले पार्क में फुटबॉल खेलना "
        "पसंद है। जब बारिश होती है, तो मैं घर पर रहता हूँ और किताब पढ़ता हूँ या अपने परिवार के "
        "साथ फ़िल्म देखता हूँ। मेरा पसंदीदा खाना पास्ता है, लेकिन मेरे भाई को लगता है कि पिज़्ज़ा "
        "बेहतर है। रात को हम साथ में खाना खाते हैं और अपने दिन के बारे में बात करते हैं। कल हम "
        "गाँव में अपनी दादी से मिलने जाएँगे।"
    ),
    "Hinglish": (
        "Har subah main jaldi uthta hoon aur ek glass paani peeta hoon. Mera school aath baje "
        "shuru hota hai, isliye main apne doston ke saath paidal jaata hoon. Hum games, music aur "
        "us homework ke baare mein baat karte hain jo humne poora nahi kiya. Dopahar mein mujhe "
        "ghar ke paas wale park mein football khelna pasand hai. Jab baarish hoti hai, toh main "
        "ghar par rehta hoon aur kitaab padhta hoon ya family ke saath movie dekhta hoon. Mera "
        "favourite khana pasta hai, lekin mere bhai ko lagta hai ki pizza better hai. Raat ko hum "
        "saath mein khana khaate hain aur apne din ke baare mein baat karte hain. Kal hum gaon "
        "mein apni dadi se milne jaayenge."
    ),
}
