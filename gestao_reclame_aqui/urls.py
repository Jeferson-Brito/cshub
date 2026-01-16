"""
URL configuration for gestao_reclame_aqui project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
import re

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
]

# Serve media files both in development and production
# In production, consider using a cloud storage solution like S3 for better performance
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # Em desenvolvimento, Django serve automaticamente de STATICFILES_DIRS
    pass
