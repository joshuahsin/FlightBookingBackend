"""
Custom SMTP backend that can disable SSL certificate verification (dev only).
Use when Python cannot verify the SMTP server cert (e.g. macOS python.org install).
Set EMAIL_SSL_VERIFY=false in .env to use this.
"""
import ssl
from django.core.mail.backends.smtp import EmailBackend as SMTPBackend
from django.utils.functional import cached_property


class EmailBackend(SMTPBackend):
    """SMTP backend that uses an unverified SSL context when requested (dev only)."""

    @cached_property
    def ssl_context(self):
        import os
        if os.environ.get('EMAIL_SSL_VERIFY', 'true').lower() == 'false':
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            return ctx
        return ssl.create_default_context()
