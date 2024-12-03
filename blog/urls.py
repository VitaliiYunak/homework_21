from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path('', views.all_blog, name='all_blog'),
    path('login/', views.LoginUser.as_view(), name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.RegisterUser.as_view(), name='register'),
    path('add_post/', views.add_post, name='add_post'),
    path('add_comment/', views.add_comment, name='add_comment'),
    path('save_comment/', views.save_comment, name='save_comment'),
    path('all_comments_post/', views.all_comments_post, name='all_comments_post'),
    path('message_for_login/', views.message_for_login, name='message_for_login'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)