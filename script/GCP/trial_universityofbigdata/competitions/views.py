from django.http import Http404
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, ListView, DetailView
from django.views.generic.edit import FormMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import CompetitionModel, CompetitionPost
from .forms import  CompetitionPostCreateForm
from django.urls import reverse_lazy
from django.utils import timezone
from scipy.stats import rankdata
from static.lib import util
import datetime
import logging
from universityofbigdata.lib.mylogger import set_log_box_lite
from competitions.utils import count_daily_submissions

logger = logging.getLogger(__name__)


def allow_invitation(user, Competition):
    if (Competition.invitation_only):
        allow_team_set=(Competition.submissions_teams.all())
        if(allow_team_set is None):
            t_box=[]
        else:
            t_box=[]
            for t in allow_team_set:
                t_box.append(t.id)
        team_id=user.selectedTeam.id
        is_allow = (team_id in t_box)
    else:
        is_allow = True
    if not(user.is_participant):
        is_allow = False
    return is_allow

def allow_public(user, Competition):
    if not(Competition.public):
        allow_team_set=(Competition.submissions_teams.all())
        if(allow_team_set is None):
            t_box=[]
        else:
            t_box=[]
            for t in allow_team_set:
                t_box.append(t.id)
        team_id=user.selectedTeam.id
        is_allow = (team_id in t_box)
    else:
        is_allow = False
    if not(user.is_participant):
        is_allow = False
    return is_allow

class CompetitionsListView(LoginRequiredMixin, ListView):
    model = CompetitionModel
    template_name = "competitions_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # contextは辞書型
        status_list=['coming','active','completed',]
        # 'coming','開催準備中'), ('active','開催中'), ('completed','開催終了')
        for st in status_list:
            query_sets=CompetitionModel.objects.filter(status=st)
            box=[]
            for q_set in query_sets:
                competition_dict={}
                competition_dict['id']=q_set.id
                competition_dict['title']=q_set.title
                competition_dict['competition_abstract']=q_set.competition_abstract
                competition_dict['status']=q_set.status
                competition_dict['open_datetime']=q_set.open_datetime
                competition_dict['close_datetime']=q_set.close_datetime
                competition_dict['public']=q_set.public
                competition_dict['invitation_only']=q_set.invitation_only
                # 投稿数、参加者数、参加チーム数
                post_set=CompetitionPost.objects.filter(post=q_set,)
                competition_dict['post_count']=len(post_set)
                team_set=post_set.order_by('team_tag').distinct().values_list('team_tag')
                competition_dict['team_count']=len(team_set)
                user_set=post_set.order_by('user_tag').distinct().values_list('user_tag')
                competition_dict['user_count']=len(user_set)
                # 認証
                is_allow = allow_public(self.request.user, q_set)
                competition_dict['is_allow_public'] = is_allow
                box.append(competition_dict)
            context[st+'_object_box']=box
        return context


class CompetitionsMainView(LoginRequiredMixin, DetailView):
    model = CompetitionModel
    context_object_name = "competition"
    template_name = "competitions_main.html"

    def get_context_data(self, *args, **kwargs):
        context = super(CompetitionsMainView, self).get_context_data(*args, **kwargs)
        Competition = self.get_object()
        # 認証
        is_allow = allow_invitation(self.request.user, Competition)
        context['is_allow'] = is_allow
        # logging
        message = set_log_box_lite('show Competitions Main page', self.request)
        logger.info(message)
        return context
    
    def get_object(self):
        try:
            my_object = CompetitionModel.objects.get(id=self.kwargs.get('pk'))
            return my_object
        except self.model.DoesNotExist:
            raise Http404(_("No MyModel matches the given query."))

class CompetitionsDataView(LoginRequiredMixin, DetailView):
    model = CompetitionModel
    context_object_name = "competition"
    template_name = "competitions_data.html"

    def get_context_data(self, *args, **kwargs):
        context = super(CompetitionsDataView, self).get_context_data(*args, **kwargs)
        Competition = self.get_object()
        # 認証
        is_allow = allow_invitation(self.request.user, Competition)
        context['is_allow'] = is_allow
        # logging
        message = set_log_box_lite('show Competitions Data page', self.request)
        logger.info(message)
        return context
    
    def get_object(self):
        try:
            my_object = CompetitionModel.objects.get(id=self.kwargs.get('pk'))
            return my_object
        except self.model.DoesNotExist:
            raise Http404(_("No MyModel matches the given query."))


class CompetitionsRankingView(LoginRequiredMixin, DetailView):
    model = CompetitionModel
    context_object_name = "competition"
    template_name = "competitions_ranking.html"
    
    def get_context_data(self, *args, **kwargs):
        """リーダーボードの計算・表示

        XXX: GETされるごとに計算されるが、それで良い?
        """
        context = super(CompetitionsRankingView, self).get_context_data(*args, **kwargs)
        Competition = self.get_object()
        post_tags=CompetitionPost.objects.filter(post=Competition.id)
        # チームリスト取得
        team_list=[]
        for post_obj in post_tags:
            team_list.append(post_obj.team)
        team_list_set = set(team_list)
        # 各チームの最新の投稿を取得
        def get_post_id_with_last_post(team_list_set):
            post_tag_last_ids=[]
            post_for_team={}
            post_score =[]
            post_fin_score =[]
            post_tag_list=[]
            for team_p in team_list_set:
                post_sets_ = post_tags.filter(team=team_p)
                last_post = post_sets_.latest('added_datetime')
                post_tag_last_ids.append(last_post.id)
                post_score.append(last_post.intermediate_score)
                post_fin_score.append(last_post.final_score)
                post_tag_list.append(last_post)
                box=[]
                for ob in post_sets_:
                    # 提出チーム, 提出者, 中間スコア, 最終スコア, 提出日時, 提出数(本日), 提出数(総提出数)
                    bx=[]
                    bx = [str(ob.team), str(ob.poster), str(ob.intermediate_score), str(ob.final_score), ob.added_datetime.date(), str(ob.count_par_today), str(ob.count_posts), ]
                    box.append(bx)
                team_ts = post_tags.filter(team=team_p)[0]
                team_id = team_ts.team_id
                post_for_team[int(team_id)] = box
            return post_tag_last_ids, post_for_team, post_tag_list, post_score, post_fin_score
        post_tag_last_ids, post_for_team, post_tag_list, post_score, post_fin_score = get_post_id_with_last_post(team_list_set)
        #print(post_for_team)

        # スコアの整理
        score_list=[]
        fin_score_list=[]
        for post_obj in post_tags:
            score_list.append(post_obj.intermediate_score)
            fin_score_list.append(post_obj.final_score)
        
        # reverse の決定 ('classification','分類'),])
        # 小さいほうが良い : ('rocauc', 'マクロ平均ROC-AUC'),('auc','Area under the ROC curve (AUC)'),
        # 大きいほうほど良い : ('mean_absolute_error','平均絶対誤差'),('mean_squared_error','二乗平均誤差'),('root_mean_squared_error','二乗平均平方根誤差',),('mean_roc_auc_score','Area under the ROC curve (AUC)'),('roc_auc_score', 'マクロ平均ROC-AUC'),
        type_e=Competition.evaluation_type
        is_reverse = -1
        if((type_e in ['mean_absolute_error', 'mean_squared_error','root_mean_squared_error']) ):
            # 大きい順
            is_reverse = 1
        else:
            is_reverse = -1
        # 管理用順位付け
        rank_list=rankdata([is_reverse * i for i in score_list], method='min').astype(int)
        final_rank_list = rankdata([is_reverse * i for i in fin_score_list], method='min').astype(int)
        # 管理用
        score_management_box=[]
        for post_obj, score, f_score, rank_id, f_rank_id in zip(post_tags, score_list, fin_score_list, rank_list, final_rank_list):
            # 最終順位 現在順位 提出チーム/提出者 中間スコア 最終スコア 提出日時 提出数(本日/総提出数)
            b2 = [f_rank_id, rank_id, str(post_obj.team)+' / '+str(post_obj.poster), score, f_score,post_obj.added_datetime.date(), str(post_obj.count_par_today) + ' / ' + str(post_obj.count_posts), ]
            score_management_box.append(b2)
        # 表示用の調整、並べ替え
        score_management_box = sorted(
            score_management_box, key=lambda x: x[1], reverse=False)
        score_management_fin_box = sorted(
            score_management_box, key=lambda x: x[0], reverse=False)

        # 表示用順位付け
        show_rank_list = rankdata([is_reverse * i for i in post_score], method='min').astype(int)
        show_final_rank_list = rankdata([is_reverse * i for i in post_fin_score], method='min').astype(int)
        # 可視化表用並び替え
        score_box=[]
        score_fin_box=[]
        # # チーム単位の評価
        for post_obj, score, f_score, rank_id, f_rank_id in zip(post_tag_list, post_score, post_fin_score, show_rank_list, show_final_rank_list):
            # 現在順位 提出チーム/提出者 中間スコア 提出日時 提出数(本日/総提出数)
            b = [rank_id, str(post_obj.team)+' / '+str(post_obj.poster), score,post_obj.added_datetime.date(), str(post_obj.count_par_today) + ' / ' + str(post_obj.count_posts), ]
            score_box.append(b)
            # 最終順位 現在順位 提出チーム/提出者 中間スコア 最終スコア 提出日時 提出数(本日/総提出数),object
            bf = [f_rank_id, rank_id, str(post_obj.team)+' / '+str(post_obj.poster), score, f_score, post_obj.added_datetime.date(), str(post_obj.count_posts), post_obj]
            score_fin_box.append(bf)
        # ランキング表並べ替え
        score_box = sorted(score_box, key=lambda x: x[0], reverse=False)
        score_fin_box = sorted(score_fin_box, key=lambda x: x[0], reverse=False)

        # 優勝者の登録
        winner_list=[]
        for score_id in score_fin_box:
            if(score_id[0]==1):
                winner_list.append(score_id[7].team_tag)
        Competition.winner_teams.set(winner_list)
        Competition.save()

        # 表示用
        context['Post_tags'] = post_tags
        context['Post_score'] = score_box
        context['Post_management_score'] = score_management_box
        context['Post_management_fin_score'] = score_management_fin_box
        context['Post_fin_score'] = score_fin_box
        context['public'] = Competition.public
        context['invitation_only'] = Competition.invitation_only
        context['status'] = Competition.status
        context['post_for_team'] = post_for_team
        # 認証
        is_allow = allow_invitation(self.request.user, Competition)
        context['is_allow'] = is_allow
        return context


class CompetitionsPostView(LoginRequiredMixin, FormMixin, DetailView):
    model = CompetitionPost
    form_class = CompetitionPostCreateForm
    context_object_name = "competition"
    template_name = 'competitions_post.html'
    extra_context = {"extra": "This is an extra context."}

    def get_initial(self):
        initial = super().get_initial()
        # 投稿カウント用処理
        today = timezone.localtime(timezone.now()).date()
        today = timezone.datetime(
                today.year, today.month, today.day,
                tzinfo=timezone.get_current_timezone())
        tomorrow = (today + datetime.timedelta(days=1))
        query_set=CompetitionPost.objects.filter(post=self.get_object(), team_tag=self.request.user.selectedTeam, added_datetime__range=[today,tomorrow])
        initial['count_par_today'] = len(query_set)
        return initial
    
    def get_success_url(self):
        # logging
        message = set_log_box_lite('Post Competitions try data page', self.request)
        logger.info(message)
        return reverse_lazy('Competitions:competitions_ranking', kwargs={'pk': self.object.pk})

    def get_object(self):
        try:
            my_object = CompetitionModel.objects.get(id=self.kwargs.get('pk'))
            return my_object
        except self.model.DoesNotExist:
            raise Http404(_("No MyModel matches the given query."))

    def get_context_data(self, *args, **kwargs):
        context = super(CompetitionsPostView, self).get_context_data(*args, **kwargs)
        Competition = self.get_object()
        # form
        context['form'] = self.get_form()
        context['Competition_data'] = Competition
        context['n_sub_daily'] = count_daily_submissions(
                self.request.user, Competition)
        context['post_tag'] = self.get_object().title
        context['team_tag'] = self.request.user.selectedTeam.name
        context['user_tag'] = self.request.user.nickname
        # 認証
        is_allow = allow_invitation(self.request.user, Competition)
        context['is_allow'] = is_allow
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        self.extra_context['post_error'] = None

        n_day_sub = count_daily_submissions(
                request.user, self.get_object())

        if n_day_sub >= self.object.n_max_submissions_per_day:
            self.extra_context['post_error']= _('一日の最大投稿回数を越えています。')
            return self.form_invalid(form)

        if form.is_valid():
            # comp_form = CompetitionPostCreateForm(request.POST, request.FILES)
            # スコア計算式の取得
            Competition = self.get_object()
            # データ読み込み
            y_pred = util.read_file_key(request.FILES['post_key'])
            y_true = util.read_file_key(Competition.truth_blob_key)
            # チェック
            if(len(y_pred) == len(y_true)):
                # データ数が同じなら投稿保存処理へ
                # スコア計算 #桁オーバーに注意
                test_idx = int(len(y_true)*(
                    Competition.public_leaderboard_percentage/100))
                final_idx = min(len(y_pred), len(y_true))-1
                score, final_score = util.calculate_score(
                        Competition.evaluation_type, y_true, y_pred, test_idx, final_idx)
                # 保存
                post_obj = CompetitionPost(
                    post = self.get_object(),
                    team_tag=self.request.user.selectedTeam,
                    user_tag=self.request.user,
                    count_par_today=n_day_sub + 1,
                    post_key=request.FILES['post_key'],
                    intermediate_score=score,
                    final_score = final_score
                )
                post_obj.save()
                return self.form_valid(form)
            else:
                # logging
                message = set_log_box_lite('Post miss data', self.request)
                logger.info(message)
                if(len(y_pred) == 0):
                    self.extra_context['post_error'] = None
                else:
                    self.extra_context['post_error']= _('投稿ファイルのデータ数が異なります。')
                return self.form_invalid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        return super(CompetitionsPostView, self).form_valid(form)

    def form_invalid(self, form):
        return super(CompetitionsPostView, self).form_invalid(form)

