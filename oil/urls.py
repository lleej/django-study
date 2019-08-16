from django.urls import path

from . import views

urlpatterns = [
    path('place/<int:id>/', views.id_place),
]
