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
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.contrib import admin
from reconstruction import views
from django.urls import include, path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


router = routers.DefaultRouter()
router.register(r'user', views.UserViewSet, basename='user')

schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),

    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('user/login/',  views.login, name='login'),
    path('user/logout/', views.logout, name='logout'),
    path('', include(router.urls)),

    path(r'works/', views.WorkList.as_view(), name='add-to-draft'),
    path(r'works/', views.WorkList.as_view(), name='works-list'),
    path(r'works/<int:pk>/', views.WorkDetail.as_view(), name='work-details'),
    path(r'works/add/', views.add_work, name='add_work'),
    path(r'works/<int:pk>/image/', views.add_image_work, name='add_image_work'),
    path(r'works/<int:pk>/', views.WorkDetail.as_view(), name='change_work_details'),
    path(r'works/<int:pk>/', views.WorkDetail.as_view(), name='delete_work'),
    
    path(r'reconstructions/', views.ReconstructionList.as_view(), name='reconstructions-list'),
    path(r'reconstructions/<int:pk>/', views.ReconstructionDetail.as_view(), name='reconstructions-details'),
    path(r'reconstructions/<int:pk>/create/', views.ReconstructionCreature.as_view(), name='reconstruction-create'),
    path(r'reconstructions/<int:pk>/finish/', views.ReconstructionCompletedRejected.as_view(), name='reconstruction-complete-reject'),
    
    path(r'reconstructions/<int:reconstruction_id>/space/<int:work_id>/', views.ReconstructionSpace.as_view(), name='reconstruction-space'),

    # path(r'profile/', views.UserProfile.as_view(), name='user-profile'),
    # path(r'registration/', views.UserRegistration.as_view(), name='user-registration'),
    # path(r'login/', views.UserLogin.as_view(), name='user-login'),
    # path(r'logout/', views.UserLogout.as_view(), name='user-logout'),

]
