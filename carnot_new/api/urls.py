from django.urls import path
from api.views import (
    url_list,
    device_latest_detail_api,
    device_start_end_location,
    device_start_end_time_and_location,
)

urlpatterns = [
    path("", url_list, name="list of all api's"),
    path(
        "device_latest_detail_api/<int:pk>",
        device_latest_detail_api,
        name="device_detail",
    ),
    path(
        "device_start_end_location/<int:pk>",
        device_start_end_location,
        name="device_start_end_location",
    ),
    path(
        "device_start_end_time_and_location/<int:pk>/<str:starttime>/<str:endtime>",
        device_start_end_time_and_location,
        name="device_start_end_time_and_location",
    ),
]
