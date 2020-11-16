from django.contrib import admin
from django.urls import path, include
from rest_framework.documentation import include_docs_urls
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
                  path('', admin.site.urls),
                  path('docs/', include_docs_urls(title='API de Documentação')),
                  path('controle_nps/', include('app_controle_nps.urls')),
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
