from django.urls import path
from bag import views


urlpatterns = [
    path('', views.view_bag, name='view_bag')
]
