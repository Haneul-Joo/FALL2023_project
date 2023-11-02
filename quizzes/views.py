from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from .models import Deck, Flashcard
from .serializers import DeckSerializer, FlashcardSerializer
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from utils.messages import msg_success
from utils.permission import IsOwnerOrReadOnly
from rest_framework.generics import get_object_or_404


class DeckView(APIView, PageNumberPagination):
    """
    Deck 리스트 조회
    """
    def get(self, request):
        all_decks = Deck.objects.all()
        page = self.paginate_queryset(all_decks, request)
        serializer = DeckSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    """
    Deck 생성
    """
    def post(self, request):
        data = request.data.copy()
        data['owner'] = request.user.student_id
        serializer = DeckSerializer(data=data)
        if serializer.is_valid():
            serializer.save()  # owner field를 채운 새로운 모델 인스턴스 생성 및 저장
            return Response(serializer.data, status=HTTP_201_CREATED)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

class DeckDetailView(APIView, PageNumberPagination):
    permission_classes = [IsOwnerOrReadOnly]
    """
    Deck 상세 조회
    """
    def get(self, request, deck_id):
        # 존재하지 않은 deck_id를 검색한 경우, 404 반환
        deck = get_object_or_404(Deck, id=deck_id)
        serializer = DeckSerializer(deck)
        return Response(serializer.data)
    """
    Deck 수정
    """
    def put(self, request, deck_id):
        # 존재하지 않은 deck_id를 수정하려고 한 경우, 404 반환
        deck = get_object_or_404(Deck, id=deck_id)
        serializer = DeckSerializer(deck, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=HTTP_200_OK)
        else:
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    """
    Deck 삭제
    """
    def delete(self, request, deck_id):
        deck = get_object_or_404(Deck, id=deck_id)
        deck.delete()
        return Response("삭제 성공", status=HTTP_204_NO_CONTENT)


class FlashcardView(APIView, PageNumberPagination):
    """
    특정 Deck에 대한 Flashcard 리스트 조회
    """
    def get(self, request, deck_id):
        deck = get_object_or_404(Deck, id=deck_id)
        all_flashcards = deck.flashcard_set.all()
        page = self.paginate_queryset(all_flashcards, request)
        serializer = FlashcardSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    """
    특정 Deck에 대한 Flashcard 생성
    """
    def post(self, request, deck_id):
        data = request.data.copy()
        data['owner'] = request.user.student_id
        data['deck'] = deck_id
        serializer = FlashcardSerializer(data=data)
        if serializer.is_valid():
            serializer.save()  # owner field를 채운 새로운 모델 인스턴스 생성 및 저장
            return Response(serializer.data, status=HTTP_201_CREATED)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

class FlashcardDetailView(APIView, PageNumberPagination):
    permission_classes = [IsOwnerOrReadOnly]
    """
    Flashcard 상세 조회
    """
    def get(self, request, deck_id, flashcard_id):
        # 존재하지 않은 flashcard_id를 검색한 경우, 404 반환
        flashcard = get_object_or_404(Flashcard, id=flashcard_id)
        serializer = FlashcardSerializer(flashcard)
        return Response(serializer.data)
    """
    Flashcard 수정
    """
    def put(self, request, deck_id, flashcard_id):
        # 존재하지 않은 flashcard_id를 수정하려고 한 경우, 404 반환
        flashcard = get_object_or_404(Flashcard, id=flashcard_id)
        serializer = FlashcardSerializer(flashcard, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=HTTP_200_OK)
        else:
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    """
    Flashcard 삭제
    """
    def delete(self, request, deck_id, flashcard_id):
        flashcard = get_object_or_404(Flashcard, id=flashcard_id)
        flashcard.delete()
        return Response("삭제 성공", status=HTTP_204_NO_CONTENT)