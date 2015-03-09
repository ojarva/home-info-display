from django.http import HttpResponseRedirect

class SpecialAuthenticationMiddleware(object):

    def process_request(self, request):
        ip = request.META["REMOTE_ADDR"]
        if ip.startswith("192.168.1.") or ip == "127.0.0.1":
            # Do not request authentication if IP is in LAN, or localhost
            return None
        if request.user.is_authenticated():
            # Do nothing if user is already authenticated
            return None
        full_path = request.get_full_path()
        if full_path.startswith("/homecontroller/admin/login/"):
            # Do nothing if user is in authentication form
            return None
        # Request authentication
        return HttpResponseRedirect("/homecontroller/admin/login/?next=%s" % full_path)
