from api.models import CarnotTable
from django.core.management.base import BaseCommand
import os
import pathlib


class Command(BaseCommand):
    help = "Ingest csv data to postgres database"

    def handle(self, *args, **options):
        BASE_DIR = os.path.join(
            pathlib.Path(__file__).parent.resolve().parent.resolve(), "data"
        )
        print(BASE_DIR)
        print(f"Total row count before ingestion: {CarnotTable.objects.all().count()}")
        print("Loading CSV data")
        buffer = []
        row_count = 0
        inserted_batch = 0
        MAX_VALUES = 99
        with open(f"{BASE_DIR}/raw_data.csv") as feed:
            next(feed)
            for row in feed:
                device_id, latitude, longitude, time_stamp, sts, speed = row.split(",")
                print(
                    device_id,
                    latitude,
                    longitude,
                    time_stamp,
                    sts,
                    speed.replace("\n", ""),
                )
                carnottable = CarnotTable()
                carnottable.device_fk_id = device_id
                carnottable.latitude = latitude
                carnottable.longitude = longitude
                carnottable.time_stamp = time_stamp
                carnottable.sts = sts
                carnottable.speed = speed.replace("\n", "")
                # carnottable.save()
                buffer.append(carnottable)
                row_count += 1
                print(f"row_count: {row_count}")
                if len(buffer) >= MAX_VALUES:
                    CarnotTable.objects.bulk_create(buffer)
                    buffer = []
                    inserted_batch += 1
                    print(f"inserted_batch: {inserted_batch}")
