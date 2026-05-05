from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/',   admin.site.urls),
    path('users/',   include('users.urls')),
    path('budgets/', include('budgets.urls')),
    path('goals/',   include('goals.urls')),
    path('transactions/', include('transactions.urls')),
    path('',         RedirectView.as_view(url='/users/login/'), name='home'),
]