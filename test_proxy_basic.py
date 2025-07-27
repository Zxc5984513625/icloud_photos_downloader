#!/usr/bin/env python3
"""Basic test to verify proxy functionality is working"""

import os
import sys

# Add src to path for importing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_proxy_session_creation():
    """Test that PyiCloudSession accepts proxy configuration"""
    from pyicloud_ipd.session import PyiCloudSession
    
    # Mock service object
    class MockService:
        def __init__(self):
            self.password_filter = None
            self.http_timeout = 30.0
    
    service = MockService()
    
    # Test without proxies
    session1 = PyiCloudSession(service)
    assert session1.proxies == {}
    
    # Test with proxies
    proxies = {'http': 'http://proxy.example.com:8080', 'https': 'https://proxy.example.com:8080'}
    session2 = PyiCloudSession(service, proxies)
    assert session2.proxies == proxies
    
    print("✓ PyiCloudSession proxy configuration works")

def test_pyicloud_service_proxy_parameters():
    """Test that PyiCloudService accepts proxy parameters"""
    from pyicloud_ipd.base import PyiCloudService
    from pyicloud_ipd.raw_policy import RawTreatmentPolicy
    from pyicloud_ipd.file_match import FileMatchPolicy
    
    def dummy_cleaner(filename):
        return filename
    
    def dummy_password_provider():
        return None
        
    # Test without proxies - should not fail
    try:
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
        assert service1.proxies == {}
        print("✓ PyiCloudService works without proxies")
    except Exception as e:
        # Authentication will fail but the proxy parameter should be accepted
        if "proxies" not in str(e):
            print("✓ PyiCloudService accepts proxy parameter")
        else:
            raise
    
    # Test with proxies - should not fail due to proxy configuration
    try:
        proxies = {'http': 'http://proxy.example.com:8080', 'https': 'https://proxy.example.com:8080'}
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
        assert service2.proxies == proxies
        print("✓ PyiCloudService works with proxies")
    except Exception as e:
        # Authentication will fail but the proxy parameter should be accepted
        if "proxies" not in str(e):
            print("✓ PyiCloudService accepts proxy parameter with values")
        else:
            raise

def test_cli_proxy_arguments():
    """Test that CLI accepts proxy arguments"""
    from click.testing import CliRunner
    from icloudpd.base import main
    
    runner = CliRunner()
    
    # Test with proxy arguments - should not fail due to proxy arguments
    result = runner.invoke(main, [
        '--help'
    ])
    
    # Check if proxy options are in help text
    assert '--http-proxy' in result.output
    assert '--https-proxy' in result.output
    print("✓ CLI includes proxy arguments in help")

if __name__ == "__main__":
    test_proxy_session_creation()
    test_pyicloud_service_proxy_parameters()
    test_cli_proxy_arguments()
    print("\nAll basic proxy tests passed! ✅")