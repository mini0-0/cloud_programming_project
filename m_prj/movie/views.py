from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView,
)
from braces.views import LoginRequiredMixin, UserPassesTestMixin
from allauth.account.models import EmailAddress
from allauth.account.views import PasswordChangeView
from movie.models import Review, User, Category, Tag, Comment
from movie.forms import ReviewForm, ProfileForm, CommentForm
from movie.functions import confirmation_required_redirect
from django.db.models import Q

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
        context['comment_form'] = CommentForm
        return context


class ReviewCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = 'movie/review_form.html'

    redirect_unauthenticated_users = True
    raise_exception = confirmation_required_redirect

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("review-detail", kwargs={"review_id": self.object.id})

    def test_func(self, user):
        return EmailAddress.objects.filter(user=user, verified=True).exists()


class ReviewUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Review
    form_class = ReviewForm
    template_name = 'movie/review_form.html'
    pk_url_kwarg = 'review_id'

    raise_exception = True
    redirect_unauthenticated_users = False

    def get_success_url(self):
        return reverse("review-detail", kwargs={"review_id": self.object.id})

    def test_func(self, user):
        review = self.get_object()
        if review.author == user:
            return True
        else:
            return False




class ReviewDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Review
    template_name = 'movie/review_confirm_delete.html'
    pk_url_kwarg = 'review_id'

    raise_exception = True
    redirect_unauthenticated_users = False

    def get_success_url(self):
        return reverse('index')

    def test_func(self, user):
        review = self.get_object()
        if review.author == user:
            return True
        else:
            return False


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


def new_comment(request, review_id):

    if request.user.is_authenticated:
        review = get_object_or_404(Review, pk=review_id)

        if request.method == "POST":
            comment_form = CommentForm(request.POST)
            comment = comment_form.save(commit=False)
            comment.author = request.user
            comment.review = review
            comment.save()
            return redirect('review-detail',review_id=review_id)
        else:
            return redirect(review.get_absolute_url())
    else:
        return redirect('account_login')


def comment_update(request,review_id,comment_pk):

    review = get_object_or_404(Review, pk=review_id)
    comment = get_object_or_404(Comment, pk=comment_pk)
    form = CommentForm(instance=comment)

    if request.method == "POST":
        update_form = CommentForm(request.POST, instance=comment)
        comment.save()
        if update_form.is_valid():
            update_form.save()
            return redirect('review-detail', review_id=review_id)

    return redirect(review.get_absolute_url(),{'form': form})



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

    # class PostSearch(IndexView):
#     paginate_by = None
#
#     def get_queryset(self):
#         q = self.kwargs['q']
#         review_list = Review.objects.filter(
#             Q(title__contains=q) | Q(tags__name__contains=q)
#         ).distinct()
#         return review_list
#
#     def get_context_data(self, **kwargs):
#         context = super(PostSearch, self).get_context_data()
#         q = self.kwargs['q']
#         context['search_info'] = f'Search: {q} ({self.get_queryset().count()})'
#
#         return context

