"""
URL configuration for reconstruction_works project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from reconstruction_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.main_page, name='main_page'),
    path('work/<int:work_id>/', views.page2, name='page2'),
    path('reconstruction/<int:reconstruction_id>/', views.page3, name='page3'),
    path('add_work/<int:work_id>', views.add_work, name='add_work'),
    path('reconstruction_delete/<int:reconstruction_id>', views.reconstruction_delete, name='reconstruction_delete'),
]