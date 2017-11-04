from django.conf.urls import url
from image_store import views

app_name = 'image_store'

urlpatterns = [

    # usage: store/get/
    url(r'^get/$', views.Imagesall.as_view(),name='list'),

    # usage: store/get/[image-name]/
    url(r'^get/(?P<img_name>(.*))/$', views.Oneimage.as_view(),name='add'),


]

