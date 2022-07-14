from django.shortcuts import render, get_object_or_404, redirect

from django.urls import reverse
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, View
)
from django.contrib.contenttypes.models import ContentType

from braces.views import LoginRequiredMixin, UserPassesTestMixin
from allauth.account.views import PasswordChangeView
from movie.models import Review, User, Category, Tag, Comment, Like
from movie.forms import ReviewForm, ProfileForm, CommentForm
from django.db.models import Q
from .mixins import LoginAndVerificationRequiredMixin, LoginAndOwnershipRequiredMixin


# Create your views here.


class IndexView(ListView):
    model = Review
    template_name = "movie/index.html"
    context_object_name = "reviews"
    paginate_by = 4
    ordering = ["-dt_created"]

    def get_context_data(self,**kwargs):
        context = super(IndexView, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_count'] = Review.objects.filter(category=None).count()
        return context


class ReviewDetailView(DetailView):
    model = Review
    template_name = 'movie/review_detail.html'
    pk_url_kwarg = 'review_id'

    def get_context_data(self, **kwargs):
        context = super(ReviewDetailView, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_count'] = Review.objects.filter(category=None).count()
        context['form'] = CommentForm()
        context['review_ctype_id'] = ContentType.objects.get(model='review').id
        context['comment_ctype_id'] = ContentType.objects.get(model='comment').id

        user=self.request.user
        if user.is_authenticated:
            review = self.object
            context['likes_review'] = Like.objects.filter(user=user, review=review).exists()
            context['liked_comments'] = Comment.objects.filter(review=review).filter(likes__user=user)

        return context


class ReviewCreateView(LoginAndVerificationRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = 'movie/review_form.html'


    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("review-detail", kwargs={"review_id": self.object.id})




class ReviewUpdateView(LoginAndOwnershipRequiredMixin, UpdateView):
    model = Review
    form_class = ReviewForm
    template_name = 'movie/review_form.html'
    pk_url_kwarg = 'review_id'

    def get_success_url(self):
        return reverse("review-detail", kwargs={"review_id": self.object.id})


class ReviewDeleteView(LoginAndOwnershipRequiredMixin, DeleteView):
    model = Review
    template_name = 'movie/review_confirm_delete.html'
    pk_url_kwarg = 'review_id'

    def get_success_url(self):
        return reverse('index')


class ProcessLikeView(LoginAndVerificationRequiredMixin, View):
    http_method_names = ['post']

    def post(self, request, *args,**kwargs):
        like, created = Like.objects.get_or_create(
            user = self.request.user,
            content_type_id=self.kwargs.get('content_type_id'),
            object_id=self.kwargs.get('object_id'),
        )

        if not created:
            like.delete()

        return redirect(self.request.META['HTTP_REFERER'])



class ProfileView(DetailView):
    model = User
    template_name = 'movie/profile.html'
    pk_url_kwarg = 'user_id'
    context_object_name = 'profile_user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.kwargs.get('user_id')
        context['user_reviews'] = Review.objects.filter(author__id=user_id).order_by('-dt_created')[:4]
        return context


class UserReviewListView(ListView):
    model = Review
    template_name = 'movie/user_review_list.html'
    context_object_name = 'user_reviews'
    paginate_by = 4

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        return Review.objects.filter(author__id=user_id).order_by('dt_created')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile_user'] = get_object_or_404(User, id=self.kwargs.get('user_id'))
        return context


class ProfileSetView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileForm
    template_name = 'movie/profile_set_form.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse('index')


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileForm
    template_name = 'movie/profile_update_form.html'


    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse('profile', kwargs=({'user_id': self.request.user.id}))


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    def get_success_url(self):
        return reverse('profile', kwargs=({'user_id': self.request.user.id}))


def categories_page(request, slug):
    if slug == 'no-category' : # 미분류일때
        category = '미분류'
        review_list = Review.objects.filter(category=None)
    else:
        category = Category.objects.get(slug=slug)
        review_list = Review.objects.filter(category=category)
    context = {
        'review_list': review_list,
        'categories' : Category.objects.all(),
        'no_category_count' : Review.objects.filter(category=None).count(),
        'category' : category,

    }
    return render(request, 'movie/index.html', context)


def tag_page(request, slug):

    tag = Tag.objects.get(slug=slug)
    review_list = tag.review_set.all()
    context = {
        'categories' : Category.objects.all(),
        'no_category_count' : Review.objects.filter(category=None).count(),
        'tag': tag,
        'review_list': review_list
    }
    return render(request, 'movie/index.html', context)

class CommentCreateView(LoginAndVerificationRequiredMixin, CreateView):
    http_method_names = ['post']

    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.review = Review.objects.get(id=self.kwargs.get('review_id'))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('review-detail', kwargs={'review_id':self.kwargs.get('review_id')})

class CommentUpdateView(LoginAndOwnershipRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'movie/comment_update_form.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse('review-detail', kwargs={'review_id': self.object.review.id})


class CommentDeleteView(LoginAndOwnershipRequiredMixin, DeleteView):
    model = Comment
    template_name = 'movie/comment_confirm_delete.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse('review-detail', kwargs={'review_id': self.object.review.id})



def comment_delete(request, review_id, comment_pk):
    if request.user.is_authenticated:
        comment = get_object_or_404(Comment, pk=comment_pk)
        if request.user == comment.author:
            comment.delete()
    return redirect('review-detail', review_id)


def search(request):
    if request.method == "GET":
        searchKey = request.GET['q']

        search_review = Review.objects.filter(Q(movie_name__icontains=searchKey))

        return render(request, 'movie/search.html', {'search_review': search_review})

    else:
        return render(request, 'movie/index.html')

