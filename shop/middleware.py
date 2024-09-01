# middleware.py
from django.utils.deprecation import MiddlewareMixin
from .models import PageVisit

class PageVisitMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        url = request.path
        view_name = view_func.__name__
        if not request.user.is_superuser:
            page_visit, created = PageVisit.objects.get_or_create(
                url=url,
                defaults={'view_name': view_name}
            )

        # Increment the visit count
            page_visit.count += 1
            page_visit.save()

        return None
