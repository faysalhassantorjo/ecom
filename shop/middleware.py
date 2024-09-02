from django.utils.deprecation import MiddlewareMixin
from .models import PageVisit
from django.urls import resolve

class PageVisitMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        # List of view names you want to track
        tracked_views = ['shop_details', 'home', 'products']

        # Get the name of the current view
        current_view_name = resolve(request.path).url_name

        if current_view_name in tracked_views and not request.user.is_superuser:
            url = request.path
            view_name = current_view_name
            request.session.save()
            session_key = request.session.session_key

            # Use get_or_create to find or create a PageVisit entry
            page_visit, created = PageVisit.objects.get_or_create(
                url=url,
                session_address=session_key,  # Match based on URL and session address
                defaults={'view_name': view_name, 'count': 0}
            )

            # Increment the visit count
            page_visit.count += 1
            page_visit.save()

        return None
