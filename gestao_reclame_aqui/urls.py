"""
URL configuration for gestao_reclame_aqui project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Em desenvolvimento, Django serve automaticamente de STATICFILES_DIRS
    # Não precisa adicionar manualmente para STATIC_URL


