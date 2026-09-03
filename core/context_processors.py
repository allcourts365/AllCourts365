from .models import SiteConfiguration

def site_config(request):
    try:
        config = SiteConfiguration.load()
    except Exception:
        config = None
    return {'site_config': config}
