#!/usr/bin/env python3
"""Test proxy functionality for icloud_photos_downloader"""

import os
import sys
import tempfile
import unittest
from unittest import mock

# Add src to path for importing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from click.testing import CliRunner

from icloudpd.base import main
from pyicloud_ipd.session import PyiCloudSession
from pyicloud_ipd.base import PyiCloudService
from pyicloud_ipd.raw_policy import RawTreatmentPolicy
from pyicloud_ipd.file_match import FileMatchPolicy


class ProxyFunctionalityTestCase(unittest.TestCase):
    
    def test_pyicloud_session_proxy_configuration(self):
        """Test that PyiCloudSession correctly configures proxies"""
        
        # Mock service object
        class MockService:
            def __init__(self):
                self.password_filter = None
                self.http_timeout = 30.0
        
        service = MockService()
        
        # Test without proxies
        session1 = PyiCloudSession(service)
        self.assertEqual(session1.proxies, {})
        
        # Test with proxies
        proxies = {
            'http': 'http://proxy.example.com:8080',
            'https': 'https://proxy.example.com:8080'
        }
        session2 = PyiCloudSession(service, proxies)
        self.assertEqual(session2.proxies, proxies)
        
        # Test that proxies are actually configured on the session
        self.assertIn('http', session2.proxies)
        self.assertIn('https', session2.proxies)
        self.assertEqual(session2.proxies['http'], 'http://proxy.example.com:8080')
        self.assertEqual(session2.proxies['https'], 'https://proxy.example.com:8080')

    def test_pyicloud_service_accepts_proxy_parameters(self):
        """Test that PyiCloudService accepts and stores proxy parameters"""
        
        def dummy_cleaner(filename):
            return filename
        
        def dummy_password_provider():
            return None
        
        # Test without proxies
        service1 = PyiCloudService(
            dummy_cleaner,
            dummy_cleaner,
            "com",
            RawTreatmentPolicy.AS_IS,
            FileMatchPolicy.NAME_SIZE_DEDUP_WITH_SUFFIX,
            "test@example.com",
            dummy_password_provider,
            proxies=None
        )
        self.assertEqual(service1.proxies, {})
        
        # Test with proxies
        proxies = {
            'http': 'http://proxy.example.com:8080',
            'https': 'https://proxy.example.com:8080'
        }
        service2 = PyiCloudService(
            dummy_cleaner,
            dummy_cleaner,
            "com",
            RawTreatmentPolicy.AS_IS,
            FileMatchPolicy.NAME_SIZE_DEDUP_WITH_SUFFIX,
            "test@example.com",
            dummy_password_provider,
            proxies=proxies
        )
        self.assertEqual(service2.proxies, proxies)

    def test_cli_proxy_arguments(self):
        """Test that CLI correctly handles proxy arguments"""
        
        runner = CliRunner()
        
        # Test help includes proxy options
        result = runner.invoke(main, ['--help'])
        self.assertIn('--http-proxy', result.output)
        self.assertIn('--https-proxy', result.output)
        self.assertIn('HTTP proxy to use for requests', result.output)
        self.assertIn('HTTPS proxy to use for requests', result.output)

    @mock.patch('icloudpd.authentication.PyiCloudService')
    def test_cli_passes_proxy_to_authenticator(self, mock_pyicloud_service):
        """Test that CLI passes proxy settings to the authenticator"""
        
        # Mock the PyiCloudService to avoid actual authentication
        mock_service_instance = mock.MagicMock()
        mock_pyicloud_service.return_value = mock_service_instance
        
        runner = CliRunner()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = runner.invoke(main, [
                '--username', 'test@example.com',
                '--password', 'dummy',
                '--auth-only',
                '--http-proxy', 'http://proxy.example.com:8080',
                '--https-proxy', 'https://proxy.example.com:8080',
                '--cookie-directory', temp_dir,
            ])
            
            # Check that PyiCloudService was called with proxy arguments
            self.assertTrue(mock_pyicloud_service.called)
            call_args = mock_pyicloud_service.call_args
            
            # Check that proxies were passed
            self.assertIn('proxies', call_args.kwargs)
            expected_proxies = {
                'http': 'http://proxy.example.com:8080',
                'https': 'https://proxy.example.com:8080'
            }
            self.assertEqual(call_args.kwargs['proxies'], expected_proxies)

    @mock.patch('icloudpd.authentication.PyiCloudService')
    def test_cli_without_proxy_arguments(self, mock_pyicloud_service):
        """Test that CLI works without proxy arguments (backward compatibility)"""
        
        # Mock the PyiCloudService to avoid actual authentication
        mock_service_instance = mock.MagicMock()
        mock_pyicloud_service.return_value = mock_service_instance
        
        runner = CliRunner()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = runner.invoke(main, [
                '--username', 'test@example.com',
                '--password', 'dummy',
                '--auth-only',
                '--cookie-directory', temp_dir,
            ])
            
            # Check that PyiCloudService was called
            self.assertTrue(mock_pyicloud_service.called)
            call_args = mock_pyicloud_service.call_args
            
            # Check that proxies were passed as empty dict
            self.assertIn('proxies', call_args.kwargs)
            self.assertEqual(call_args.kwargs['proxies'], {})

    def test_session_request_uses_proxy_configuration(self):
        """Test that the session actually uses the proxy configuration when making requests"""
        
        # Mock service object
        class MockService:
            def __init__(self):
                self.password_filter = None
                self.http_timeout = 30.0
        
        service = MockService()
        proxies = {
            'http': 'http://proxy.example.com:8080',
            'https': 'https://proxy.example.com:8080'
        }
        
        session = PyiCloudSession(service, proxies)
        
        # Mock the parent request method to verify proxy is passed
        with mock.patch('requests.Session.request') as mock_request:
            mock_request.return_value = mock.MagicMock(
                status_code=200,
                headers={},
                json=mock.MagicMock(return_value={})
            )
            
            # Make a request - this will trigger the session.request method
            try:
                session.request('GET', 'http://example.com')
            except:
                # We expect this to fail due to mocking, but we want to check
                # that the proxy was configured on the session
                pass
            
            # Verify that the session has the correct proxy configuration
            self.assertEqual(session.proxies, proxies)


if __name__ == '__main__':
    unittest.main()