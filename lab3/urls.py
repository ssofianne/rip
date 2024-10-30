"""
URL configuration for lab3 project.

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
from reconstruction import views
from django.urls import include, path
from rest_framework import routers

router = routers.DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('admin/', admin.site.urls),

    path(r'works/', views.WorkList.as_view(), name='works-list'),
    path(r'works/<int:pk>/', views.WorkDetail.as_view(), name='works-detail'),
    path(r'works/<int:pk>/add_image/', views.WorkDetail.as_view(), name='add-work-image'),
    path(r'works/draft/', views.ReconstructionList.as_view(), name='add-to-draft'),

    path(r'reconstructions/', views.ReconstructionList.as_view(), name='reconstructions-list'),
    path(r'reconstructions/<int:pk>/', views.ReconstructionDetail.as_view(), name='reconstructions-details'),
    path(r'reconstructions/<int:pk>/create/', views.ReconstructionCreature.as_view(), name='reconstruction-create'),
    path(r'reconstructions/<int:pk>/complete-reject/', views.ReconstructionCompletedRejected.as_view(), name='reconstruction-complete-reject'),
    
    path(r'reconstructions/<int:reconstruction_id>/space/<int:work_id>/', views.ReconstructionSpace.as_view(), name='reconstruction-space'),

    path(r'profile/', views.UserProfile.as_view(), name='user-profile'),
    path(r'registration/', views.UserRegistration.as_view(), name='user-registration'),
    path(r'login/', views.UserLogin.as_view(), name='user-login'),
    path(r'logout/', views.UserLogout.as_view(), name='user-logout'),

]
