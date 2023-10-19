from django.contrib import admin
from django.urls import path, include
from universityofbigdata.views import (
        top, not_implemented, participation_guide,)
from django.conf.urls.i18n import i18n_patterns
""" -----------インポート------------"""
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = i18n_patterns(
    path('', top, name='top'),
    path('not_implemented/', not_implemented, name='not_implemented'),
    path('admin_tool/', admin.site.urls, name='admin'),
    path('i18n/', include('django.conf.urls.i18n')),
    path('competitions/', include('competitions.urls')),
    path('accounts/', include('accounts.urls')),
    path('discussion/', include('discussion.urls')),
    path('userlog/', include('userlog.urls')),
    path('management/', include('management.urls')),
    path('universityofbigdata/', include('universityofbigdata.urls')),
    path('authentication/', include('authentication.urls')),
    path('oauth/', include('social_django.urls', namespace='social')),  # Social Django用
    #
)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

""" ----------------デバッグがTrueだった場合----------------------"""
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
