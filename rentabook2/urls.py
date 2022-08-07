"""rentabook2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from bookquery import views as bq_views
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from user import views as user_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", bq_views.BookQueryView, name="search"),
    path("iwantin/", user_views.RegisterUser, name="register"),
    path(
        "gimme/",
        auth_views.LoginView.as_view(template_name="user/login.html"),
        name="login",
    ),
    path(
        "downloadAPI/<book_id>",
        bq_views.DownloadView.as_view(),
        name="download-book-api",
    ),
    path(
        "downloadLocalAPI/<book_id>",
        bq_views.DownloadLocalView.as_view(),
        name="download-local-api",
    ),
]
