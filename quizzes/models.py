from django.db import models
from accounts.models import NewUserInfo


class Deck(models.Model):
    owner = models.ForeignKey(NewUserInfo, on_delete=models.CASCADE)
    subject = models.CharField(max_length=50)
    name = models.CharField(max_length=80)
    description = models.TextField(default='')

    def __str__(self):
        return self.name

    class Meta:
        db_table = "deck"


class Flashcard(models.Model):
    owner = models.ForeignKey(NewUserInfo, on_delete=models.CASCADE)
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE)
    question = models.TextField()
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified_at = models.DateTimeField(auto_now=True)
    vote = models.SmallIntegerField(default=0)
    visible = models.BooleanField(default=True)

    def __str__(self):
        return self.question

    class Meta:
        db_table = "flashcard"
        ordering = ['id']


class UserVote(models.Model):
    user = models.ForeignKey(NewUserInfo, on_delete=models.CASCADE)
    flashcard = models.ForeignKey(Flashcard, on_delete=models.CASCADE)
    vote_type = models.CharField(max_length=4)  # 'up' 또는 'down'

    class Meta:
        # 중복 투표 방지
        constraints = [
            models.UniqueConstraint(fields=['user', 'flashcard'], name='unique_user_flashcard_vote')
        ]
