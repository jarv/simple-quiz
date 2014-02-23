from simple_quiz import app, db
from flask.ext.security import Security, MongoEngineUserDatastore, \
    UserMixin, RoleMixin, login_required
import datetime

class CardStates:
    review = 1
    training = 2
    correct = 3
    learning = 4
    learned = 5

class DeckStates:
    mnemonic = 0
    review = 1
    training = 2
    correct = 3
    learning = 4
    learned = 5


# Setup Flask-Security

class Role(db.Document, RoleMixin):
    name = db.StringField(max_length=80, unique=True)
    description = db.StringField(max_length=255)


class UserDeckData(db.Document):
    deck = db.ReferenceField('Deck')
    user = db.ReferenceField('User')
    deck_state = db.IntField(choices=[DeckStates.mnemonic, DeckStates.training, DeckStates.learning, DeckStates.learned], default=DeckStates.mnemonic)


class UserCardData(db.Document):
    card = db.ReferenceField('Card')
    user = db.ReferenceField('User')
    card_state = db.IntField(choices=[CardStates.review, CardStates.training, CardStates.learning, CardStates.learned], default=CardStates.review)
    # card history counts
    wrong = db.IntField()
    correct = db.IntField()
    learning = db.IntField()
    last_review = db.DateTimeField(default=None)
    last_training = db.DateTimeField(default=None)
    last_learning = db.DateTimeField(default=None)
    last_learned = db.DateTimeField(default=None)
    num_review = db.IntField()
    num_training = db.IntField()
    num_learning = db.IntField()
    num_learned = db.IntField()
    num_lapses = db.IntField()
    date_modified = db.DateTimeField(default=datetime.datetime.now)


class User(db.Document, UserMixin):
    email = db.EmailField(max_length=255, unique=True)
    name = db.StringField(max_length=255)
    password = db.StringField(max_length=255)
    active = db.BooleanField(default=True)
    confirmed_at = db.DateTimeField()
    roles = db.ListField(db.ReferenceField('Role'), default=[])


class Deck(db.Document):
    slug = db.StringField(max_length=50, unique=True)
    user = db.ReferenceField('User', reverse_delete_rule=db.CASCADE)
    title = db.StringField(max_length=120)
    featured = db.BooleanField(default=False)
    date_modified = db.DateTimeField(default=datetime.datetime.now)
    cards = db.ListField(db.ReferenceField('Card'), default=[])
    mnemonic = db.ListField(default=[])
    mnemonic_positions = db.ListField(default=[])
    turn_time = db.IntField()


class Card(db.Document):
    user = db.ReferenceField('User')
    public = db.BooleanField(default=True)
    front_text = db.StringField()
    front_img = db.ImageField(size=(150,180), thumbnail_size=(60,80))
    date_modified = db.DateTimeField(default=datetime.datetime.now)
    answer = db.IntField()

user_datastore = MongoEngineUserDatastore(db, User, Role)
security = Security(app, user_datastore)


def is_authorized(user, deck):
    if 'admin' in [role.name for role in user.roles]:
        return True
    if deck.user == user:
        return True
    return False
