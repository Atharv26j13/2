LANGUAGE DETECTIVE: COMPLETE ACTIVITY (teacher copy, contains the solution)

What is in this folder
- detective.py      : the full working solution.
- samples.py        : one training paragraph for each of the 7 languages (UTF-8 text).
- detective_app.py  : the Gradio web page (step 8). It uses detective.py.
- requirements.txt  : gradio and a recent jinja2 (needed only for the web page).

Setup
1. Python 3.10 or newer.
2. For the web page:  pip install -r requirements.txt

Run
- The program:   python detective.py        (Windows: py detective.py)
- The web page:  python detective_app.py    then open http://127.0.0.1:7860

Expected results (teacher): the game ends with "Detective: 7/7". The cold cases pizza, Hola!, 12345 and the Japanese sentence say Unknown.
Do not share this folder with students: the boilerplate zip is the student copy.
