from django.urls import path
from .views import *

urlpatterns=[
    path('dashboard',dashboard,name='dashboard'),
    path('tickets/',ticket_list, name='ticket_list'),
    path('tickets/create/',create_ticket, name='create_ticket'),
    path('tickets/<int:pk>/',ticket_detail, name='ticket_detail'),
    path('tickets/<int:pk>/update/',update_ticket, name='update_ticket'),
    

    path('',login_view,name='home'),
    
    path('login',login_view,name='login'),
    path('logout/',logout_view,name='logout'),
    path('register/',register_view,name='register'),
]