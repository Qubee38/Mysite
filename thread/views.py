from django.core.mail import send_mail, EmailMessage
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (
    CreateView, FormView, DetailView, TemplateView, ListView)
from django.urls import reverse_lazy

from . forms import (
    TopicModelFrom, TopicForm, CommentModelForm,
    LoginedUserTopicModelFrom, LoginedUserCommentModelForm
)
from . models import Topic, Category, Comment, Vote


class TopicDetailView(DetailView):
    template_name = 'thread/detail_topic.html'
    model = Topic
    context_object_name = 'topic'


class TopicCreateView(CreateView):
    template_name = 'thread/create_topic.html'
    form_class = LoginedUserTopicModelFrom
    model = Topic
    success_url = reverse_lazy('base:top')

    def get_form_class(self):
        """ ログイン状態によってフォームを動的に変更する
        """
        if self.request.user.is_authenticated:
            return LoginedUserTopicModelFrom
        else:
            return TopicModelFrom

    def form_valid(self, form):
        ctx = {'form': form}
        if self.request.POST.get('next', '') == 'confirm':
            ctx['category'] = form.cleaned_data['category']
            return render(self.request, 'thread/confirm_topic.html', ctx)
        if self.request.POST.get('next', '') == 'back':
            return render(self.request, 'thread/create_topic.html', ctx)
        if self.request.POST.get('next', '') == 'create':
            form.save(self.request.user)
            # メール送信処理
            # send_mail(
            #     subject='トピック作成: ' + form.cleaned_data['title'],
            #     message='トピックが生成されました',
            #     from_email='hogehoge@example.com',
            #     recipient_list = [
            #         'admin@example.com',
            #     ]
            # )
            # return super().form_valid(form)
            return redirect(self.success_url)
        else:
            # 正常動作ではここは通らない。エラーページへの遷移でも良い
            return redirect(reverse_lazy('base:top'))


class TopicAndCommentView(FormView):
    template_name = 'thread/detail_topic.html'
    form_class = LoginedUserCommentModelForm

    def get_form_class(self):
        """ ログイン状態によってフォームを動的に変更する
        """
        if self.request.user.is_authenticated:
            return LoginedUserCommentModelForm
        else:
            return CommentModelForm

    def form_valid(self, form):
        # comment = form.save(commit=False)  # 保存せずオブジェクト生成する
        # comment.topic = Topic.objects.get(id=self.kwargs['pk'])
        # comment.no = Comment.objects.get(topic=self.kwargs['pk']).count() + 1
        # comment.save()

        # Comment.objects.create_comment(
        #       user_name=form.cleaned_data['user_name'],
        #       message=form.cleaned_data['message'],
        #       topic_id=self.kwargs['pk'],
        #       image=form.cleaned_data['image']
        #   )
        kwargs = {}
        if self.request.user.is_authenticated:
            kwargs['user'] = self.request.user
        # コメント保存のためsave_with_topicメソッドを呼ぶ
        form.save_with_topic(self.kwargs.get('pk'), **kwargs)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('thread:topic', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self):
        ctx = super().get_context_data()
        ctx['topic'] = Topic.objects.get(id=self.kwargs['pk'])
        # ctx['comment_list'] = Comment.objects.filter(
        #          topic_id=self.kwargs['pk']).order_by('no')
        ctx['comment_list'] = Comment.objects.filter(
            topic_id=self.kwargs['pk']).annotate(vote_count=Count('vote')).order_by('no')
        return ctx


class CategoryView(ListView):
    template_name = 'thread/category.html'
    context_object_name = 'topic_list'
    paginate_by = 5
    page_kwarg = 'p'

    def get_queryset(self):
        return Topic.objects.filter(category__url_code=self.kwargs['url_code'])

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['category'] = get_object_or_404(Category, url_code=self.kwargs['url_code'])
        return ctx


class TopicCreateViewBySession(FormView):
    """セッションを使用したトピック作成
    """
    template_name = 'thread/create_topic.html'
    form_class = TopicForm

    def post(self, request, *args, **kwargs):
        ctx = {}
        if request.POST.get('next', '') == 'back':
            if 'input_data' in self.request.session:
                input_data = self.request.session['input_data']
                form = TopicForm(input_data)
                ctx['form'] = form
            return render(request, self.template_name, ctx)
        elif request.POST.get('next', '') == 'create':
            if 'input_data' in self.request.session:
                Topic.objects.create_topic(
                    title=request.session['input_data']['title'],
                    user_name=request.session['input_data']['user_name'],
                    category_id=request.session['input_data']['category'],
                    message=request.session['input_data']['message'],
                )
                # メールの送信処理は省略
                response = redirect(reverse_lazy('base:top'))
                response.set_cookie('categ_id', request.session['input_data']['category'])
                # セッションに保管した情報の削除
                request.session.pop('input_data')
                return response
        elif request.POST.get('next', '') == 'confirm':
            form = TopicForm(request.POST)
            if form.is_valid():
                ctx = {'form': form}
                # セッションにデータを保存
                input_data = {
                    'title': form.cleaned_data['title'],
                    'user_name': form.cleaned_data['user_name'],
                    'category': form.cleaned_data['category'].id,
                    'message': form.cleaned_data['message'],
                }
                request.session['input_data'] = input_data
                ctx['category'] = form.cleaned_data['category']
                return render(request, 'thread/confirm_topic.html', ctx)
            else:
                return render(request, self.template_name, {'form': form})

    def get_context_data(self):
        ctx = super().get_context_data()
        if 'categ_id' in self.request.COOKIES:
            form = ctx['form']
            form['category'].field.initial = self.request.COOKIES['categ_id']
            ctx['form'] = form
        return ctx
        

# def topic_create(request):
#     template_name = 'thread/create_topic.html'
#     ctx = {}
#     if request.method == 'GET':
#         # form = TopicForm()
#         # ctx['form'] = form
#         ctx['form'] = TopicCreateForm()
#         return render(request, template_name, ctx)
#
#     if request.method == 'POST':
#         topic_form = TopicCreateForm(request.POST)
#         if topic_form.is_valid():
#             topic_form.save()
#             # topic = Topic()
#             # cleaned_data = topic_form.cleaned_data
#             # topic.title = cleaned_data['title']
#             # topic.message = cleaned_data['message']
#             # topic.user_name = cleaned_data['user_name']
#             # topic.category = cleaned_data['category']
#             # topic.save()
#             return redirect(reverse_lazy('base:top'))
#         else:
#             ctx['form'] = topic_form
#             return render(request, template_name, ctx)
