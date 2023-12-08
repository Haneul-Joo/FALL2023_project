from django.urls import path, include
from utils.rendering import *
from quizzes.views import (DeckView, DeckDetailView, FlashcardView, FlashcardDetailView, UserVotedFlashcardsView, VoteFlashcardView)
urlpatterns = [
    path('', DeckView.as_view(), name='deck-list'),
    path('myvotes', UserVotedFlashcardsView.as_view(), name='voted-list'),
    path('<int:deck_id>/', DeckDetailView.as_view(), name='deck-detail'),
    path('<int:deck_id>/delete/', DeckDetailView.as_view(), name='deck-delete'), #삭제하기 url
    path('<int:deck_id>/cards/', FlashcardView.as_view(), name='card-list'),
    path('<int:deck_id>/cards/<int:flashcard_id>', FlashcardDetailView.as_view(), name='card-detail'),
    path('<int:deck_id>/cards/<int:flashcard_id>/vote/', VoteFlashcardView.as_view(), name='vote_flashcard'),
]