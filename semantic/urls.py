"""
URL configuration for semantic project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from analyze.views import upload_text, download_file, summarize_text, getEntities
from users.views import login_view
from historyRDF import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/upload/', upload_text, name='upload_text'),
    path('api/summarize/', summarize_text, name='summarize_text'),
    path('api/getEntities/', getEntities, name='getEntities'),
    path('api/generate/', download_file, name='generate_rdf'),
    path('api/login/', login_view, name='login'),
    path('api/download/<str:filename>/', views.download_file, name='download_file'),
]
