from simple_quiz import app, db
from flask.ext.security import Security, MongoEngineUserDatastore, \
    UserMixin, RoleMixin, login_required
import datetime

class CardStates:
    review = 0
    correct = 1
    learning = 2
    wrong = 3

# Setup Flask-Security

class Role(db.Document, RoleMixin):
    name = db.StringField(max_length=80, unique=True)
    description = db.StringField(max_length=255)

class UserCardData(db.Document):
    card = db.ReferenceField('Card')
    user = db.ReferenceField('User')
    card_state = db.IntField(choices=[CardStates.wrong, CardStates.correct, CardStates.learning], default=CardStates.learning)
    # card history counts
    wrong = db.IntField()
    correct = db.IntField()
    learning = db.IntField()
    last_wrong = db.DateTimeField(default=None)
    last_correct = db.DateTimeField(default=None)
    last_learning = db.DateTimeField(default=None)
    rev_wrong = db.IntField()
    rev_correct = db.IntField()
    rev_learning = db.IntField()
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
    round_time = db.IntField()


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
