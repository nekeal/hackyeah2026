from django.urls import path

from . import views

app_name = "map"
urlpatterns = [
    path("", views.map_view, name="index"),
    path("api/roads/", views.roads_geojson, name="roads_geojson"),
]
