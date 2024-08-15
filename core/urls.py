from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('generate-blog/', views.generate_blog, name='generate_blog')
]