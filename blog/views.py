from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import LoginUserForm, RegisterUserForm, PostForm, CommentForm
from .models import Post, Comment


def send_email_to_user(subject, message, recipient_email):
    """ Відправлення повідомлення на електронну адресу """
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,  # Адреса відправника
        [recipient_email],  # Адреса отримувача
        fail_silently=False)


class LoginUser(LoginView):
    """ Авторизація """
    template_name = 'blog/login.html'
    form_class = LoginUserForm
    extra_context = {'title': 'Авторизація'}

    def get_success_url(self):
        return reverse_lazy('all_blog')


class RegisterUser(CreateView):
    """ Реєстрація нового користувача """
    form_class = RegisterUserForm
    template_name = 'blog/register.html'
    extra_context = {"title": "Реєстрація користувача"}
    success_url = reverse_lazy('message_for_login')

    def form_valid(self, form):
        """ Якщо форма валідна, створюємо користувача та відправляємо лист """
        response = super().form_valid(form)
        # Отримання електронної пошти користувача
        user_email = form.cleaned_data.get('email')
        # Відправлення листа на email
        try:
            send_email_to_user(
                'Успіх',  # Тема
                f'Вітаємо! Ви успішно зареєстровані на сайті.',
                user_email
            )
        except Exception as e:
            print(e)
        return response


def logout_user(request):
    """
    Функція викликає метод logout(request) для виходу користувача із системи.
    """
    logout(request)
    return redirect('all_blog')


def all_blog(request):
    """ Всі пости """
    # posts = Post.objects.all()

    # Всі пости з кількістю коментарів до кожного посту
    posts = Post.objects.annotate(comment_count=Count('comment')).order_by('-updated_at')

    context = {'posts': posts,
               'title': "Пости"}
    form = CommentForm()
    context['comment_form'] = form
    return render(request, 'blog/index.html', context=context)


@login_required(login_url='login')
def add_comment(request):
    """ Сторінка з формою для додавання коментаря """
    post_id = request.POST.get('post_id')
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm()
    return render(request, 'blog/add_comment.html', {'form': form,
                                                     'post': post,
                                                     "title": "Дадати коментар"})


def save_comment(request):
    """ Збереження нового коментаря """
    context = {"title": "Додати коментар"}
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        context["post"] = post
        form = CommentForm(request.POST)
        if form.is_valid():
            user_email = request.user.email
            new_comment = form.save(commit=False)
            new_comment.post = post
            new_comment.comment_author = request.user
            new_comment.save()
            try:
                # Відправлення повідомлення на email
                send_email_to_user(
                    'Успіх',
                    f'Вітаємо! Ваш коментар успішно розміщений на сайті.',
                    user_email)  # Адреса отримувача
            except Exception as e:
                print(e)
            return render(request,'blog/message_to_user.html')
    else:
        form = CommentForm()
        context["form"] = form
    return render(request, 'blog/add_comment.html', context=context)


def all_comments_post(request):
    """ Всі коментарі для посту """
    context ={
        'title': "Коментарі"
    }
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        context["post"] = post
        all_comments = Comment.objects.filter(post=post)
        if all_comments:
            context["all_comments"] = all_comments
            for comment in all_comments:
                print(comment.comment_author)
                print(comment.content)
    return render(request, 'blog/post_comments.html', context=context)


@ login_required(login_url='login')
def add_post(request):
    """ Додавання посту авторизованим користувачем """
    title = "Додати пост"
    # Визначаємо електронну адресу авторизованого користувача
    user_email = request.user.email
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post_title = form.cleaned_data['title']
            post = form.save(commit=False)
            # Визначаємо авторизованого користувача (логін)
            post.author = request.user
            # Зберігаємо в БД
            post.save()
            # Зберігаємо до БД зв'язок ManyToMany
            form.save_m2m()
            # Відправляємо повідомлення на електронну пошту
            try:
                send_email_to_user(
                    'Успіх',
                    f'Вітаємо! Ваш пост "{post_title}" успішно розміщений на сайті.',
                    user_email,  # Адреса отримувача
                    )
            except Exception as e:
                print(e)
            return redirect("all_blog")
        else:
            print(form.errors.values())
    else:
        form = PostForm()
    return render(request, 'blog/add_post.html', {'form': form, "title": title})


def message_for_login(request):
    return render(request, 'blog/message_for_login.html')
