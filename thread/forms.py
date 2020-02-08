from django import forms
from .models import Topic, Comment, Category


class TopicModelFrom(forms.ModelForm):
    # ゲストユーザ用入力項目
    user_name = forms.CharField(
        label='ゲストユーザ名',
        required=True,
    )

    class Meta:
        model = Topic
        fields = [
            'title',
            # 'user_name',
            'category',
            'message',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'hoge'}),
            # 'user_name' : forms.TextInput(attrs={'value': '名無し'}),

        }

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = '選択して下さい'
        self.fields['user_name'].widget.attrs['value'] = '匿名'

    def save(self, commit=True):
        topic = super().save(commit=False)
        topic.user_name = self.cleaned_data['user_name']
        if commit:
            topic.save()
        return topic


class LoginedUserTopicModelFrom(forms.ModelForm):
    class Meta:
        model = Topic
        fields = [
            'title',
            'category',
            'message',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'hoge'}),
        }

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = '選択して下さい'

    def save(self, user, commit=True, **kwargs):
        topic = super().save(commit=False)
        topic.user = user
        topic.user_name = user.username
        if commit:
            topic.save()
        return topic


class CommentModelForm(forms.ModelForm):
    # ゲストユーザ用入力項目
    user_name = forms.CharField(
        label='ゲストユーザ名',
        required=True,
    )

    class Meta:
        model = Comment
        fields = [
            # 'user_name',
            'message',
            'image',
        ]

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super().__init__(*args, **kwargs)
        self.fields['user_name'].widget.attrs['value'] = '名無し'

    def save_with_topic(self, topic_id, commit=True, **kwargs):
        comment = self.save(commit=False)
        comment.topic = Topic.objects.get(id=topic_id)
        comment.no = Comment.objects.filter(topic_id=topic_id).count() + 1
        comment.user_name = self.cleaned_data['user_name']
        if commit:
            comment.save()
        return comment


class LoginedUserCommentModelForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = [
            'message',
            'image',
        ]

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super().__init__(*args, **kwargs)

    def save_with_topic(self, topic_id, user, commit=True, **kwargs):
        comment = self.save(commit=False)
        comment.topic = Topic.objects.get(id=topic_id)
        comment.no = Comment.objects.filter(topic_id=topic_id).count() + 1
        print(user.is_authenticated, user, user.username)
        comment.user = user
        comment.user_name = user.username
        if commit:
            comment.save()
        return comment


class TopicCreateForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = [
            'title',
            'user_name',
            'category',
            'message',
        ]

    def __init__(self, *args, **kwargs):
        # kwargs.setdefault('label_suffix', '')
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = '選択して下さい'
        self.fields['user_name'].widget.attrs['value'] = '匿名'
        self.fields['title'].widget.attrs['class'] = 'huga'


# class CommentModelForm(forms.ModelForm):
#     class Meta:
#         model = Comment
#         fields = [
#             'user_name',
#             'message',
#             'image',
#         ]
#
#     def __init__(self, *args, **kwargs):
#         kwargs.setdefault('label_suffix', '')
#         super().__init__(*args, **kwargs)
#         self.fields['user_name'].widget.attrs['value'] = '名無し'
#
#     def save_with_topic(self, topic_id, commit=True):
#         comment = self.save(commit=False)
#         comment.topic = Topic.objects.get(id=topic_id)
#         comment.no = Comment.objects.filter(topic_id=topic_id).count() + 1
#         if commit:
#             comment.save()
#         return comment


class TopicForm(forms.Form):
    title = forms.CharField(
        label='タイトル',
        max_length=255,
        required=True,
    )
    user_name = forms.CharField(
        label='お名前',
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'value': '匿名'}),
    )
    category = forms.ModelChoiceField(
        label='カテゴリー',
        queryset=Category.objects.all(),
        required=True,
        empty_label='選択して下さい',
    )
    message = forms.CharField(
        label='本文',
        widget=forms.Textarea,
        required=True,
    )

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '：')
        super().__init__(*args, **kwargs)
