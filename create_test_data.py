from simple_quiz import app
from simple_quiz.models import Deck, Card, User
from flask import request, render_template
from flask.ext.security import Security, MongoEngineUserDatastore, \
    UserMixin, RoleMixin, login_required, LoginForm
from flask.ext.login import current_user
import os

import simplejson
from mongoengine.queryset import DoesNotExist
from loremipsum import get_paragraphs, get_sentences
from random import choice

Deck.objects.all().delete()
Card.objects.all().delete()


class CardTypes:
    img_only = 0
    text_only = 1
    text_and_img = 2
    img_and_text = 3

path = os.path.dirname(os.path.abspath(__file__))
card_types = [CardTypes.img_only, CardTypes.text_only,
              CardTypes.text_and_img, CardTypes.img_and_text]


# Create 100 decks
deck_titles = get_sentences(100)

data = []

imgs = ['sample_imgs/' + img for img in os.listdir(
        os.path.join(path, 'sample_imgs'))]

for x in range(0, 10):
    card_questions = get_sentences(20)
    card_answers = get_sentences(20)
    d = Deck.objects.create(slug=str(x), featured=True)
    d.title = deck_titles[x][:50]
    cards = []
    for y in range(0, 20):
        card_type = choice(card_types)
        front_text = card_questions[y]
        back_text = card_answers[y]
        with open(choice(imgs)) as front_img, open(choice(imgs)) as back_img:
            print front_img.name
            print back_img.name

            if card_type == CardTypes.img_only:
                c = Card.objects.create(front_img=front_img,
                                        back_img=back_img)
            elif card_type == CardTypes.text_only:
                c = Card.objects.create(front_text=front_text,
                                        back_text=back_text)
            elif card_type == CardTypes.text_and_img:
                c = Card.objects.create(front_text=front_text,
                                        back_img=back_img)
            elif card_type == CardTypes.img_and_text:
                c = Card.objects.create(back_text=back_text,
                                        front_img=front_img)
            c.save()
        cards.append(c.to_dbref())
    d.cards = cards
    d.save()
