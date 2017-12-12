"""
WSGI config for pricegen project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/
"""

import os
import sys

activate_this = os.path.join(os.path.dirname(__file__), '..', '..', 'ENV', 'bin', 'activate_this.py')
if os.path.exists(activate_this):
    # python 2: execfile(activate_this, dict(__file__=activate_this))
    exec(open(activate_this).read(), dict(__file__=activate_this))

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pricegen.settings")

application = get_wsgi_application()
