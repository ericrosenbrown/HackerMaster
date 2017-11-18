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
    session.attributes['in_game'] = False

    return question(welcome_msg)


@ask.intent("YesIntent")

def next_round():
    if session.attributes['in_game'] == False:
        session.attributes['lives'] = 3
        r = random.choice(pp.row)
        c = random.choice(pp.col)
        p = random.choice(pp.places.keys())
        session.attributes['r'] = r
        session.attributes['c'] = c
        session.attributes['p'] = p

        session.attributes['in_game'] = True
    
        msg = render_template('set_diff', diff = [c,r,p])
        return question(msg)
    if session.attributes['in_game'] == True:
        return checkpass('dummy','dummy','dummy')

@ask.intent("AnswerIntent", convert={'stepone': str, 'steptwo': str, 'stepthree': str})

def checkpass(stepone,steptwo,stepthree):
    print 'their response: ',stepone, steptwo, stepthree
    tr = stepone + " " + steptwo + " " + stepthree
    mc = str(session.attributes['c'])
    mr = str(session.attributes['r'])
    mp = str(session.attributes['p'])
    action = "there was no action"
    print mc
    print pp.adjectives
    print pp.colors

    print mr
    print pp.animals
    print pp.people
    if mc in pp.adjectives and mr in pp.animals:
        action = "walks alone"
    if mc in pp.colors and mr in pp.animals:
        action = "has landed"
    if mc in pp.adjectives and mr in pp.people:
        action = "is in danger"
    if mc in pp.colors and mr in pp.people:
        action = "is waiting"

    rr = pp.places[mp] + " " + pp.chart[str([mc,mr])] + " " + action
    print 'the right response:', pp.places[mp], pp.chart[str([mc,mr])], action
    print rr == tr
    
    if rr == tr:
        msg = render_template('correct')
        session.attributes['in_game'] = False
    else:
        session.attributes['lives'] -= 1
        life = session.attributes['lives']
        if life == 0:
            msg = render_template('lose')
        else:
            msg = render_template('wrong', diff = [str(life),mc,mr,mp])
    return question(msg)


if __name__ == '__main__':

    app.run(debug=True)
