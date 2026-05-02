from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/',        views.dashboard_view,      name='dashboard'),
    path('',                  views.budget_list_view,    name='budget-list'),
    path('create/',           views.budget_create_view,  name='budget-create'),
    path('<int:pk>/edit/',    views.budget_edit_view,    name='budget-edit'),
    path('<int:pk>/delete/',  views.budget_delete_view,  name='budget-delete'),
    path('alerts/',           views.budget_alerts_view,  name='budget-alerts'),
]