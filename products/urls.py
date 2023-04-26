from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path('products', views.ProductGenericAPIView.as_view()),
    path('products/<str:pk>', views.ProductGenericAPIView.as_view()),
    path('upload', views.FileUploadView.as_view())

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # <-- set up static path.
