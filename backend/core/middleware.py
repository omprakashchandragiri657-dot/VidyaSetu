from django.utils.deprecation import MiddlewareMixin


class TenantMiddleware(MiddlewareMixin):
    """
    Middleware to handle multi-tenancy by setting the current college
    on the request object based on the authenticated user.
    """
    
    def process_request(self, request):
        """Set the current college on the request object"""
        request.current_college = None
        
        if hasattr(request, 'user') and request.user.is_authenticated:
            request.current_college = request.user.college
