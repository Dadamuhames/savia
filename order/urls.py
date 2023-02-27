from django.urls import path, include
from . import views
# Create your views here.

urlpatterns = [
    path('order/create', views.OrderCreateView.as_view()),
    path('application/create', views.AplicationCreateView.as_view())
]
