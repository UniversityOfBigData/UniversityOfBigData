from django.contrib import admin
from .models import CompetitionModel
from .models import CompetitionPost

class CompetitionModelAdmin(admin.ModelAdmin): #Django管理サイトの画面を編集
    # リスト画面
    list_display = ('id','title','owner','owner_name','status','added_datetime','open_datetime','close_datetime')

    # 以下の2行は詳細画面のため
    fields = ('title','title_en',
              'owner','owner_name',
              'competition_abstract','competition_abstract_en',
              'competition_description','competition_description_en',
              'problem_type','evaluation_type','leaderboard_type','use_forum',
              'open_datetime','close_datetime',
              'status',
              'public','invitation_only',
              'n_max_submissions_per_day','public_leaderboard_percentage',
              'blob_key','truth_blob_key',
              'file_description','file_description_en',
              'authentication_code',)
    readonly_fields = ('added_datetime', )


admin.site.register(CompetitionModel, CompetitionModelAdmin)

class CompetitionPostAdmin(admin.ModelAdmin): #Django管理サイトの画面を編集
    # リスト画面
    list_display = ('id','post','added_datetime','count_par_today','poster','poster_id','team','team_id','post_key','team_tag','user_tag','intermediate_score','final_score',)

    # 以下の2行は詳細画面のため
    fields = ( 'post','added_datetime','count_par_today',
                'team_tag',
                'user_tag',
                'post_key'
              )
    readonly_fields = ('added_datetime', )

admin.site.register(CompetitionPost, CompetitionPostAdmin)


