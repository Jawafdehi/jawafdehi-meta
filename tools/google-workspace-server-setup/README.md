# Google Workspace Server Setup

Nginx configuration for `google-auth-internal.jawafdehi.org` to reverse proxy to local port 40321.

## Status

✅ **Deployed and Active**
- Server: google-auth-internal.jawafdehi.org
- HTTPS: Enabled with Let's Encrypt SSL
- Certificate Expires: June 22, 2026
- Backend: localhost:40321

## Prerequisites

- Ubuntu server with root/sudo access
- Domain `google-auth-internal.jawafdehi.org` pointing to server IP
- Port 40321 running your application locally

## Quick Setup

```bash
# 1. Install nginx and certbot
sudo apt update
sudo apt install -y nginx certbot python3-certbot-nginx

# 2. Copy nginx configuration
sudo cp nginx.conf /etc/nginx/sites-available/google-auth-internal
sudo ln -s /etc/nginx/sites-available/google-auth-internal /etc/nginx/sites-enabled/

# 3. Remove default site (optional)
sudo rm -f /etc/nginx/sites-enabled/default

# 4. Test nginx configuration
sudo nginx -t

# 5. Restart nginx
sudo systemctl restart nginx

# 6. Obtain SSL certificate (certbot will auto-configure HTTPS)
sudo certbot --nginx -d google-auth-internal.jawafdehi.org
```

**Note**: The initial nginx configuration serves HTTP traffic. After running certbot, it will automatically configure HTTPS and set up HTTP→HTTPS redirects.

## Configuration Details

- HTTP (port 80) → Redirects to HTTPS (configured by certbot)
- HTTPS (port 443) → Reverse proxy to localhost:40321
- SSL certificates managed by Let's Encrypt/Certbot
- Auto-renewal configured via systemd timer

## Maintenance

### Renew SSL Certificate
```bash
sudo certbot renew --dry-run  # Test renewal
sudo certbot renew            # Actual renewal
```

Certificate auto-renewal is configured via systemd timer. Check status:
```bash
sudo systemctl status certbot.timer
```

### Check Nginx Status
```bash
sudo systemctl status nginx
sudo nginx -t  # Test configuration
```

### View Logs
```bash
sudo tail -f /var/log/nginx/google-auth-internal.access.log
sudo tail -f /var/log/nginx/google-auth-internal.error.log
```

## Troubleshooting

### Port 40321 not accessible
```bash
# Check if application is running
sudo netstat -tlnp | grep 40321
# or
sudo ss -tlnp | grep 40321
```

### Nginx won't start
```bash
# Check configuration syntax
sudo nginx -t

# Check error logs
sudo journalctl -u nginx -n 50
```

### SSL certificate issues
```bash
# Check certificate status
sudo certbot certificates

# Force renewal
sudo certbot renew --force-renewal
```

## Deployment

To deploy on a new server:

```bash
# Copy files to server
scp -r tools/google-workspace-server-setup/ ubuntu@<server-address>:~/

# SSH into server
ssh ubuntu@<server-address>

# Run setup
cd google-workspace-server-setup
sudo ./setup.sh

# Get SSL certificate
sudo certbot --nginx -d <your-domain>
```
