from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("konsultasi/", views.consultation, name="consultation"),
    path("basis-pengetahuan/", views.knowledge, name="knowledge"),
    path("uji-dugaan/", views.quiz, name="quiz"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("dataset/", views.dataset, name="dataset"),
    path("dataset/unduh/", views.download_csv, name="download_csv"),
]
