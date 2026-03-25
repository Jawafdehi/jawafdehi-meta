#!/bin/bash
# Setup script for google-auth-internal.jawafdehi.org nginx configuration

set -e

DOMAIN="google-auth-internal.jawafdehi.org"
NGINX_CONF="/etc/nginx/sites-available/google-auth-internal"
NGINX_ENABLED="/etc/nginx/sites-enabled/google-auth-internal"

echo "=== Google Workspace Server Setup ==="
echo "Domain: $DOMAIN"
echo "Target: localhost:40321"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
    exit 1
fi

# Install nginx and certbot
echo "Installing nginx and certbot..."
apt update
apt install -y nginx certbot python3-certbot-nginx

# Copy nginx configuration
echo "Copying nginx configuration..."
cp nginx.conf "$NGINX_CONF"

# Enable site
echo "Enabling site..."
ln -sf "$NGINX_CONF" "$NGINX_ENABLED"

# Remove default site if exists
if [ -f /etc/nginx/sites-enabled/default ]; then
    echo "Removing default nginx site..."
    rm /etc/nginx/sites-enabled/default
fi

# Test nginx configuration
echo "Testing nginx configuration..."
nginx -t

# Start nginx
echo "Starting nginx..."
systemctl enable nginx
systemctl restart nginx

echo ""
echo "=== Nginx installed and configured ==="
echo ""
echo "Next steps:"
echo "1. Ensure your application is running on localhost:40321"
echo "   Test with: curl http://localhost:40321"
echo ""
echo "2. Ensure DNS for $DOMAIN points to this server"
echo "   Test with: dig $DOMAIN"
echo ""
echo "3. Run the following command to obtain SSL certificate:"
echo ""
echo "   sudo certbot --nginx -d $DOMAIN"
echo ""
echo "4. Certbot will automatically:"
echo "   - Obtain SSL certificate from Let's Encrypt"
echo "   - Configure HTTPS in nginx"
echo "   - Set up HTTP to HTTPS redirect"
echo ""
echo "After SSL setup, your site will be available at:"
echo "   https://$DOMAIN"
echo ""
