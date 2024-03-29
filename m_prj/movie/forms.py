from django import forms
from .models import User, Review, Comment


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = [
            "title",
            "movie_name",
            "rating",
            "category",
            "tags",
            "image1",
            "image2",
            "image3",
            "content",
        ]
        widgets = {
            "rating": forms.Select,
            "category":forms.Select,
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'nickname',
            'profile_pic',
            'intro',
        ]
        widgets = {
            'intro': forms.Textarea,
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = [
            'content',
        ]
        widgets = {
            'content':forms.Textarea,
        }