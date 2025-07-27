# Proxy Support in icloud_photos_downloader

This document describes the proxy support feature that has been added to icloud_photos_downloader.

## Overview

The icloud_photos_downloader now supports HTTP and HTTPS proxies for all network requests to Apple's iCloud services. This is useful in corporate environments or situations where network traffic must go through a proxy server.

## Command Line Options

Two new command line options have been added:

- `--http-proxy <proxy_url>`: Specifies the HTTP proxy to use for requests
- `--https-proxy <proxy_url>`: Specifies the HTTPS proxy to use for requests

## Usage Examples

### Using HTTP Proxy Only
```bash
icloudpd --http-proxy http://proxy.example.com:8080 \
         --username user@example.com \
         --password mypassword \
         --directory ~/Photos
```

### Using HTTPS Proxy Only
```bash
icloudpd --https-proxy https://proxy.example.com:8080 \
         --username user@example.com \
         --password mypassword \
         --directory ~/Photos
```

### Using Both HTTP and HTTPS Proxies
```bash
icloudpd --http-proxy http://proxy.example.com:8080 \
         --https-proxy https://secure-proxy.example.com:8080 \
         --username user@example.com \
         --password mypassword \
         --directory ~/Photos
```

### Authentication with Proxy
```bash
icloudpd --http-proxy http://user:pass@proxy.example.com:8080 \
         --https-proxy https://user:pass@secure-proxy.example.com:8080 \
         --username user@example.com \
         --auth-only
```

### No Proxy (Default Behavior)
```bash
# This works exactly as before - no proxy configuration
icloudpd --username user@example.com \
         --password mypassword \
         --directory ~/Photos
```

## Proxy URL Format

Proxy URLs should follow the standard format:
- `http://proxy.example.com:8080` - Basic HTTP proxy
- `https://proxy.example.com:8080` - Basic HTTPS proxy  
- `http://username:password@proxy.example.com:8080` - HTTP proxy with authentication
- `https://username:password@proxy.example.com:8080` - HTTPS proxy with authentication

## Implementation Details

### Technical Architecture

The proxy support is implemented at the requests session level:

1. **PyiCloudSession**: The `PyiCloudSession` class (which extends `requests.Session`) now accepts an optional `proxies` parameter in its constructor
2. **PyiCloudService**: The `PyiCloudService` class accepts an optional `proxies` parameter and passes it to the session
3. **CLI Integration**: The main CLI command accepts `--http-proxy` and `--https-proxy` arguments and constructs a proxies dictionary
4. **Authentication Flow**: The authenticator function passes proxy settings through to the PyiCloudService

### Backward Compatibility

The implementation maintains full backward compatibility:
- All proxy parameters are optional with default values of `None`
- When no proxy is specified, the behavior is identical to previous versions
- Existing scripts and configurations continue to work without modification

### Error Handling

- Invalid proxy URLs will result in standard requests library error messages
- Connection failures through proxies will be reported as connection errors
- Authentication failures with proxy servers will be handled by the requests library

## Testing

The proxy functionality has been tested with:
- ✅ Basic proxy parameter acceptance and configuration
- ✅ CLI argument parsing and help text
- ✅ Session proxy configuration
- ✅ Authentication flow proxy passing
- ✅ Backward compatibility (no proxy specified)
- ✅ Integration testing with mocked network requests

## Security Considerations

- Proxy URLs containing credentials will be passed to the requests library securely
- No proxy credentials are logged or stored by icloud_photos_downloader
- Standard HTTPS encryption applies between the client and HTTPS proxies
- Corporate proxy certificates should be properly configured in the system certificate store

## Troubleshooting

### Common Issues

1. **Proxy Connection Refused**
   ```
   Cannot connect to Apple iCloud service
   ```
   - Verify proxy URL is correct
   - Check that proxy server is running and accessible
   - Verify firewall rules allow connections to proxy

2. **Authentication Required**
   ```
   407 Proxy Authentication Required
   ```
   - Include username and password in proxy URL: `http://user:pass@proxy.example.com:8080`
   - Verify proxy credentials are correct

3. **Certificate Issues**
   ```
   SSL certificate verification failed
   ```
   - Configure system certificate store to trust corporate proxy certificates
   - For testing only: some proxy setups may require certificate configuration

### Debug Information

To get more detailed information about proxy usage, enable debug logging:
```bash
icloudpd --log-level debug \
         --http-proxy http://proxy.example.com:8080 \
         --username user@example.com \
         --auth-only
```

## Future Enhancements

Potential future improvements could include:
- Support for SOCKS proxies
- Proxy auto-configuration (PAC) file support
- Per-service proxy configuration
- Proxy health checking and failover

## Contributing

If you encounter issues with proxy support or have suggestions for improvements, please:
1. Check existing issues on GitHub
2. Create a new issue with detailed information about your proxy setup
3. Include debug logs (with sensitive information redacted)
4. Specify your operating system and Python version