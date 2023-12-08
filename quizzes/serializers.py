from rest_framework import serializers
from quizzes.models import Deck, Flashcard, UserVote


class DeckSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deck
        fields = '__all__'


class DeckDetailSerializer(serializers.ModelSerializer):
    flashcards_count = serializers.SerializerMethodField()
    total_votes = serializers.SerializerMethodField()
    flashcard_ids = serializers.SerializerMethodField()

    class Meta:
        model = Deck
        fields = ['id', 'owner', 'subject', 'name', 'description', 'flashcards_count', 'total_votes', 'flashcard_ids']

    def get_flashcards_count(self, deck):
        return deck.flashcard_set.count()

    def get_total_votes(self, deck):
        flashcards = deck.flashcard_set.all()
        total_votes = sum([flashcard.vote for flashcard in flashcards])
        return total_votes

    def get_flashcard_ids(self, deck):
        return list(deck.flashcard_set.values_list('id', flat=True))

class FlashcardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flashcard
        fields = '__all__'

class UserVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserVote
        fields = ['user', 'flashcard', 'vote_type']
