from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    # path('login/', views.login_user, name='login'), Use this for a separate login page + view
    path('logout/', views.logout_user, name='logout'),

]
