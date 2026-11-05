from django.urls import path
from .import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns =[
     path('owner-register/', views.owner_register, name='owner_register'),
     path('owner_login/', views.owner_login, name='owner_login'),

 # Dashboard
    path(
        "owner-dashboard/",
        views.owner_dashboard,
        name="owner_dashboard"
    ),
     path('size/add/', views.add_size, name='add_size'),
    path('size/edit/<int:id>/', views.edit_size, name='edit_size'),
    path('size/delete/<int:id>/', views.delete_size, name='delete_size'),
     path('logout/', views.owner_logout, name='owner_logout'),
    
path('colour/add/', views.add_colour, name='add_colour'),
path('colour/edit/<int:id>/', views.edit_colour, name='edit_colour'),
path('colour/delete/<int:id>/', views.delete_colour, name='delete_colour'),

     path('add-category/', views.add_category, name='add_category'),
    #  path('edit-category/<int:id>/', views.edit_category, name='edit_category'),
    #  path('delete-category/<int:id>/', views.delete_category, name='delete_category'),


path(
    'edit-category/<int:id>/',
    views.edit_category,
    name='edit_category'
),

path(
    'delete-category/<int:id>/',
    views.delete_category,
    name='delete_category'
),


path('add-product/', views.add_product, name='add_product'),

path('edit-product/<int:id>/', views.edit_product, name='edit_product'),

path('delete-product/<int:id>/', views.delete_product, name='delete_product'),


    path("billing/<int:order_id>/", views.billing_page,name="billing_page"),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

path(
    'dashboard/',
    views.owner_dashboard,
    name='owner_dashboard'
),



