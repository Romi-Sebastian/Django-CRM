from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    # path('login/', views.login_user, name='login'), Use this for a separate login page + view
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),
    path('record/<int:pk>', views.customer_record, name='record'),
    path('delete_record/<int:pk>', views.delete_record, name='delete'),
    path('add_record/', views.add_record, name='add'),
    path('update_record/<int:pk>', views.update_record, name='update'),
    path('profile/', views.profile_view, name='profile'),
    path('toggle_task/<int:task_id>', views.toggle_task_completion, name='toggle_task'),
    path('edit_task/<int:task_id>', views.edit_task, name='edit_task'),
    path('delete_task/<int:task_id>', views.delete_task, name='delete_task')

]
