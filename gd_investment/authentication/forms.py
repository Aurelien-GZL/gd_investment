from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.core.exceptions import ValidationError
from django import forms
from .models import User
from .validators import contains_letter, contains_number, contains_special_character


# Profil parent form
#------------------------------
class BaseProfileForm(forms.ModelForm):
    """
    Parent form class for signing up and modifying profil
    """
    class Meta:
        """
        Meta data for the form
        """
        # Define model associated to the form
        model = User
        # Define fields included in the form
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
            'profile_picture',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize labels for the form fields
        self.fields['username'].label = 'Identifiant'
        self.fields['first_name'].label = 'Prénom'
        self.fields['last_name'].label = 'Nom'
        self.fields['email'].label = 'Email'
        # Customize help text for the form fields
        self.fields['username'].help_text = 'Renseignez un identifiant unique contanant: \
            \n - Une lettre'
        self.fields['email'].help_text = 'Renseignez une adresse e-mail valide'
        # Customize validators for the form fields
        self.fields['username'].validators.append(contains_letter)
        # Set profile_picture field parameters           
        if 'profile_picture' in self.fields:
            self.fields['profile_picture'].required = False
        # Surcharge password1 parameters using fake password field     
        if 'password' in self.fields:
            self.fields['password'].required = False
            self.fields['password1'].help_text = 'Votre mot de passe doit contenir: \
                    \n - Au minimum 10 caractères \
                    \n - Une lettre \
                    \n - Un chiffre'
            self.fields['password1'].validators.append(contains_letter)
            self.fields['password1'].validators.append(contains_number)
            self.fields['password1'].validators.append(contains_special_character)

    def clean_username(self):
        """
        Custom validation to ensure username is unique.
        """
        username = self.cleaned_data['username']
        users_with_different_username = User.objects.filter(username=username).exclude(username=self.instance.username)
        if users_with_different_username.exists():
            raise forms.ValidationError('Un compte existe déjà pour cet identifiant')
        return username

    def clean_email(self):
        """
        Custom validation to ensure e-mail is unique.
        """
        email = self.cleaned_data['email']
        users_with_different_email = User.objects.filter(email__iexact=email).exclude(username=self.instance.username)
        if users_with_different_email.exists():
            raise forms.ValidationError('Un compte existe déjà pour cet e-mail')
        return email


# Sign up form
#------------------------------
class ProfileForm(UserCreationForm, BaseProfileForm):
    """
    Form to register on the website
    """
    class Meta(UserCreationForm.Meta, BaseProfileForm.Meta):
        """
        Meta data for the form
        """
        # Define model associated to the form
        model = User
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
            'password'
        ]


# Change profile form
#------------------------------
class ChangeProfileForm(BaseProfileForm):
    class Meta(BaseProfileForm.Meta):
        """
        Meta data for the form
        """
        # Define model associated to the form
        model = User
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
            'profile_picture',
        ]
        

# Form to change password
# ------------------------------
class ChangePasswordForm(PasswordChangeForm):
    """
    Form to change password
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Surcharge new_password1 parameter     
        self.fields['new_password1'].help_text = 'Votre mot de passe doit contenir: \
                \n - Au minimum 10 caractères \
                \n - Une lettre \
                \n - Un chiffre'
        self.fields['new_password1'].validators.append(contains_letter)
        self.fields['new_password1'].validators.append(contains_number)
        self.fields['new_password1'].validators.append(contains_special_character)

    def clean_old_password(self):
        """
        Validate that the old password is correct.
        """
        old_password = self.cleaned_data.get("old_password")

        if not self.user.check_password(old_password):
            raise ValidationError("Votre ancien mot de passe est incorrect.")

        return old_password
    
    class Meta:
        # Define model associated to the form
        model = User
        fields = [
            'old_password',
            'new_password1',
            'new_password2'
            ]


# Form to login as user
#------------------------------
class LoginForm(forms.Form):
    """
    Form to login
    """
    username = forms.CharField(max_length=50, label="Identifiant")
    password = forms.CharField(
        max_length=50, widget=forms.PasswordInput, label="Mot de passe")


# Form for email to reset password
#------------------------------
class CustomPasswordResetForm(PasswordResetForm):
    """
    From for password recovery e-mail
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Customize labels for the form fields
        self.fields['email'].label = 'Email'


# Form for email to set new password
#------------------------------
class CustomPasswordResetConfirmForm(SetPasswordForm):
    """
    Form to define new password
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Surcharge new_password1 parameter     
        self.fields['new_password1'].help_text = 'Votre mot de passe doit contenir: \
                \n - Au minimum 10 caractères \
                \n - Une lettre \
                \n - Un chiffre'
        self.fields['new_password1'].validators.append(contains_letter)
        self.fields['new_password1'].validators.append(contains_number)
        self.fields['new_password1'].validators.append(contains_special_character)