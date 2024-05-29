from django.urls import reverse
from rest_framework.test import APITestCase
from decouple import config
from django.test import override_settings
from django.contrib.auth import get_user_model
from authentication.models import ApiKey
import uuid


class TestDailyTrade(APITestCase):
    """Test connection to the dailytrade API
    """
    def setUp(self):
        """Create a test user and log in
        """
        User = get_user_model()
        self.test_user = User.objects.create_user(username='testuser', email='testuser@email.com', password='Testpassword123!')
        self.api_key = ApiKey.objects.create(user=self.test_user, key=str(uuid.uuid4()))
        self.client.login(username='testuser', password='Testpassword123!')

    def test_get_api_dailytrade(self):
        """Test the connection to the dailytrade API and check response code is 200
        """
        url = reverse('api-dailytrade')
        response = self.client.get(url, HTTP_AUTHORIZATION=f'Bearer {self.api_key.key}')
        self.assertEqual(response.status_code, 200)