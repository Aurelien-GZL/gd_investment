"""
URL configuration for gd_investment project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.contrib.auth import views as auth_views
from django.urls import path, include
import stocks.views
import authentication.views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('__debug__/', include('debug_toolbar.urls')),
    # Stocks app paths
    #------------------------------
    path('', stocks.views.home, name='index'),
    path('stocks/', stocks.views.stocks_list, name='stocks-list'),
    path('stocks/price/', stocks.views.stocks_evolution, name='stocks-evolution'),
    path('stocks/analysis/', stocks.views.stocks_analysis, name='stocks-analysis'),
    # Authenticate app paths
    #------------------------------
    path('login/', authentication.views.LoginPage.as_view(), name='login'),
    path('logout/', authentication.views.logout_user, name='logout'),
    path('signup/', authentication.views.signup_page, name='signup'),
    path('profile/', authentication.views.profile, name='profile'),
    # Reset password
    #------------------------------
    path(
        'resetpassword/',
        authentication.views.CustomPasswordResetView.as_view(template_name="authentication/password_reset.html"),
        name="password_reset"
    ),
    path(
        'resetpassword_sent/',
        auth_views.PasswordResetDoneView.as_view(template_name="authentication/password_reset_done.html"),
        name="password_reset_done"
    ),
    path(
        'reset/<uidb64>/<token>', # uidb64: user encoded in base 64 / token to check the password is valid
        authentication.views.CustomPasswordResetConfirmView.as_view(template_name="authentication/password_reset_confirm.html"),
        name="password_reset_confirm"
    ),
    path(
        'resetpassword_complete/',
        auth_views.PasswordResetCompleteView.as_view(template_name="authentication/password_reset_complete.html"),
        name="password_reset_complete"
    ),
    # API
    #------------------------------
    path('api-key/', stocks.views.generate_api_key, name='api-key-generate'),
    path('api/dailytrade/', stocks.views.get_api_dailytrade, name='api-dailytrade'),
    path('api/dailytrade/request', stocks.views.api_daily_form, name='api-dailytrade-request')
]
