from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import gettext_lazy as _
from .models import User, TeamTag

class MyUserChangeForm(UserChangeForm): #ユーザー更新フォームを作成
    class Meta:
        model = User
        fields = '__all__'

class MyUserCreationForm(UserCreationForm): #ユーザー登録フォームを作成
    class Meta:
        model = User
        fields = ('email','username')

class MyUserAdmin(UserAdmin): #Django管理サイトの画面を編集
    fieldsets = (
        (None, {'fields': ('username', 'email','nickname', 'password',)}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                    'is_guest','is_participant','groups',)}),
        (_('Team'), {'fields': ['selectedTeam']}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'nickname','password1', 'password2'),
        }),
        (_('Team'), {'fields': ['selectedTeam']}),
    )# ユーザー追加時の設定項目
    form = MyUserChangeForm
    add_form = MyUserCreationForm
    list_display = ('email', 'username','nickname','affiliation_organization','is_active', 'is_staff', 'is_superuser', 'is_guest','is_participant', )
    
    # フィルターによる絞り込み部分
    list_filter = ()
    search_fields = ('email', 'username','nickname')
    ordering = ('email',)

admin.site.register(User, MyUserAdmin) #Django管理サイトへUserモデルとUserAdminを登録

class MyTeamAdmin(admin.ModelAdmin): #Django管理サイトの画面を編集
    list_display = ('name',)
    fields = ('name',)

admin.site.register(TeamTag, MyTeamAdmin)
