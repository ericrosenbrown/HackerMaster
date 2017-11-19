import logging
import passphrase as pp

from random import randint
import random

from xml.etree import ElementTree

from flask import Flask, render_template

from flask_ask import Ask, statement, question, session


app = Flask(__name__)

ask = Ask(app, "/")

logging.getLogger("flask_ask").setLevel(logging.DEBUG)

def my_output_speech(speech):
    try:
        xmldoc = ElementTree.fromstring(speech)
        if xmldoc.tag == 'speak':
            return {'type': 'SSML', 'ssml': speech}
    except (UnicodeEncodeError, ElementTree.ParseError) as e:
        pass
    return {'type': 'PlainText', 'text': speech}

@ask.launch
def new_game():
    session.attributes['in_game'] = False
    welcome_msg = render_template('welcome_with_audio', number=[str(randint(0,9))])
    return question(welcome_msg).standard_card(title='Hacker Manual', text='URL to manual')


def generate_secure_phassphrase():
    random.seed()
    secure_noun = random.choice(pp.row)
    secure_adjective = random.choice(pp.col)
    secure_place = random.choice(pp.places.keys())
    return secure_noun, secure_adjective, secure_place


def get_right_response(secure_adjective, secure_noun, secure_place):
    if secure_adjective in pp.adjectives and secure_noun in pp.animals:
        secret_action = "walks alone"
    elif secure_adjective in pp.colors and secure_noun in pp.animals:
        secret_action = "has landed"
    elif secure_adjective in pp.adjectives and secure_noun in pp.people:
        secret_action = "is in danger"
    elif secure_adjective in pp.colors and secure_noun in pp.people:
        secret_action = "is waiting"
    else:
        secret_action = "error"
    print pp.places[secure_place]
    print pp.chart[str([secure_adjective, secure_noun])]
    print secret_action
    return '{} {} {}'.format(pp.places[secure_place], pp.chart[str([secure_adjective, secure_noun])], secret_action)

@ask.intent("AMAZON.YesIntent")
def next_round():
    if session.attributes['in_game'] == False:
        session.attributes['lives'] = 3
        session.attributes['current_round'] = 0
        secure_noun, secure_adjective, secure_place = generate_secure_phassphrase()
        session.attributes['secure_noun'] = secure_noun
        session.attributes['secure_adjective'] = secure_adjective
        session.attributes['secure_place'] = secure_place
        session.attributes['in_game'] = True
    
        msg = render_template('set_secure_passphrase', secure_passphrase=[secure_adjective,secure_noun,secure_place])

        right_response = get_right_response(secure_adjective, secure_noun, secure_place)
        print 'the right response: {}'.format(right_response)


        return question(msg)
    elif session.attributes['in_game'] == True:
        return checkpass('dummy', 'dummy', 'dummy')


@ask.intent("AnswerIntent", convert={'stepone': str, 'steptwo': str, 'stepthree': str})
def checkpass(stepone,steptwo,stepthree):
    """

    :param stepone:
    :param steptwo:
    :param stepthree:
    :return:
    """
    # sanity check that they didn't give an answer with no question
    if session.attributes['in_game'] == False:
        msg = render_template('answer_with_no_question')
        return question(msg)

    stepone = str(stepone).lower()
    steptwo = str(steptwo).lower()
    stepthree = str(stepthree).lower()
    print 'their response: ',stepone, steptwo, stepthree
    their_response = stepone + " " + steptwo + " " + stepthree
    secure_adjective = str(session.attributes['secure_adjective'])
    secure_noun = str(session.attributes['secure_noun'])
    secure_place = str(session.attributes['secure_place'])
    print 'alexa said: {} {} {}'.format(secure_adjective, secure_noun, secure_place)

    right_response = get_right_response(secure_adjective, secure_noun, secure_place)
    print 'the right response: {}'.format(right_response)

    print right_response == their_response

    if right_response == their_response:
        session.attributes['current_round'] += 1
        if session.attributes['current_round'] >= 5:
            msg = render_template('win')
            session.attributes['in_game'] = False
        else:
            secure_noun, secure_adjective, secure_place = generate_secure_phassphrase()
            session.attributes['secure_noun'] = secure_noun
            session.attributes['secure_adjective'] = secure_adjective
            session.attributes['secure_place'] = secure_place
            msg = render_template('correct', secure_passphrase=[str(session.attributes['current_round'] * 20),
                                                                secure_adjective, secure_noun, secure_place])
            print get_right_response(secure_adjective, secure_noun, secure_place)
    else:
        session.attributes['lives'] -= 1
        life = session.attributes['lives']
        if life == 0:
            msg = render_template('lose')
            session.attributes['in_game'] = False
        else:
            msg = render_template('wrong', secure_passphrase=[str(life), secure_adjective, secure_noun, secure_place])
    return question(msg)

@ask.intent("SendPdfIntent")
def send_pdf_card():
    return question('Say yes when you have the hacker manual').standard_card(title='Hacker Manual', text='URL to manual')

@ask.intent('AMAZON.NoIntent')
@ask.intent('AMAZON.PauseIntent')
@ask.intent('AMAZON.StopIntent')
@ask.intent('AMAZON.CancelIntent')
def stop_audio_and_exit():
    return statement('')


if __name__ == '__main__':

    app.run(debug=True)
