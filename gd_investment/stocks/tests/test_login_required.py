from django.test import TestCase, Client
from django.db import connection
from django.contrib.auth import get_user_model
from django.urls import reverse

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

class LoginRequiredTest(TestCase):
    """Test that views are only accessible by logged in users
    """
    @classmethod
    def setUpTestData(cls):
        """Create a test user
        """
        User = get_user_model()
        cls.test_user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpassword')

    def check_redirect_if_not_logged_in(self, view_name):
        """For a given view name, check that the view redirects to the login page if the user is not logged in
        """
        url = reverse(view_name)
        response = self.client.get(url)
        self.assertRedirects(response, '/login/?next=' + url)

    def check_view_url_accessible_by_name(self, view_name):
        """For a given view name, check that the view is accessible by a logged in user
        """
        self.client.login(username='testuser', password='testpassword')
        url = reverse(view_name)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

# Views to test
view_names = ['profile', 'stocks-list', 'stocks-evolution', 'stocks-analysis', 'api-key-generate']

# Loop through the views and create a test for each
for view_name in view_names:
    def redirect_test(self, view_name=view_name):
        self.check_redirect_if_not_logged_in(view_name)
    setattr(LoginRequiredTest, 'test_redirect_if_not_logged_in_{}'.format(view_name), redirect_test)

    def accessible_test(self, view_name=view_name):
        self.check_view_url_accessible_by_name(view_name)
    setattr(LoginRequiredTest, 'test_view_url_accessible_by_name_{}'.format(view_name), accessible_test)