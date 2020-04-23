from unittest import mock, TestCase

import django
import os

class TestManage(TestCase):

    @mock.patch('os.environ.setdefault')
    @mock.patch('django.core.wsgi.get_wsgi_application')
    # @mock.patch('audibene.wsgi.django.core.wsgi')
    def test_example(self, mock_get_wsgi_application, mock_setdefault):
        # Given

        # When
        import audibene.wsgi

        # Then
        mock_get_wsgi_application.assert_called_once()
        mock_setdefault.assert_called_once()
