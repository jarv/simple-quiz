from simple_quiz import app
from simple_quiz.models import Deck, Card, User
from simple_quiz.models import user_datastore, is_authorized
from flask import request, render_template, abort, flash, redirect
from flask.ext.security import Security, MongoEngineUserDatastore, \
    UserMixin, RoleMixin, login_required, LoginForm
from flask.ext.login import current_user, login_user
from werkzeug import secure_filename
from werkzeug import Response

import os

import simplejson
from mongoengine.queryset import DoesNotExist
from mongoengine import ValidationError
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


@app.route('/', methods=["GET", "POST"])
def index():
    form = LoginForm()
    if request.method == "POST":
        if form.validate_on_submit():
            login_user(form.user, remember=form.remember.data)
    print 'errors: {}'.format(form.errors)
    print 'email: {}'.format(form.email)
    print 'is_submitted: {}'.format(form.is_submitted)

    return render_template('index.html', login_user_form=form)

@app.route('/login_test')
@login_required
def login_test():
    return "hello world"

@app.route('/img/<img_type>/<cid>/<gridfs_id>', defaults={'size': None},
           methods=["GET"])
@app.route("/img/<img_type>/<cid>/<gridfs_id>/<size>", methods=["GET"])
def get_img(img_type, cid, size, gridfs_id):

    if not img_type or img_type not in ['front_img', 'back_img']:
        abort(404)

    try:
        card = Card.objects.get(id=cid)
    except ValidationError:
        abort(404)

    if size == 'thumb':
        return Response(getattr(card, img_type).thumbnail.read())
    else:
        return Response(getattr(card, img_type).read())


@app.route("/update_card", methods=["POST"])
def update_card():
    # update_card will update a card
    # in a deck

    img_types = []
    ret_status = {}

    try:
        deck = Deck.objects.get(id=request.form['deck_id'])
    except ValidationError as e:
        abort(404)

    if not is_authorized(current_user, deck):
        abort(404)

    is_new_card = False
    if request.form['card_id'] == 'new':
        print "Creating new card"
        # create a new card
        card = Card.objects.create()
        is_new_card = True
    else:
        card = Card.objects.get(id=request.form['card_id'])

    if 'delete_card' in request.form:
        print "Deleting card"
        deck.cards.remove(card)
        deck.save()
        return(simplejson.dumps({'status': 'success'}))

    if 'front_img' in request.files:
        img_types.append('front_img')
    if 'back_img' in request.files:
        img_types.append('back_img')
    for img_type in img_types:
        data_file = request.files.get(img_type)
        if data_file:
            if getattr(card, img_type).grid_id is None:
                getattr(card, img_type).put(data_file)
            else:
                getattr(card, img_type).replace(data_file)

    card.front_text = request.form['front']
    card.back_text = request.form['back']
    card.save()

    if is_new_card:
        # if it's a new card, add it to the deck
        deck.cards.append(card)
        deck.save()

    ret_status.update({
        'id': str(card.id),
        'front_text': card.front_text,
        'back_text': card.back_text
    })

    for img_type in img_types:
        if getattr(card, img_type).grid_id is not None:
            ret_status[img_type] = 'img/{img_type}/{cid}/{grid_id}'.format(
                img_type=img_type, cid=card.id,
                grid_id=getattr(card, img_type).grid_id)
    print ret_status
    return simplejson.dumps(ret_status)


@app.route("/card/<id>", methods=["PUT", "POST", "DELETE"])
def card(id):
    if request.method == "DELETE":
        return 'ok'
    data = simplejson.loads(request.data)
    (card, created) = Card.objects.get_or_create(id=id)
    if 'front_text' in data:
        card.front_text = data['front_text']
    if 'back_text' in data:
        card.back_text = data['back_text']
    card.save()
    return simplejson.dumps({'status': 'ok'})



@app.route('/whoami')
def whoami():
    if current_user.is_authenticated():
        return simplejson.dumps({'loggedin': True})
    else:
        return simplejson.dumps({'loggedin': False})


@app.route('/update-deck/<slug>', methods=['POST'])
#@login_required
def update_deck(slug=None):
    """
    Replaces or creates <slug> with post
    data which should be stringify'd
    json that looks like the following

    json_data:  json_string({
                    title:
                    public:
                    cards: [

                    ]
                })

    returns:

    {
        status: {created, updated, error}
        msg: ''
    }
    """

    try:
        data = simplejson.loads(request.form['json_data'])
        (d, created) = Deck.objects.get_or_create(slug=slug)
        d.public = data['public']
        d.title = data['title']
        # create the cards
        d.cards = [Card(**card) for card in data['cards']]
        # associate the user
        d.author = current_user.to_dbref()
        d.save()

    except Exception as e:
        print e
        return(simplejson.dumps({'status': 'error'}))
        raise

    if created:
        return(simplejson.dumps({'status': 'created'}))
    else:
        return(simplejson.dumps({'status': 'updated'}))


@app.route('/deck-edit')
@login_required
def view():
    return render_template('deck-edit.html')


@app.route('/featured_decks')
def featured_decks():
    """
    Returns list of featured
    decks
    """
    try:
        decks = Deck.objects.filter(featured=True)
    except DoesNotExist:
        return simplejson.dumps({})
    print [{'title': deck['title']} for deck in decks]
    return simplejson.dumps([{'title': deck['title'],
                              'slug': deck['slug']} for deck in decks])


@app.route('/deck/<slug>')
#@login_required
def deck(slug=None):
    """
    Returns information about a deck as a
    JSON object.  If the deck is not public
    ensure the at the logged in user owns
    the deck.

    {
        id:
        title:
        author-email:
        author-name:
        public:
        can_modify:
        cards: [


        ]
    }
    """

    try:
        deck = Deck.objects.get(slug=slug)
    except DoesNotExist:
        return simplejson.dumps({})

    cards = []
    for card in deck.cards:
        front_img = False
        back_img = False
        if card['front_img'].grid_id is not None:
            front_img = 'img/front_img/{cid}/{grid_id}'.format(cid=card.id,
                        grid_id=card['front_img'].grid_id)
        if card['back_img'].grid_id is not None:
            back_img = 'img/back_img/{cid}/{grid_id}'.format(cid=card.id,
                        grid_id=card['back_img'].grid_id)
        cards.append(dict(front_img=front_img, back_img=back_img,
                          front_text=card['front_text'],
                          back_text=card['back_text'],
                          id=str(card.id)))

    can_write = False

    if current_user.is_authenticated():
        admin_role = user_datastore.find_role("admin")
        if admin_role in current_user.roles:
            # admins can write to all decks
            can_write = True

    data = {
        'id': str(deck.id),
        'can_write': can_write,
        'title': deck.title,
        'cards': cards,
    }
    return simplejson.dumps(data)
