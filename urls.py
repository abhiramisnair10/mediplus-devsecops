from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Main website pages
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('index/', views.index, name='index'),
    path('services/', views.services, name='services'),
    path('contact/', views.contact, name='contact'),
    path('user_register/', views.user_register, name='user_register')
    path('login/', views.login, name='login'),

    # Admin and user application URLs
    path('', include('admin_app.urls')),
    path('', include('user_app.urls')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )