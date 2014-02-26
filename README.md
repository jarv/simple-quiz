# Mnemonics

* colors - richard of york gains battles in vain
* roman numerals - I veer across but lucy can't drink milk
* two letter scrabble words -
* house of tudors
* wives of King Henry the VIII

# Quiz
[ Review ]
    - type the mnemonic with it displayed
    - type or click answer before the turn counter is up
[ Training ]
    - type the mnemonic with just the mnemonic
    - type answer to make card appear
[ Learning ]
    - type the full mnemonic without it displayed
    - type answer, no mnemonic
[ Learned ]

## DeckStates
* training - [T]
* review - [R]
* learning - [L]
* learned - [checkmark]

## DeckCounters
* num\_traning
* num\_review
* num\_learning
* num\_lapses

## CardStates
* training - [T]
* review - [R]
* learning - [L]
* learned - [checkmark]

## CardCounters
* num\_review
* num\_training
* num\_learning
* num\_lapses


## Models

* DeckModel
* CardModel

## Views

* CardView  `<div class="box" />`
* BoardView `<div id="deck_view" />`
* QuizView `<div id="quiz">`

## Collections

* CardList

## Router

* AppRouter

## Globals

* `app_router` - AppRouter
* `active_cards` - CardList
* `deck_view` - BoardView 
* `active_deck` - DeckModel (activ on the board)
