from django.urls import path
from . import views

urlpatterns = [
    path('',              views.goals_view,       name='goals'),
    path('<int:pk>/delete/', views.goal_delete_view, name='goal-delete'),
    path('reports/',      views.reports_view,     name='reports'),
]