from django.urls import path

from . import views

urlpatterns = [
    path('orders', views.OrderGenericAPIView.as_view()),
    path('orders/<str:pk>', views.OrderGenericAPIView.as_view()),
    path('export', views.ExportAPIView.as_view()),
    path('chart', views.ChartAPIView.as_view()),
]
