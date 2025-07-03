from django.urls import path

from . import views

app_name = "polls"
urlpatterns = [
    path("", views.index, name="index"),
    path("<int:question_id>/", views.detail, name="detail"),
    path("<int:pk>/results/", views.ResultsView.as_view(), name="results"),
    path("<int:question_id>/vote/", views.vote, name="vote"),

    path("create/", views.create_poll, name="create_poll"),
    path("edit/<int:pk>/", views.edit_poll, name="edit_poll"),
    path("delete/<int:pk>/", views.delete_poll, name="delete_poll"),
]