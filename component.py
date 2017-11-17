import logging
import passphrase as pp

from random import randint
import random

from flask import Flask, render_template

from flask_ask import Ask, statement, question, session


app = Flask(__name__)

ask = Ask(app, "/")

logging.getLogger("flask_ask").setLevel(logging.DEBUG)


@ask.launch

def new_game():

    welcome_msg = render_template('welcome', number=[str(randint(0,9))] )

    return question(welcome_msg)


@ask.intent("YesIntent")

def next_round():

    numbers = [randint(0, 9) for _ in range(3)]

    round_msg = render_template('round', numbers=numbers)

    session.attributes['numbers'] = numbers[::-1]  # reverse

    return question(round_msg)


@ask.intent("SetDifficultyIntent", convert={'difficulty': str})

def setdif(difficulty):
    r = random.choice(pp.row)
    c = random.choice(pp.col)
    p = random.choice(pp.places.keys())
    session.attributes['r'] = r
    session.attributes['c'] = c
    session.attributes['p'] = p
    
    msg = render_template('set_diff', diff = [difficulty,c,r,p])
    return question(msg)

@ask.intent("AnswerIntent", convert={'stepone': str, 'steptwo': str, 'stepthree': str})

def checkpass(stepone,steptwo,stepthree):
    print 'their response: ',stepone, steptwo, stepthree
    mc = str(session.attributes['c'])
    mr = str(session.attributes['r'])
    mp = str(session.attributes['p'])
    #if pp.places[mp] in adjectives and pp.chart[str([mc,mr])]
    print 'the right response:', pp.places[mp], pp.chart[str([mc,mr])]

"""
@ask.intent("AnswerIntent", convert={'first': int, 'second': int, 'third': int})

def answer(first, second, third):

    winning_numbers = session.attributes['numbers']

    if [first, second, third] == winning_numbers:

        msg = render_template('win')

    else:

        msg = render_template('lose')

    return statement(msg)
"""

if __name__ == '__main__':

    app.run(debug=True)
