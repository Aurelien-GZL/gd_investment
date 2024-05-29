from django.test.runner import DiscoverRunner

class NoDbTestRunner(DiscoverRunner):
    """Indicate that the tests do not require to create and delete a database
    """
    def setup_databases(self, **kwargs):
        pass

    def teardown_databases(self, old_config, **kwargs):
        pass