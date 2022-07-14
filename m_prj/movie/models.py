from django.db import models
from django.contrib.auth.models import AbstractUser
from .validators import validate_no_special_characters
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation


class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/tag/{self.slug}'


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=200,unique=True, allow_unicode=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/category/{self.slug}'

    class Meta:
        verbose_name_plural = 'Categories'


class User(AbstractUser):
    nickname = models.CharField(
        max_length=15, 
        unique=True, 
        null=True,
        validators=[validate_no_special_characters],
        error_messages={'unique':'이미 사용중인 닉네임입니다.'},
    )

    profile_pic = models.ImageField(default="default_profile_pic.jpg",upload_to="profile_pics")
    intro = models.CharField(max_length=60,blank=True)

    def __str__(self):
        return self.email


class Review(models.Model):
    title = models.CharField(max_length=30)
    movie_name = models.CharField(max_length=20)

    RATIMG_CHOICES = [
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
        (6, 6),
        (7, 7),
        (8, 8),
        (9, 9),
        (10, 10)
    ]

    rating = models.IntegerField(choices=RATIMG_CHOICES,default=None)

    image1 = models.ImageField(upload_to = "review_pics")
    image2 = models.ImageField(upload_to = "review_pics",blank=True)
    image3 = models.ImageField(upload_to = "review_pics",blank=True)
    content = models.TextField()
    dt_created = models.DateTimeField(auto_now_add = True)
    dt_updated = models.DateTimeField(auto_now_add = True)

    author = models.ForeignKey(User,on_delete=models.CASCADE)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)
    tags = models.ManyToManyField(Tag, blank=True)
    likes = GenericRelation('Like', related_query_name='review')

    def __str__(self):
        return self.title

class Like(models.Model):
    dt_created = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)

    object_id = models.PositiveIntegerField()

    liked_object = GenericForeignKey()

    def __str__(self):
        return f"({self.user}, {self.liked_object})"

class Comment(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE,related_name='comments')
    content = models.TextField()
    dt_created = models.DateTimeField(auto_now_add=True)
    dt_updated = models.DateTimeField(auto_now=True)
    likes = GenericRelation('Like',related_query_name='comment')

    def __str__(self):
        return f'{self.author} ::: {self.pk}'

    class Meta:
        ordering = ['-dt_created']
    # def get_absolute_url(self):
    #     return f'{self.review.get_absolute_url()}#comment-{self.review_id}'


