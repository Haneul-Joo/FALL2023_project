from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from .models import Deck, Flashcard, UserVote
from .serializers import DeckSerializer, DeckDetailSerializer, FlashcardSerializer, UserVoteSerializer
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from utils.permission import IsOwnerOrReadOnly
from rest_framework.generics import get_object_or_404


class DeckView(APIView, PageNumberPagination):
    """
    Deck 리스트 조회
    """
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    serializer_class = DeckSerializer

    def get(self, request):
        all_decks = Deck.objects.all()
        filter_by = request.GET.get('filter', '')
        query = request.GET.get('query', '')
        if filter_by == 'subject':
            all_decks = all_decks.filter(subject__icontains=query)
        elif filter_by == 'owner':
            all_decks = all_decks.filter(owner=query)
        else:
            all_decks = Deck.objects.all()

        all_decks = all_decks.order_by('-id')
        page = self.paginate_queryset(all_decks, request)

        if page is not None:
            serializer = self.get_paginated_response(DeckSerializer(page, many=True).data)
        else:
            serializer = DeckSerializer(all_decks, many=True)
        return Response(serializer.data, template_name='quizzes.html', status=HTTP_200_OK)

    """
    Deck 생성
    """
    def post(self, request):
        self.renderer_classes = [JSONRenderer]  # post 메서드에서만 TemplateHTMLRenderer 없이 사용
        data = request.data.copy()
        data['owner'] = request.user.student_id
        serializer = DeckSerializer(data=data)
        if serializer.is_valid():
            serializer.save()  # owner field를 채운 새로운 모델 인스턴스 생성 및 저장
            return Response(serializer.data, status=HTTP_201_CREATED)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class DeckDetailView(APIView, PageNumberPagination):
    permission_classes = [IsOwnerOrReadOnly]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    """
    Deck 상세 조회
    """
    def get(self, request, deck_id):
        # 존재하지 않은 deck_id를 검색한 경우, 404 반환
        deck = get_object_or_404(Deck, id=deck_id)
        serializer = DeckDetailSerializer(deck)
        return Response(serializer.data, template_name='quiz_detail.html')

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
        try:
            deck = get_object_or_404(Deck, id=deck_id)
            deck.delete()
            return JsonResponse({'message': 'Deck deleted successfully'})
        except Exception as e:
            # 디버깅을 위해 예외를 로그에 기록
            print(f"An error occurred: {str(e)}")

            # 적절한 오류 응답을 반환
            return JsonResponse({'error': 'Internal Server Error'}, status=500)



class FlashcardView(APIView, PageNumberPagination):
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    """
    특정 Deck에 대한 Flashcard 리스트 조회
    """
    def get(self, request, deck_id):
        deck = get_object_or_404(Deck, id=deck_id)
        all_flashcards = deck.flashcard_set.all()
        page = self.paginate_queryset(all_flashcards, request)
        if page is not None:
            serializer = self.get_paginated_response(FlashcardSerializer(page, many=True).data)
        else:
            serializer = FlashcardSerializer(page, many=True)
        return Response({"data": serializer.data,
                         "owner": request.user.student_id,
                         "deck_id": deck_id},
                        status=HTTP_200_OK,
                        template_name='cards.html')
    """
    특정 Deck에 대한 Flashcard 생성
    """
    def post(self, request, deck_id):
        self.renderer_classes = [JSONRenderer]  # post 메서드에서만 TemplateHTMLRenderer 없이 사용
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
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    """ Flashcard 상세 조회"""
    def get(self, request, deck_id, flashcard_id):
        # 존재하지 않은 flashcard_id를 검색한 경우, 404 반환
        deck = get_object_or_404(Deck, id=deck_id)
        flashcard = get_object_or_404(Flashcard, id=flashcard_id)
        serializer = FlashcardSerializer(flashcard)

        return Response({'deck': DeckSerializer(deck).data,
                         'flashcard': serializer.data,
                         },
                        template_name='card_detail.html'
                        )
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


class FlashcardAttemptView(APIView, PageNumberPagination):
    permission_classes = [IsOwnerOrReadOnly]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    """
    Flashcard 문제 풀이
    """
    def get(self, request, deck_id, flashcard_id):
        # 존재하지 않은 flashcard_id를 검색한 경우, 404 반환
        deck = get_object_or_404(Deck, id=deck_id)
        flashcard = get_object_or_404(Flashcard, id=flashcard_id)
        serializer = FlashcardSerializer(flashcard)

        next_flashcard = self.get_next_flashcard(deck, flashcard_id)
        return Response({'deck': DeckSerializer(deck).data,
                         'flashcard': serializer.data,
                        'next_flashcard': next_flashcard
                         },
                        template_name='attempt_quiz.html'
                        )
    """
    다음 Flashcard 상세 조회
    """
    def get_next_flashcard(self, deck, current_flashcard_id):
        current_deck = DeckDetailSerializer(deck).data
        flashcard_ids = current_deck.get('flashcard_ids', [])

        # flashcard_ids가 비어 있거나 current_flashcard_id가 flashcard_ids에 없는 경우
        if not flashcard_ids or current_flashcard_id not in flashcard_ids:
            return None

        # 현재 flashcard_id의 인덱스를 찾아서 다음 flashcard_id를 가져옵니다.
        current_index = flashcard_ids.index(current_flashcard_id)

        # 다음 flashcard_id가 flashcard_ids 범위 내에 있는지 확인합니다.
        if current_index + 1 < len(flashcard_ids):
            next_flashcard_id = flashcard_ids[current_index + 1]
            next_flashcard = Flashcard.objects.filter(id=next_flashcard_id).first()
            return FlashcardSerializer(next_flashcard).data

        return None

"""
flashcard 추천 기능
"""
class VoteFlashcardView(APIView):
    renderer_classes = [JSONRenderer]

    def post(self, request, deck_id, flashcard_id):
        flashcard = get_object_or_404(Flashcard, id=flashcard_id)

        # 사용자가 이미 해당 Flashcard에 투표한 경우
        if UserVote.objects.filter(user=request.user, flashcard=flashcard).exists():
            return Response({'error': 'You have already voted for this Flashcard.'}, status=HTTP_400_BAD_REQUEST)

        # 사용자가 투표한 기록 저장
        user_vote = UserVote(user=request.user, flashcard=flashcard, vote_type=request.data.get('vote_type'))
        user_vote.save()

        # 투표 처리 및 결과 반환
        if request.data.get('vote_type') == 'up':
            flashcard.vote += 1
        elif request.data.get('vote_type') == 'down':
            flashcard.vote -= 1
        flashcard.save()

        return Response({'success': True, 'new_vote_count': flashcard.vote}, status=HTTP_200_OK)


class UserVotedFlashcardsView(APIView):
    def get(self, request):
        # 현재 사용자가 추천한 Flashcard 목록을 가져오기
        user_votes = UserVote.objects.filter(user=request.user)
        serializer = UserVoteSerializer(user_votes, many=True)
        return Response(serializer.data)
