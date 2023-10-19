from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from .models import Deck
from .serializers import DeckSerializer
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
        data = request.data
        data['owner'] = request.user.student_id
        serializer = DeckSerializer(data=data)
        if serializer.is_valid():
            serializer.save() # owner field를 채운 새로운 모델 인스턴스 생성 및 저장
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



