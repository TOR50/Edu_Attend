from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views as core_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Custom admin and core views first
    path('', core_views.home, name='home'),

    # Accounts
    path('accounts/login/', auth_views.LoginView.as_view(authentication_form=core_views.CustomLoginForm), name='login'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/', core_views.signup, name='signup'),
    path('accounts/login-success/', core_views.login_success, name='login_success'),
    path('accounts/logout/get/', core_views.logout_get, name='logout_get'),

    # Core
    path('core/', include('core.urls')),

    # Django admin (keep last to avoid shadowing)
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
