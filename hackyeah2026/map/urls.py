from django.urls import path

from . import views

app_name = "map"
urlpatterns = [
    path("", views.map_view, name="index"),
    path("api/roads/", views.roads_geojson, name="roads_geojson"),
    path("api/geojson/", views.roads_geojson, name="geojson"),
    path("api/details/", views.details_geojson, name="details_geojson"),
    path("pois/", views.pois_view, name="pois"),
    path("api/pois/", views.pois_geojson, name="pois_geojson"),
    path("route/", views.route_view, name="route"),
    path("api/route/", views.route_api, name="route_api"),
]
