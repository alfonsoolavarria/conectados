from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path

from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('checklist/toggle/', views.toggle_day, name='toggle_day'),
    path('estadisticas/', views.estadisticas, name='estadisticas'),
    path('mensajeria/', views.mensajeria, name='mensajeria'),
    path('mensajeria/<int:user_id>/', views.conversacion, name='conversacion'),
    path('desafio/<int:cabin_id>/', views.challenge, name='challenge'),
    path('qr/', views.qr_lideres, name='qr_lideres'),
    path('', views.home, name='home'),
]
