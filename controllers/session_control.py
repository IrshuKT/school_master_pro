from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class SessionDestroyController(http.Controller):

    @http.route('/web/session/destroy', type='http', auth='user', methods=['POST'], csrf=False)
    def destroy_session(self, **kwargs):
        """Destroy user session when browser closes"""
        try:
            _logger.info(f"Destroying session for user: {request.env.user.name}")

            # Invalidate the current session
            request.session.logout(keep_db=True)

            # Clear session data
            request.session.rotate = False

            _logger.info("Session destroyed successfully")
            return http.Response("Session destroyed", status=200)

        except Exception as e:
            _logger.error(f"Error destroying session: {str(e)}")
            return http.Response("Error destroying session", status=500)