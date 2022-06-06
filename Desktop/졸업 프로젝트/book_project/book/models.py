from django.utils import timezone
from distutils.command.upload import upload
from email.policy import default
from tkinter import CASCADE
from django.db import models
from django.contrib.auth.models import AbstractUser
from .validators import validate_no_special_characters

# Create your models here.

class User(AbstractUser):
    nickname = models.CharField(
        max_length=15,
        unique=True,
        null=True,
        error_messages={'unique':'이미 사용중인 닉넥임입니다'},
        verbose_name="별명",
    )

    email = models.CharField(max_length = 128, verbose_name="이메일")
    password = models.CharField(max_length = 65, verbose_name = "비밀번호")
    profile_pic = models.ImageField(default="default_profile_pic.jpg",upload_to="profile_pics")
    intro = models.CharField(max_length=60,blank=True)


    def __str__(self):
        return self.username

    

class Book(models.Model):
    book_isbn = models.CharField(max_length=200)
    book_img_url = models.URLField()
    book_title = models.CharField(max_length=255)
    book_author = models.CharField(max_length=100)
    book_publisher = models.CharField(max_length=100)
    genre_name = models.CharField(max_length=50)

    class Meta:
        db_table = 'bookList.csv'
    
class Review(models.Model):
    author = models.ForeignKey(User,null=True,on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    book = models.ForeignKey(Book,on_delete=models.CASCADE)
    review_context = models.TextField()
    dt_created = models.DateTimeField(default=timezone.now)
    dt_updated = models.DateTimeField(auto_now=True)
    RATIMG_CHOICES = (
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
    )
    rating = models.IntegerField(choices=RATIMG_CHOICES,default=None)
   
    def __str__(self):
        return self.title

    
    
class Tag(models.Model):
    tag_name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=20,allow_unicode=True)

    def __str__(self):
        return self.tag_name
    
    def get_absolute_url(self):
        return f'/tag/{self.slug}'
