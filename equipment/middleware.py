from .models import SecurityLog

class IPSecurityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')

        path = request.path
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        if not path.startswith('/static/') and not path.startswith('/media/'):
            try:
                SecurityLog.objects.create(
                    ip_address=ip,
                    attempted_path=path,
                    user_agent=user_agent,
                    is_blocked=False
                )
            except Exception:
                pass

        return self.get_response(request)
