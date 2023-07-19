# Questions:
# 1. What type of datetime input will be passed in 3rd API.
# 2. Tuple as output not getting in 2nd API.
# 3.
from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from api.models import CarnotTable
from api.serializers import CarnotTableSerializers
from django.http import HttpResponse
from datetime import datetime
import redis
import json

cache = redis.Redis(host="localhost", port=6379, db=0)


def row_details(object):
    results = {}
    results["device_fk_id"] = object.device_fk_id
    results["latitude"] = object.latitude
    results["longitude"] = object.longitude
    results["time_stamp"] = str(object.time_stamp)
    results["sts"] = str(object.sts)
    results["speed"] = object.speed
    return results


def ingest_id_and_latest_time_to_redis():
    distinct_ids = CarnotTable.objects.distinct("device_fk_id")
    for ids in distinct_ids:
        unique_row = CarnotTable.objects.filter(device_fk_id=ids.device_fk_id).order_by(
            "-sts"
        )[0]

        cache_key = f"{unique_row.device_fk_id}-latest"
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            continue
        else:
            results = row_details(unique_row)
            cache.set(cache_key, json.dumps(results))

    pass


@api_view(["GET"])
def url_list(request):
    list = {
        "device_latest_detail_api": "api/details/<int:pk>",
        "example of device_latest_detail_api": "api/device_latest_detail_api/25029",
        "device_start_end_location": "api/device_start_end_location/<int:pk>",
        "example of device_start_end_location": "api/device_start_end_location/25029",
        "device_start_end_time_and_location": "api/device_start_end_time_and_location/<int:pk>/<str:starttime>/<str:endtime>",
        "example of device_start_end_time_and_location": "api/device_start_end_time_and_location/25029/2021-10-23T14:07:50.67886Z/2021-10-23T14:08:08.5984Z",
    }
    return Response(list)


@api_view(["GET"])
def device_latest_detail_api(request, pk):
    ingest_id_and_latest_time_to_redis()
    if CarnotTable.objects.filter(device_fk_id=pk).exists():
        cache_key = f"{pk}-latest"
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            data = json.loads(cached_data)
            return Response(data)
        else:
            data = CarnotTable.objects.filter(device_fk_id=pk).order_by("-sts")[0]
            result = row_details(data)
            cache.set(cache_key, json.dumps(result))
            serializer = CarnotTableSerializers(result, many=False)
            return Response(serializer.data)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(["GET"])
def device_start_end_location(request, pk):
    if CarnotTable.objects.filter(device_fk_id=pk).exists():
        start = CarnotTable.objects.filter(device_fk_id=pk).order_by("-sts")[0]
        end = CarnotTable.objects.filter(device_fk_id=pk).order_by("sts")[0]
        start_location = (start.latitude, start.longitude)
        end_location = (end.latitude, end.longitude)

        cache_key = f"{pk}-{start_location}-{end_location}"
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            data = json.loads(cached_data)
            return Response(data)
        else:
            result = {
                pk: {"start_location": start_location, "end_location": end_location}
            }
            cache.set(cache_key, json.dumps(result))
            return Response(result)
    else:
        Response(status=status.HTTP_404_NOT_FOUND)


@api_view(["GET"])
def device_start_end_time_and_location(request, pk, starttime, endtime):
    # starttime = 2021-10-23T14:07:50.67886Z
    # end_time = 2021-10-23T14:08:08.5984Z
    if CarnotTable.objects.filter(device_fk_id=pk).exists():
        start_time = datetime.strptime(starttime, "%Y-%m-%dT%H:%M:%S.%fZ")
        end_time = datetime.strptime(endtime, "%Y-%m-%dT%H:%M:%S.%fZ")
        data = CarnotTable.objects.filter(
            device_fk_id=pk, sts__gte=start_time, sts__lte=end_time
        )
        results = {}
        result_list = []
        for row in data:
            results["latitude"] = row.latitude
            results["longitude"] = row.longitude
            results["sts"] = row.sts
            result_list.append(results)
        return Response(result_list)
    else:
        Response(status=status.HTTP_404_NOT_FOUND)
