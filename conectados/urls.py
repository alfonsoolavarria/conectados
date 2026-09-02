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
    path('desafio-editar/<int:challenge_id>/', views.edit_challenge, name='edit_challenge'),
    path('desafio-historial/<int:challenge_id>/', views.challenge_historial, name='challenge_historial'),
    path('desafio/<int:challenge_id>/muro/', views.muro_desafio, name='muro_desafio'),
    path('desafio/<int:challenge_id>/lectura/', views.lectura, name='lectura'),
    path('desafio/<int:challenge_id>/muro/comment/', views.muro_desafio_comment, name='muro_desafio_comment'),
    path('desafio-muro/comment/delete/<int:comment_id>/', views.muro_desafio_comment_delete, name='muro_desafio_comment_delete'),
    path('desafio-muro/react/<int:comment_id>/', views.muro_desafio_react, name='muro_desafio_react'),
    path('mis-desafios/', views.mis_desafios, name='mis_desafios'),
    path('qr/', views.qr_lideres, name='qr_lideres'),
    path('cambiar-contrasena/', views.cambiar_contrasena, name='cambiar_contrasena'),
    path('perfil-imagen/', views.perfil_imagen, name='perfil_imagen'),
    path('competencias/', views.competencias, name='competencias'),
    path('entrevistas/', views.entrevistas, name='entrevistas'),
    path('competencias/react/<int:photo_id>/', views.competencia_react, name='competencia_react'),
    path('competencias/comment/<int:photo_id>/', views.competencia_comment, name='competencia_comment'),
    path('competencias/comment/edit/<int:comment_id>/', views.competencia_comment_edit, name='competencia_comment_edit'),
    path('competencias/comment/delete/<int:comment_id>/', views.competencia_comment_delete, name='competencia_comment_delete'),
    path('', views.home, name='home'),
]
