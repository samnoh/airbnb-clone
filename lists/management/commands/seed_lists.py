import random
from django.core.management.base import BaseCommand
from django.contrib.admin.utils import flatten
from django_seed import Seed
from lists import models as list_models
from users import models as user_models
from rooms import models as room_models


class Command(BaseCommand):

    help = f"This command creates lists"

    def add_arguments(self, parser):
        parser.add_argument(
            "--number", type=int, default=1, help=f"How many lists you want to create"
        )

    def handle(self, *args, **options):
        number = options.get("number")
        seeder = Seed.seeder()
        users = user_models.User.objects.all()
        rooms = room_models.Room.objects.all()
        seeder.add_entity(
            list_models.List, number, {"user": lambda x: random.choice(users)}
        )
        created_pks = seeder.execute()
        flatten_pks = flatten(list(created_pks.values()))
        for pk in flatten_pks:
            list_model = list_models.List.objects.get(pk=pk)
            random_rooms = rooms[random.randint(0, 5) : random.randint(6, 20)]
            list_model.rooms.add(*random_rooms)

        self.stdout.write(self.style.SUCCESS(f"{number} lists created!"))
