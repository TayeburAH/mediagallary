from django.urls import path, reverse
from . import views

urlpatterns = [
    path('', views.galleries, name='galleries'),
    path('picture_gallery/<int:category_id>/', views.pictures, name='picture_gallery'),
    path('add/', views.create, name='create_gallery'),

    path('test/', views.test, name='test'),

    path('update-category/<int:category_id>/', views.update_category, name='update_category'),
    path('update-image/<int:pic_id>/', views.update_image, name='update_image'),
    path('download/<int:pic_id>/', views.download, name='download_image'),
    path('search/', views.search, name='search'),
    path('trash/', views.trash, name='trash'),
    path('delete-permanent/<int:pic_id>/', views.delete_permanent, name='delete_permanent'),

]
