from django.views.generic import DetailView
from django.views.generic.edit import FormMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.http import Http404
from competitions.models import CompetitionModel
from competitions.views import allow_invitation
from discussion.models import Discussion, DiscussionPost
from discussion.forms import DiscussionPostCreateForm, DiscussionCreateForm
import logging

logger = logging.getLogger(__name__)

class DiscussionCompetitionView(LoginRequiredMixin, FormMixin, DetailView):
    #テーブル連携
    model = CompetitionModel
    #レコード情報をテンプレートに渡すオブジェクト
    context_object_name = "competition"
    #テンプレートファイル連携
    template_name = "discussion_competition.html"
    # フォームクラス
    form_class = DiscussionCreateForm

    def get_initial(self):
        initial = super().get_initial()
        initial['post_tag_disc'] = self.get_object()
        initial['team_tag_disc'] = self.request.user.selectedTeam
        initial['user_tag_disc'] = self.request.user
        return initial
    
    def get_success_url(self):
        context = self.get_context_data()
        comp = self.get_object()
        return reverse_lazy('Discussion:discussion_competition', kwargs={'pk': self.object.pk})

    def get_object(self):
        try:
            my_object = CompetitionModel.objects.get(id=self.kwargs.get('pk'))
            return my_object
        except self.model.DoesNotExist:
            raise Http404(_("No MyModel matches the given query."))

    def get_context_data(self, *args, **kwargs):
        context = super(DiscussionCompetitionView, self).get_context_data(*args, **kwargs)
        Competition = self.get_object()
        # 投稿情報セット
        context['competition_title'] = Competition.title
        context['team_name'] = self.request.user.selectedTeam.name # 主投稿者所属チーム
        context['user_nickname'] = self.request.user.nickname # 投稿者ニックネーム
        # コメントリストセット
        query_set = Discussion.objects.filter(post_tag_disc=Competition)
        c_list = list(query_set.values())
        for i, box in enumerate(c_list):
            obj = query_set[i]
            objects = DiscussionPost.objects.filter(post_tag_post=obj)
            c_list[i]['post_count'] = len(objects) # 返信件数
            c_list[i]['team_name'] = obj.author_team_name  # 投稿者所属チーム
            c_list[i]['team_id'] = obj.author_team_id
            c_list[i]['user_nickname'] = obj.author_user_nickname # 投稿者ニックネーム
            c_list[i]['user_id'] = obj.author_user_id
            c_list[i]['obj_id'] = obj.id # リンクのPK
        context['discussion_obj'] = query_set
        context['obj_list'] = c_list
        # 認証
        is_allow = allow_invitation(self.request.user, Competition)
        context['is_allow'] = is_allow
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data()
        comp_title = context['competition_title']
        disc_title = request.POST['title_disc']
        
        form = self.get_form()
        # 検証
        if form.is_valid():
            post_dis = DiscussionCreateForm(request.POST, request.FILES)
            # 保存
            post_obj = Discussion(
                    post_tag_disc = self.get_object(),
                    team_tag_disc=self.request.user.selectedTeam,
                    user_tag_disc=self.request.user,
                    title_disc = post_dis['title_disc'].value(),
                    comment_field_disc = post_dis['comment_field_disc'].value()
                )
            post_obj.save()

            return self.form_valid(form, comp_title, disc_title)
        else:
            return self.form_invalid(form, comp_title, disc_title)

    def form_valid(self, form, comp_title, disc_title):
        msg = f"{_('議題を投稿しました')}"
        logger.info(msg, extra={
            'request': self.request,
            'action': {
                'name': 'create_post',
                'is_valid': True,
                'target_competition': comp_title,
                'title': disc_title,
                }
            })
        return super(DiscussionCompetitionView, self).form_valid(form)

    def form_invalid(self, form, comp_title, disc_title):
        msg = f"{_('議題投稿に失敗しました: ')}:\n{form.errors.as_text()}"
        logger.error(msg, extra={
            'request': self.request,
            'action': {
                'name': 'create_post',
                'is_valid': True,
                'target_competition': comp_title,
                'title': disc_title,
                }
            })
        return super(DiscussionCompetitionView, self).form_invalid(form)


class DiscussionPostView(LoginRequiredMixin, FormMixin, DetailView):
    model = Discussion
    form_class = DiscussionPostCreateForm
    context_object_name = "discussion"
    template_name = 'discussion_post.html'

    def get_initial(self):
        initial = super().get_initial()
        return initial
    
    def get_success_url(self):
        return reverse_lazy('Discussion:discussion_post', kwargs={'pk': self.object.pk})

    def get_object(self):
        try:
            my_object = Discussion.objects.get(id=self.kwargs.get('pk'))
            return my_object
        except self.model.DoesNotExist:
            raise Http404(_("No MyModel matches the given query."))

    def get_context_data(self, *args, **kwargs):
        context = super(DiscussionPostView, self).get_context_data(*args, **kwargs)
        Discussion = self.get_object()
        Competition=Discussion.post_tag_disc
        context['competition'] = Competition
        Comments = DiscussionPost.objects.filter(post_tag_post=Discussion)
        post_count = len(Comments) # 返信件数
        context['post_count'] = post_count
        team_name = Discussion.author_team_name
        context['team_name'] = team_name
        team_id = Discussion.author_team_id
        context['team_id'] = team_id
        user_nickname = Discussion.author_user_nickname
        context['user_nickname'] = user_nickname
        user_id = Discussion.author_user_id
        context['user_id'] = user_id
        c_list = list(Comments.values()) # コメントのリスト
        for i, box in enumerate(c_list):
            obj=Comments[i]
            c_list[i]['team_name'] = obj.author_team_name
            c_list[i]['team_id'] = obj.author_team_id
            c_list[i]['user_nickname'] = obj.author_user_nickname
            c_list[i]['user_id'] = obj.author_user_id
            c_list[i]['comment_field'] = obj.comment_field_post  # コメント内容
            c_list[i]['post_time'] = obj.added_datetime_post # 投稿時刻
            c_list[i]['obj_id'] = box['id'] # コメントのPK
        context['obj_list'] = c_list
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data()
        comp_title = context['competition'].title
        disc_title = self.object.title_disc
        comment = request.POST['comment_field_post']
        form = self.get_form()
        if form.is_valid():
            post_dis = DiscussionPostCreateForm(request.POST, request.FILES)
            # 保存
            post_obj = DiscussionPost(
                    post_tag_post = self.get_object(),
                    team_tag_post=self.request.user.selectedTeam,
                    user_tag_post=self.request.user,
                    comment_field_post = post_dis['comment_field_post'].value()
                )
            post_obj.save()

            msg = f"{_('議題にコメントを投稿しました')}"
            logger.info(msg, extra={
                'request': self.request,
                'action': {
                    'name': 'add_comment',
                    'is_valid': True,
                    'target_competition': comp_title,
                    'target_discussion': disc_title,
                    }
                })

            return self.form_valid(form)
        else:
            msg = f"{_('議題へのコメントに失敗しました: 入力フォームの内容に問題があります')}"
            logger.error(msg, extra={
                'request': self.request,
                'action': {
                    'name': 'add_comment',
                    'is_valid': False,
                    'target_competition': comp_title,
                    'target_discussion': disc_title,
                    }
                })
            return self.form_invalid(form)

    def form_valid(self, form):
        return super(DiscussionPostView, self).form_valid(form)

    def form_invalid(self, form):
        return super(DiscussionPostView, self).form_invalid(form)
