from django.test import TestCase
from authentication.forms import ProfileForm
from authentication.models import User

class ProfileFormTest(TestCase):
    def test_form_valid(self):
        """Test the form is valid with correct data
        """
        form_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': 'Testpassword123!',
            'password2': 'Testpassword123!',
        }
        form = ProfileForm(data=form_data)
        self.assertTrue(form.is_valid())
