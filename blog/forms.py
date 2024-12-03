from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError

from blog.models import Post, Comment, Category


# Обмеження розміру завантаженого файлу
def validate_image_size(file):
    max_size = 5 * 1024 * 1024  # 5MB
    if file.size > max_size:
        raise ValidationError(f"Розмір файлу не повинен перевищувати {max_size} (зараз {file.size / (1024 * 1024):.2f} МБ).")


class LoginUserForm(AuthenticationForm):
    """
    Форма авторизації. Використовується вбудована з класу LoginView
    """
    username = forms.CharField(label='Логін',
                               widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Пароль',
                               widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        # Використовуємо поточну модель користувача, тому що стандартна модель User може бути змінена.
        model = get_user_model()
        fields = ['username', 'password']


class RegisterUserForm(UserCreationForm):
    """
    Форма реєстрації користувача
    """
    username = forms.CharField(label='Логін', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label="Підтвердження пароля",
                                widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'password1', 'password2')
        labels = {
            'email': "E-mail",
            }
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            }

    def clean_email(self):
        """
        Перевірка на унікальність електронної пошти
        :return: email
        """
        email = self.cleaned_data.get('email')
        if get_user_model().objects.filter(email=email).exists():
            raise forms.ValidationError("Такий E-mail вже існує")
        return email



class PostForm(forms.ModelForm):
    """
    Форма додавання нового посту
    """
    category = forms.ModelChoiceField(queryset=Category.objects.all(),
                                      label="Категорія", empty_label="--Оберіть категорію--")
    # image = forms.ImageField(
    #     label="Зображення", required=True,
    #     validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif']),
    #                 validate_image_size]
    # )

    class Meta:
        model = Post
        fields = ['title', 'content', 'category', 'tags', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'})
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
           'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}), # Встановлюємо висоту в 3 рядка
        }
