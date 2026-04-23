from django import forms
from django.contrib.auth import get_user_model
from .models import Topic, Task

User = get_user_model()


class CreateStudentForm(forms.Form):
    first_name = forms.CharField(max_length=64, required=False, label='Имя')
    last_name  = forms.CharField(max_length=64, required=False, label='Фамилия')
    username   = forms.CharField(max_length=150, label='Логин')
    email      = forms.EmailField(required=False, label='Email')
    password   = forms.CharField(min_length=6, label='Пароль')

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(f'Ученик с логином «{username}» уже существует.')
        return username


class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['title', 'description']
        labels = {'title': 'Название', 'description': 'Описание'}
        widgets = {
            'title':       forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Например: Циклы'}),
            'description': forms.Textarea(attrs={
                'class': 'form-input', 'rows': 3,
                'placeholder': 'Краткое описание темы',
            }),
        }


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['topic', 'number', 'text_ru', 'text_kg']
        labels = {
            'topic': 'Тема', 'number': 'Номер задачи',
            'text_ru': 'Условие (RU)', 'text_kg': 'Шарт (KG)',
        }
        widgets = {
            'topic':   forms.Select(attrs={'class': 'form-input'}),
            'number':  forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '1', 'min': 1}),
            'text_ru': forms.Textarea(attrs={
                'class': 'form-input', 'rows': 5,
                'placeholder': 'Напишите условие задачи на русском...',
            }),
            'text_kg': forms.Textarea(attrs={
                'class': 'form-input', 'rows': 4,
                'placeholder': 'Шарт кыргызча (милдеттүү эмес)',
            }),
        }


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, label='Логин')
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')