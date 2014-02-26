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
      card_state: @model.get('card_state')
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

  CardStates:
    review: 'review'
    training: 'training'
    learning: 'learning'
    learned: 'learned'

  DeckStates:
    mnemonic: 'mnemonic'
    review: 'review'
    training: 'training'
    learning: 'learning'
    learned: 'learned'


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
    $('#quiz').show()
    mnemonic = active_deck.toJSON().mnemonic
    deck_state = active_deck.toJSON().deck_state
    mnemonic_pos = 0
    to_quiz = active_deck.toJSON().cards
    answers = (card for card in to_quiz)
    # shuffle the cards to quiz
    to_quiz = _.shuffle(to_quiz)
    got_mnemonic = false
    mnemonic_timed_out = false
    $('#quiz_answer_input').focus()

    for c in to_quiz
      if c.front_img
        # cache the images
        $("<img />").attr("src", c.front_img)
        $("<img />").attr("src", c.front_img + '/thumb')
      # Create an array of boxes for masonry
      c.$box = $(_.template( $("#quiz_answer_template").html(), c))

    switch deck_state
      when "review"
        # show the mnemonic
        $('#quiz_mnemonic').html(active_deck.toJSON().mnemonic.join(' '))
    

    start_time = Math.floor(new Date().getTime() / 1000)

    game_loop = () ->
      cur_time = Math.floor(new Date().getTime() / 1000)
      turn_time = cur_time - start_time
      switch deck_state
        when "review"
          if not got_mnemonic or mnemonic_timed_out
            check_string = $('#quiz_answer_input').val().toLowerCase().replace(/[^\w]/g, '')
            answer_string = mnemonic.join("").toLowerCase().replace(/[^\w]/g, '')
            if answer_string == check_string
              got_mnemonic = true
            if turn_time >= active_deck.toJSON().mnemonic_time
              start_time = Math.floor(new Date().getTime() / 1000)
              mnemonic_timed_out = true
            if got_mnemonic or mnemonic_timed_out
              $('#quiz_answer_input').val('')
              for c in to_quiz
                $('#quiz_answer').append(c.$box).masonry('reload')
          else
            got_answer = false

            check_string = $('#quiz_answer_input').val().toLowerCase().replace(/[^\w]/g, '')
            answer_string = answers[mnemonic_pos].front_text.toLowerCase().replace(/[^\w]/g, '')
            if answer_string == check_string
              got_answer = answers.shift()
            if got_answer or turn_time >= active_deck.toJSON().turn_time
              for c in to_quiz
                $('#quiz_answer').masonry('remove', c.$box)
              to_quiz = _.shuffle(to_quiz)
              for c in to_quiz
                $('#quiz_answer').append(c.$box).masonry('reload')
              start_time = Math.floor(new Date().getTime() / 1000)
              $('#quiz_answer_input').val('')
              got_answer = false

      setTimeout(game_loop, 200)
    setTimeout(game_loop, 200)
          

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
