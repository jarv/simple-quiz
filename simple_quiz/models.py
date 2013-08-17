from simple_quiz import app, db
from flask.ext.security import Security, MongoEngineUserDatastore, \
    UserMixin, RoleMixin, login_required

# Setup Flask-Security

class Role(db.Document, RoleMixin):
    name = db.StringField(max_length=80, unique=True)
    description = db.StringField(max_length=255)

class CompletedDeck(db.EmbeddedDocument):
    deck = db.ReferenceField('Deck')
    completed_on = db.DateTimeField()
    lapses = db.IntField()
    time_to_complete = db.DateTimeField()


class User(db.Document, UserMixin):
    email = db.EmailField(max_length=255, unique=True)
    name = db.StringField(max_length=255)
    password = db.StringField(max_length=255)
    active = db.BooleanField(default=True)
    confirmed_at = db.DateTimeField()
    roles = db.ListField(db.ReferenceField('Role'), default=[])
    cards = db.DictField()


class Deck(db.Document):
    slug = db.StringField(max_length=50, unique=True)
    public = db.BooleanField()
    title = db.StringField(max_length=120)
    author = db.ReferenceField('User', reverse_delete_rule=db.CASCADE)
    cards = db.ListField(db.ReferenceField('Card'), default=[])
    featured = db.BooleanField(default=False)


class Card(db.Document):
    front_text = db.StringField()
    back_text = db.StringField()
    front_img = db.ImageField(size=(150,180), thumbnail_size=(60,80))
    back_img = db.ImageField(size=(150,180), thumbnail_size=(60,80))

user_datastore = MongoEngineUserDatastore(db, User, Role)
security = Security(app, user_datastore)


def is_authorized(user, deck):
    if 'admin' in [role.name for role in user.roles]:
        return True
    if deck.author == user:
        return True
    return False
