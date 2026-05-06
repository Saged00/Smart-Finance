from django.urls import path
from . import views

urlpatterns = [
    path('',                       views.transaction_list_view,  name='transactions'),
    path('income/add/',            views.income_create_view,     name='income-create'),
    path('expense/add/',           views.expense_create_view,    name='expense-create'),
    path('income/<int:pk>/edit/',   views.income_edit_view,      name='income-edit'),
    path('expense/<int:pk>/edit/',  views.expense_edit_view,     name='expense-edit'),
    path('income/<int:pk>/delete/', views.income_delete_view,    name='income-delete'),
    path('expense/<int:pk>/delete/',views.expense_delete_view,   name='expense-delete'),
]
