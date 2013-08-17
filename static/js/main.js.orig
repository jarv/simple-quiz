$(function(){
  var renders = 0;
  var adds = 0;
  var addAlls = 0;
  var DeckModel = Backbone.Model.extend({
    defaults: function() {
      return {
        new_card: false
      };
    }
  });
  var CardModel = Backbone.Model.extend({
    urlRoot: '/card',
    defaults: function() {
      return {
        is_selected: false,
        selected_card: null,
        accordion_state: null
      };
    },
    toggle_selected: function() {
      this.set({'is_selected': !this.get('is_selected')});
    }
  });

  var CardList = Backbone.Collection.extend({
    model: CardModel,
    // Filter down the list of cards that are selected
    selected: function() {
      return this.where({is_selected: true});
    }
    
  });

  var AppRouter = Backbone.Router.extend({
    routes: {
      "deck/:id": "getDeck",
      "*actions": "defaultRoute"
    }
  });

  // view that displays a card on the board
  var CardView = Backbone.View.extend({

    tagName: 'div',  // default

    attributes : function () {
        return {
          'class' : 'box'
        };
    },

    events:{
      'click': 'selectCard',
      'mouseenter': 'displayCard',
      'mouseleave': 'hideCard'
    },

    initialize: function() {

      // Set up event listeners. The 'change' backbone
      // event is raised when a property changes
      this.listenTo(this.model, 'change', this.render);
      this.listenTo(this.model, 'remove', this.remove);
    },
    clear: function() {
      this.model.destroy();
    },
    render: function() {
      renders += 1;
      var variables = { 
        front_text: this.model.get('front_text'),
        back_text: this.model.get('back_text'),
        front_img: '',
        back_img: ''
      };
      if (this.model.get('front_img')) {
        var thumb_front = this.model.get('front_img') + '/thumb';
        var full_front = this.model.get('front_img');
        this.model.set({'front_img_thumb': '<img class="board_preview" src="' + thumb_front + '"/>'});
        this.model.set({'front_img_full': '<img class="board_preview" src="' + full_front + '"/>'});
        variables.front_img = this.model.get('front_img_thumb');
      } 
      if (this.model.get('back_img')) {
        var thumb_back = this.model.get('back_img') + '/thumb';
        var full_back = this.model.get('back_img');
        this.model.set({'back_img_thumb': '<img class="board_preview" src="' + thumb_back + '"/>'});
        this.model.set({'back_img_full': '<img class="board_preview" src="' + full_back + '"/>'});
        variables.back_img = this.model.get('back_img_thumb');
      } 
      var template = _.template( $("#box_template").html(), variables );
      // Load the compiled HTML into the Backbone "el"
      this.$el.html( template );
      return this;
    },
    renderCard: function(variables) {
      var template = _.template( $("#box_template").html(), variables );
      // Load the compiled HTML into the Backbone "el"
      this.$el.html( template );
      return this;
    },
    hideCard: function() {
    },

    displayCard: function() {
      console.log('this-> ');
      console.log(this.model);
      console.log('last -> ');
      console.log(active_deck.last_selected);
      if (this.model == active_deck.last_selected) {
        return;
      }
      if (! active_deck.selected_card && ! active_deck.new_card) {
        // nothing is selected
        $('#front_img_preview').html('');
        $('#back_img_preview').html('');
        $('#front_img_preview').html(this.model.get('front_img_full'));
        $('#back_img_preview').html(this.model.get('back_img_full'));
        $('#front_input').val(this.model.get('front_text'));
        $('#back_input').val(this.model.get('back_text'));
        if (! $('#quiz_input').is(":visible")) {
          // animate/show if the element is hidden
          $("#quiz_input").slideDown('slow');
        }
      }

    }, 
    selectCard: function() {

      active_deck.new_card = false;
      var clicked_model = this.model;
      // save the last card selected so that it isn't
      // shown immediately due to hover
      active_deck.last_selected = active_deck.selected_card;
      if (active_deck.selected_card && active_deck.selected_card != clicked_model) {
        // toggle the selected state of the previously
        // selected card
        active_deck.selected_card.toggle_selected();
      }
      clicked_model.toggle_selected();
      if (clicked_model.get('is_selected')) {
        active_deck.selected_card = clicked_model;
        $('.box').removeClass('select');
        $(this.el).addClass('select');
        $('#front_img_preview').html('');
        $('#back_img_preview').html('');
        $('#front_img_preview').html(clicked_model.get('front_img_full'));
        $('#back_img_preview').html(clicked_model.get('back_img_full'));
        $('#front_input').val(clicked_model.get('front_text'));
        $('#back_input').val(clicked_model.get('back_text'));
        $('#quiz_input').show();
      } else {
        active_deck.selected_card = null;
        $(this.el).removeClass('select');
        $('#quiz_input').hide();
      }
    }

  });


  var QuizView = Backbon.View.extend({
    el: $('#quiz_view'),

  });
  // game board
  var BoardView = Backbone.View.extend({

    el: $('#deck_view'),
    events:{
      'click #hide_quiz_input': 'hideQuizInput',
      'click #login_link': 'showLogin',
      'click #submit_card': 'updateCard',
      'click #delete_card': 'deleteCard',
      'click #click_add_card': 'addCard',
      'click #click_select_deck': 'clickDeck',
      'change #front_img': 'updateImgFront',
      'change #back_img': 'updateImgBack',
      'mouseenter #content': 'enterBoard',
      'mouseleave #content': 'leaveBoard'
    },
    hideQuizInput: function() {
      var view = new CardView({model: active_deck.selected_card});
      view.selectCard();
    },
    showLogin: function() {
      $('#login_form').toggle(); 
    },
    enterBoard: function() {
      if (! active_deck.selected_card && active_deck.accordion_state === null) {
        // no card is selected and there isn't a saved state
        // active_deck.accordion_state  = $("#accordion").accordion( "option", "active" );
        // $('#accordion').accordion("option", "active", false);
      }
    },
    leaveBoard: function() {

      if (! active_deck.selected_card && ! active_deck.new_card) {
        // nothing is selected
        //$("#quiz_input").hide();
        $("#quiz_input").slideUp('slow');
      }

    },
    clickDeck: function() {
      app_router.navigate('/');
    },

    initialize: function(){

      // Listen for change events active card list
      this.listenTo(active_cards, 'add', this.addOne);
      //this.listenTo(active_cards, 'remove', this.removeOne);


      // Populate the featured deck list
      $.get('featured_decks', function(data) {
        json_data = $.parseJSON(data);
        _.each(json_data, function(f_data) {
          var template = _.template( $("#featured_template").html(), f_data );
          $('#featured').prepend(template);
        });
        $("#accordion").accordion({
          active: false,
          collapsible: true
        });
      });
    },
   
    removeOne: function(card) {
      //card.destroy();
    },

    addOne: function(card) {
      var view = new CardView({model: card});
      var $box = $(view.render().el);
      var $container = this.$('#container');
      $box.imagesLoaded( function() {
        $('#container').prepend( $box ).masonry('reload');
      });
    },

    addAll: function() {
    },

    addCard: function(e) {
      var selected = active_deck.selected_card;
      $('#update_card').get(0).reset();
      // clear the file input
      $('#front_img_preview').html('');
      $('#back_img_preview').html('');
      if (active_deck.selected_card) {
        // toggle the selected state of the previously
        // selected card
        active_deck.selected_card.toggle_selected();
      }
      $('#quiz_input').show();
      active_deck.new_card = true;
    },

    deleteCard: function(e){
      var form_data = new FormData();    
      form_data.append('deck_id', active_deck.id);
      form_data.append('card_id', active_deck.selected_card.id);
      form_data.append('delete_card', true);
      $.ajax({
        url: 'update_card',  //server script to process data
        type: 'POST',
        success: function(data) {
          json_data = $.parseJSON(data);
          var selected = active_deck.selected_card;
          // deselect card
          var view = new CardView({model: active_deck.selected_card});
          view.selectCard();
          // remove the card
          active_cards.remove(selected);
          $('#container').masonry('reload');
        },
        error: function(e) {
          console.log('error');
        },
        data: form_data,
        //Options to tell JQuery not to process data or worry about content-type
        cache: false,
        contentType: false,
        processData: false
      });
    },
    updateCard: function(e){
      e.preventDefault(); //This prevents the form from submitting normally
      console.log('saving card ');
      var form_data = new FormData($('#update_card')[0]);
      if (active_deck.new_card) {
        form_data.append('card_id', 'new');
      } else {
        form_data.append('card_id', active_deck.selected_card.id);
      }
      form_data.append('deck_id', active_deck.id);
      $.ajax({
        url: 'update_card',  //server script to process data
        type: 'POST',
        success: function(data) {
          json_data = $.parseJSON(data);
          var params = {
            'id': json_data.id,
            'front_text': json_data.front_text,
            'back_text': json_data.back_text
          };
          if (json_data.front_img != 'None') {
            params.front_img = json_data.front_img;
          }
          if (json_data.back_img != 'None') {
            params.back_img = json_data.back_img;
          }
          if (active_deck.new_card) {
            active_cards.add(params);
          } else {
            active_deck.selected_card.set(params);
          }
          // after the image loads 
          // re-arrange the masonry
          // board
          $('img.board_preview').load(function() {
            $('#container').masonry('reload');
          });
          console.log('success');
        },
        error: function(e) {
          console.log('error');
        },
        data: form_data,
        //Options to tell JQuery not to process data or worry about content-type
        cache: false,
        contentType: false,
        processData: false
      });
      return false;

    },

    updateImgFront: function(e) {
      e.preventDefault(); //This prevents the form from submitting normally
      this.updateImgPreview(e, '#front_img_preview');
    },
    updateImgBack: function(e) {
      e.preventDefault(); //This prevents the form from submitting normally
      this.updateImgPreview(e, '#back_img_preview');
    },

    updateImgPreview: function(e, selector) {
      //Check File API support
      if(window.File && window.FileList && window.FileReader) {
          var files = e.target.files; //FileList object
          $.each(files, function (i,file) {
            //Only pics
            if(!file.type.match('image')) {
              return;
            }
            var picReader = new FileReader();
            picReader.addEventListener("load",function(e){
                var picFile = e.target;
                $(selector).html("<img class='thumbnail_preview' src='" + 
                                 picFile.result + "'" +
                                 "title='" + picFile.name + "'/>");
            });
            //Read the image
            picReader.readAsDataURL(file);
          });
      } else {
        $(selector).html('No preview support for your browswer');
      }
    }
  });



  var app_router = new AppRouter();
  var active_cards = new CardList();
  var deck_view = new BoardView({ });
  // always will be the currently selected deck
  var active_deck = new DeckModel({});


  app_router.on('route:getDeck', function(id) {
    active_deck.url = 'deck/' + id;
    active_deck.fetch({
      success: function(model, response) {
        active_cards.reset();
        // clear the board
        $('#container').html('');
        $.each(response.cards, function(i, card) {
            active_cards.add(card);
        });

        // enable or disable functions
        // depending whether the user 
        // has write access to the deck
        if (response.can_write === true) {
          console.log(response.can_write);
          $('#add_card').show();
          $('#quiz_input_submit').show();
          $('.icon_label').show();
        } else {
          $('#add_card').hide();
          $('#quiz_input_submit').hide();
          $('.icon_label').hide();
        }
      },
      error: function(model, response) {
        console.log('error: ' + JSON.stringify(model) + ' : ' + JSON.stringify(response));
        deck_view.model = model;
        deck_view.showBoard();
      }
    });
  });

});

$(document).ready(function() {

  Backbone.history.start();

  // initialize the board
  var $container = $('#container');
  $container.imagesLoaded(function(){
    $container.masonry({
      itemSelector : '.box',
      columnWidth : 10,
      isAnimated: false
    });
  });
});
