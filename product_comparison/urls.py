from django.contrib import admin
from django.urls import path
from scraper import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('comparison/', views.comparison, name='comparison'),
]