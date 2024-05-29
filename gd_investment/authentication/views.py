from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from authentication import forms
from authentication.models import User, ApiKey


# Login page view
#------------------------------
# View for login page using provided username and password to authenticate
class LoginPage(View):
    # Common attributes definition
    form_class = forms.LoginForm
    template_name = 'authentication/login.html'
    
    # GET request management
    def get(self, request):
        form = self.form_class()
        message = ''
        return render(
            request,
            self.template_name,
            context={
                'form': form,
                'message': message
            }
        )
    
    # POST request management    
    def post(self, request):
        form = self.form_class(request.POST)
        message = ''
        if form.is_valid():
            # Django authenticate method taking username and password to send back corresponding user
            # Return None otherwise
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
                )
            if user is not None:
                # Django login function to connect with user 
                login(request, user)
                return redirect('index')
            else:
                message = 'Identifiants invalides'
            return render(
                request,
                self.template_name,
                context={
                    'form': form,
                    'message': message
                }
            )


# View for disconnection
#------------------------------
def logout_user(request):
    # Django function to disconnect 
    logout(request)
    # Django redirect function to send back user at a specific app location after connection
    return redirect('login')


# View for sign-up page /!\ Mot2passe! for tests
#------------------------------
def signup_page(request):
    form = forms.ProfileForm()
    success_message = None
    
    # Delete any existing success messages
    storage = messages.get_messages(request)
    storage.used = True
    
    # If request is post and form is valid, save user
    if request.method == 'POST':
        form = forms.ProfileForm(request.POST)
        if form.is_valid():
            # Save user if form is correctly fulfilled
            user = form.save()
            # Display success message
            user_name = form.cleaned_data.get('username')
            success_message = user_name + ' votre compte a été créé avec succès.'
            messages.success(request, success_message )
            # Set a flag in the session to indicate success
            request.session['signup_success'] = True
            # Connect automatically user after signing up
            login(request, user)
            return redirect('index')
    # Else return the signup page
    else:
        return render(
            request,
            'authentication/signup.html',
            context={
                'form':form,
            }
        )
    # This line should only be reached if the form is not valid
    # It will display the issue
    return render(
        request,
        'authentication/signup.html',
        context={'form': form}
    )
   
    
# Profile page
#------------------------------
# # Decorator to restric access to the view  to register user only
@login_required
def profile(request):
    success_message = None
    user = request.user
    user_profile = get_object_or_404(User, id=user.id)
    
    change_form = forms.ChangeProfileForm(instance=user_profile)
    password_form = forms.ChangePasswordForm(user)
    
    if request.method == 'POST':

        # Logic for user profile change
        if 'update_profile' in request.POST:
            change_form = forms.ChangeProfileForm(request.POST, request.FILES, instance=user_profile)
            if change_form.is_valid():
                user = change_form.save()
                # Display success message
                user_name = change_form.cleaned_data.get('username')
                success_message = user_name + ' votre compte a été mis à jour.'
                messages.success(request, success_message)
                # Update the session to prevent the user from being logged out
                update_session_auth_hash(request, user)

        # Logic for password change
        elif 'change_password' in request.POST:
            password_form = forms.ChangePasswordForm(user, request.POST)
            if password_form.is_valid():
                password_form.save()     
                # Display success message
                user_name = user.username
                success_message = user_name + ' votre mot de passe a été mis à jour.'
                messages.success(request, success_message )
                # Update the session to prevent the user from being logged out
                update_session_auth_hash(request, user)  

        # Logic for account deletion
        elif 'delete_account' in request.POST:
            user.delete()
            logout(request)
            return redirect('index')

            

    return render(
        request,
        'authentication/profile.html',
        # Send back the user in the context to have it updated
        context={
            'change_form': change_form,
            'password_form': password_form,
            'user':user,
            'success_message': success_message
            }
    )


# Reset password
#------------------------------
class CustomPasswordResetView(PasswordResetView):
    form_class = forms.CustomPasswordResetForm


# Set new password
#------------------------------
class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = forms.CustomPasswordResetConfirmForm


# Authentication through custom API key
#------------------------------
class ApiKeyAuthentication(BaseAuthentication):
    """
    Define authentication for API through custom API key extending BaseAuthentification
    """
    def authenticate(self, request):
        # Extract API key from the bearer
        api_key = request.headers.get('Authorization', '').split('Bearer ')[-1]
        if not api_key:
            return None

        # Retreive corresponding ApiKey object from database in tuple form (user, none) if api key is valid
        try:
            api_key_obj = ApiKey.objects.get(key=api_key)
        except ApiKey.DoesNotExist:
            raise AuthenticationFailed('Clé API incorrecte')

        return (api_key_obj.user, None)
