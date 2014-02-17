class DeckModel extends Backbone.Model
  defaults: ->
    new_card: false


class CardModel extends Backbone.Model
  defaults: ->
    is_selected: false
    selected_card: null
  toggle_selected: ->
    @set({'is_selected': !@get('is_selected')})


class CardList extends Backbone.Collection
  model: CardModel
  selected: ->
    @where({is_selected: true})
class AppRouter extends Backbone.Router
  routes:
    "deck/:id": "getDeck"
    "*actions": "defaultRoute"
class CardView extends Backbone.View
  tagName: 'div'
  attributes: ->
    'class': 'box'
  events:
    'click': 'selectCard'
  initialize: ->
    @listenTo(@model, 'change', @render)
    @listenTo(@model, 'remove', @remove)
    undefined
  clear: ->
    @model.destroy()
    undefined
  render: ->
    variables = {
      front_text: @model.get('front_text')
      front_img: @model.get('front_img')
    }
    template = _.template($("#box_template").html(), variables)
    @$el.html(template)
    @
  selectCard: ->
    active_deck.new_card = false
    clicked_model = @model
    # save the last card selected so that it isn't
    # shown immediately due to hover
    active_deck.last_selected = active_deck.selected_card
    if active_deck.selected_card && active_deck.selected_card != clicked_model
      # toggle the selected state of the previously
      # selected card
      active_deck.selected_card.toggle_selected()


    clicked_model.toggle_selected()

    variables = {
      front_text: clicked_model.get('front_text')
      front_img: clicked_model.get('front_img')
    }
 
    if clicked_model.get('is_selected')
      active_deck.selected_card = clicked_model
      $('.box').removeClass('select')
      $(@el).addClass('select')
      $('#quiz_input').html(_.template( $('#quiz_input_template').html(), variables ))
      $('#quiz_input').show()
    else
      active_deck.selected_card = null
      $(@el).removeClass('select')
      $('#quiz_input').hide()
    undefined
# END class CardView extends Backbone.View

# display the quiz board
class QuizView extends Backbone.View
  el: $('#quiz')

# game board
class BoardView extends Backbone.View
  CardStates =
    review: 0
    correct: 1
    learning: 2
    wrong: 3

  el: $('#deck_view')
  events:
    'click #hide_quiz_input': 'hideQuizInput'
    'click #login_link': 'showLogin'
    'click #submit_card': 'updateCard'
    'click #delete_card': 'deleteCard'
    'click #click_add_card': 'addCard'
    'click #click_start_quiz': 'startQuiz'
    'click #click_select_deck': 'clickDeck'
    'change #front_img': 'updateImgFront'
    'mouseleave #content': 'leaveBoard'
  startQuiz: ->
    # hide the board
    $('#container').hide()
    # hide the header and detailed card view
    $('#deck_header').hide()
    $('#quiz_input').hide()
    # show the mnemonic
    $('#quiz_mnemonic').html(active_deck.toJSON().mnemonic.join(' '))
    $('#quiz').show()
    round_time = active_deck.toJSON().mnemonic.length * 5000
    mnemonics = active_deck.toJSON().mnemonic
    mnemonic_cnt = 0
    active_deck.round_time = active_deck.toJSON().round_time
    to_quiz = active_deck.toJSON().cards
    # shuffle the cards to quiz
    to_quiz = _.shuffle(to_quiz)
    for c in to_quiz
      if c.front_img
        $("<img />").attr("src", c.front_img)
        $("<img />").attr("src", c.front_img + '/thumb')
      # Create an array of boxes for masonry
      to_quiz.$box = $(_.template( $("#quiz_answer_template").html(), c))
      $('#quiz_answer').append(to_quiz.$box).masonry('reload')

    game_loop = () ->
      got_answer = false
      cur_time = Math.floor(new Date().getTime() / 1000)
      round_time = cur_time - active_deck.start_time
      answer = (c for c in to_quiz when c.answer == mnemonic_cnt)[0].front_text
      console.log($('#quiz_answer_input').val())
      if $('#quiz_answer_input').val() == answer
        got_answer = true
      #if (c for c in to_quiz when not c.blur).length > 1
      #  to_blur = _.sample((c for c in to_quiz when c.answer != mnemonic_cnt and not c.blur))
      #  pos_to_blur = $.inArray(to_blur, to_quiz)
      #  to_quiz[pos_to_blur].blur = true
      #  $boxes[pos_to_blur].addClass('blur')
      if got_answer or round_time >= active_deck.round_time
        #  for $box in $boxes
        #  $box.removeClass('blur')
        #for c in to_quiz
        #  c.blur = false
        $('#quiz_answer').masonry('remove', $boxes[pos_to_remove]).masonry('reload')
        to_quiz.splice(pos_to_remove, 1)
        $boxes.splice(pos_to_remove, 1)
        mnemonic_cnt += 1
        active_deck.start_time = Math.floor(new Date().getTime() / 1000)
        $('#quiz_answer_input').val('')

      setTimeout(game_loop, 200)

    active_deck.start_time = Math.floor(new Date().getTime() / 1000)
    setTimeout(game_loop, 100)
          

    undefined
  hideQuizInput: ->
    view = new CardView({model: active_deck.selected_card})
    view.selectCard()
    undefined
  showLogin: ->
    $('#login_form').toggle()
    undefined
  leaveBoard: ->
    if !active_deck.selected_card && !active_deck.new_card
      # nothing is selected
      #$("#quiz_input").hide()
      $("#quiz_input").slideUp('slow')
    undefined
  clickDeck: ->
    app_router.navigate('/')
    undefined
  initialize: ->
    # Listen for change events active card list
    @listenTo(active_cards, 'add', @addOne)
    # Populate the featured deck list
    $.get('featured_decks', (data) ->
      json_data = $.parseJSON(data)
      # Create the list of featured
      # decks on the sidebar
      _.each(json_data, (f_data) ->
        template = _.template( $("#featured_template").html(), f_data )
        $('#featured').prepend(template)
      )
      $("#accordion").accordion({
        active: false,
        collapsible: true
      })
    )
    undefined
  addOne: (card) ->
    view = new CardView({model: card})
    $box = $(view.render().el)
    $container = @$('#container')
    $box.imagesLoaded( ()->
      $('#container').append( $box ).masonry('reload')
    )
    undefined
  addCard: (e) ->
    selected = active_deck.selected_card
    $('#update_card').get(0).reset()
    # clear the file input
    $('#front_img_preview').html('')
    if active_deck.selected_card
      # toggle the selected state of the previously
      # selected card
      active_deck.selected_card.toggle_selected()
    $('#quiz_input').show()
    active_deck.new_card = true
    undefined
  deleteCard: (e) ->
    form_data = new FormData()
    form_data.append('deck_id', active_deck.id)
    form_data.append('card_id', active_deck.selected_card.id)
    form_data.append('delete_card', true)
    $.ajax({
      url: 'update_card',  #server script to process data
      type: 'POST',
      success: (data) ->
        json_data = $.parseJSON(data)
        selected = active_deck.selected_card
        # deselect card
        view = new CardView({model: active_deck.selected_card})
        view.selectCard()
        # remove the card
        active_cards.remove(selected)
        $('#container').masonry('reload')
      error: (e) ->
        console.log('error')
      data: form_data,
      # Options to tell JQuery not to process data or worry about content-type
      cache: false,
      contentType: false,
      processData: false
    })
    undefined
  updateCard: (e) ->
    e.preventDefault() #This prevents the form from submitting normally
    console.log('saving card ')
    form_data = new FormData($('#update_card')[0])
    if active_deck.new_card
      form_data.append('card_id', 'new')
    else
      form_data.append('card_id', active_deck.selected_card.id)
    form_data.append('deck_id', active_deck.id)
    $.ajax({
      url: 'update_card',  #server script to process data
      type: 'POST',
      success: (data) ->
        json_data = $.parseJSON(data)
        params = {
          'id': json_data.id,
          'front_text': json_data.front_text,
        }
        if json_data.front_img != 'None'
          params.front_img = json_data.front_img
        if active_deck.new_card
          active_cards.add(params)
        else
          active_deck.selected_card.set(params)
        # after the image loads
        # re-arrange the masonry
        # board
        $('img.board_preview').load(()->
          $('#container').masonry('reload')
        )
        console.log('success')
        @
      error: (e) ->
        console.log('error')
        @
      data: form_data
      #Options to tell JQuery not to process data or worry about content-type
      cache: false
      contentType: false
      processData: false
    })
    false
  updateImgFront: (e) ->
    e.preventDefault() #This prevents the form from submitting normally
    @updateImgPreview(e, '#front_img_preview')
    undefined
  updateImgPreview: (e, selector) ->
    #Check File API support
    if window.File && window.FileList && window.FileReader
      files = e.target.files; #FileList object
      $.each(files, (i,file) ->
        #Only pics
        if !file.type.match('image')
          return
        picReader = new FileReader()
        picReader.addEventListener("load", (e) ->
          picFile = e.target
          $(selector).html("<img class='thumbnail_preview' src='" +
                           picFile.result + "'" +
                           "title='" + picFile.name + "'/>")
        )
        #Read the image
        picReader.readAsDataURL(file)
        @
      )
    else
      $(selector).html('No preview support for your browswer')
    undefined
# END class BoardView extends Backbone.View

app_router = new AppRouter()
active_cards = new CardList()
deck_view = new BoardView({ })
# always will be the currently selected deck
active_deck = new DeckModel({ })


user_card_data = {}

app_router.on('route:getDeck', (id) ->
  active_deck.url = 'deck/' + id
  active_deck.fetch({
    success: (model, response) ->
      active_cards.reset()
      # clear the board
      $('#container').html('')
      $('#container').show()
      # update the mnemonic
      $('#mnemonic').html(active_deck.toJSON().mnemonic.join(" "))
      $.each(response.cards, (i, card) ->
        active_cards.add(card)
        undefined
      )
      # enable or disable functions
      # depending whether the user
      # has write access to the deck
      if response.can_write == true
        console.log(response.can_write)
        $('#add_card').show()
        $('#quiz_input_submit').show()
        $('.icon_label').show()
      else
        $('#add_card').hide()
        $('#quiz_input_submit').hide()
        $('.icon_label').hide()
      console.log(active_deck.toJSON())
      undefined
    error: (model, response) ->
      console.log(
        'error: ' + JSON.stringify(model) + ' : ' + JSON.stringify(response))
      deck_view.model = model
      deck_view.showBoard()
      undefined
  })
  undefined
)
undefined

$(document).ready(() ->
  Backbone.history.start()
  # initialize the board

  $quiz_answer = $('#quiz_answer')
  $quiz_answer.masonry({
    itemSelector : '.box',
    columnWidth : 10,
    isAnimated: false
  })

  $container = $('#container')
  $container.masonry({
    itemSelector : '.box',
    columnWidth : 10,
    isAnimated: false
  })

  undefined
)
