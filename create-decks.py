import os
os.environ['FLASK_SETTINGS'] = 'cfg/prod.py'
import sys
from simple_quiz.models import Deck, Card, User, user_datastore, UserCardData, CardStates
import yaml

ADMIN_EMAIL = 'test@example.com'
ADMIN_PASS = 'test'

Deck.objects.all().delete()
Card.objects.all().delete()
User.objects.all().delete()

# create admin user

admin_role = user_datastore.find_or_create_role(name="admin")
admin_user = user_datastore.create_user(email=ADMIN_EMAIL, password=ADMIN_PASS)
user_datastore.add_role_to_user(admin_user, admin_role)
admin_user.save()


path = os.path.dirname(os.path.abspath(__file__))

with open('deck-data.yaml') as f:
    deck_data = yaml.load(f.read())
    for deck in deck_data:
        d = Deck.objects.create(slug=str(deck['slug']), featured=deck['featured'])
        d.mnemonic = deck['mnemonic']
        d.mnemonic_positions = deck['mnemonic_positions']
        d.title = deck['title']
        d.user = user_datastore.find_user(email=ADMIN_EMAIL)
        d.round_time = 20
        cards = []
        for card in deck['cards']:
            c = Card.objects.create()
            if card['front_text']:
                c.front_text = card['front_text']
            if card['front_img']:
                with open(card['front_img']) as f:
                    c.front_img = f
            c.answer = card['answer']
            c.save()
            cards.append(c)
        d.cards = cards
        d.save()
