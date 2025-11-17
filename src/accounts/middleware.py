import logging
from typing import Callable
from django.shortcuts import redirect
from django.urls import resolve, Resolver404

logger = logging.getLogger(__name__)

class LoginRequiredMiddleware:
    """Require authentication for non-public paths.

    Public access is granted when any of these are true:
      * Exact path match in PUBLIC_EXACT_PATHS
      * Path starts with one of PUBLIC_PREFIXES
      * Resolved url_name is in PUBLIC_VIEW_NAMES
    Otherwise unauthenticated users are redirected to the combined login/register page.
    """

    PUBLIC_EXACT_PATHS = {
        '/',
        '/login/',
        '/login/submit/',
        '/register/submit/',
        '/accounts/login/',
        '/accounts/login/submit/',
        '/accounts/register/submit/',
    }

    PUBLIC_PREFIXES = (
        '/static/',
        '/media/',
        '/admin/',
    )

    PUBLIC_VIEW_NAMES = {
        'home',
        'login_register',
        'login_user',
        'register_user',
    }

    def __init__(self, get_response: Callable):
        self.get_response = get_response
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('[LoginRequiredMiddleware] %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.DEBUG)

    def _path_public(self, path: str) -> bool:
        """Fast path checks: exact match or prefix."""
        if path in self.PUBLIC_EXACT_PATHS:
            return True
        return any(path.startswith(pref) for pref in self.PUBLIC_PREFIXES)

    def _view_name_public(self, path: str) -> bool:
        """Resolve and compare url_name; resolver failures are non-public."""
        try:
            match = resolve(path)
            return match.url_name in self.PUBLIC_VIEW_NAMES
        except Resolver404:
            return False

    def is_public(self, path: str) -> bool:
        return self._path_public(path) or self._view_name_public(path)

    def __call__(self, request):  # pragma: no cover - entry still exercised via tests
        path = request.path
        is_auth = request.user.is_authenticated
        logger.debug("Request path=%s is_authenticated=%s", path, is_auth)

        if self.is_public(path):
            logger.debug("Allowed: public path")
            return self.get_response(request)
        if is_auth:
            logger.debug("Allowed: authenticated")
            return self.get_response(request)
        logger.debug("Redirecting to login page")
        return redirect('login_register')

