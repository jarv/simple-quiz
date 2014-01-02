import os
os.environ['FLASK_SETTINGS'] = 'cfg/prod.py'
from simple_quiz.models import Deck, Card, User, user_datastore, UserCardData, CardStates
from loremipsum import get_sentences
from random import choice, sample, randrange

Deck.objects.all().delete()
Card.objects.all().delete()
User.objects.all().delete()

admin_role = user_datastore.find_or_create_role(name="admin")
for num in range(10):
    test_user = user_datastore.create_user(email='test-{}@example.com'.format(num), password='test')
    user_datastore.add_role_to_user(test_user, admin_role)
    test_user.save()


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
        os.path.join(path, 'sample_imgs')) if 'README' not in img]

for x in range(0, 10):
    card_questions = get_sentences(20)
    card_answers = get_sentences(20)
    d = Deck.objects.create(slug=str(x), featured=True)
    user = user_datastore.find_user(email='test-{}@example.com'.format(choice(range(10))))
    d.user = user
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
            c.user = user
            c.save()
        cards.append(c.to_dbref())
    d.cards = cards
    d.save()

for num in range(10):
    v = user_datastore.find_user(email='test-{}@example.com'.format(num))
    # 100 random cards
    random_cards = sample(Card.objects.all(), 100)
    for card in random_cards:
        cdata = UserCardData.objects.create(card=card.to_dbref(),
            user=v.to_dbref(),
            card_state=choice([CardStates.learning, CardStates.wrong, CardStates.correct]),
            wrong=randrange(0, 100),
            correct=randrange(0, 100),
            learning=randrange(0, 100),
            rev_wrong=randrange(0, 100),
            rev_correct=randrange(0, 100),
            rev_learning=randrange(0, 100))
        cdata.save()
