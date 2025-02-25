from django.core.management.base import BaseCommand
from django.db import transaction
from ...models import Vessel
import threading


class Command(BaseCommand):
    help = "Simulate condition when withdrawing refrigerant from a vessel."

    def handle(self, *args, **kwargs):
        Vessel.objects.create(name="Test Vessel", content=50.0)
        self.stdout.write("Simulating condition...")
        self.run_simulation()

    def run_simulation(self):
        barrier = threading.Barrier(2)

        def withdraw_refrigerant(user, amount):
            with transaction.atomic():
                barrier.wait()
                vessel = Vessel.objects.select_for_update().get(id=1)
                if vessel.content < amount:
                    self.stderr.write(f"{user}: Not enough refrigerant!")
                    return
                vessel.content -= amount
                vessel.save()
                self.stdout.write(f"{user}: Withdrawn {amount} kg")

        def user1():
            withdraw_refrigerant('user1', 10.0)

        def user2():
            withdraw_refrigerant('user2', 10.0)


        t1 = threading.Thread(target=user1)
        t2 = threading.Thread(target=user2)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        vessel = Vessel.objects.get(id=1)
        self.stdout.write(f"Remaining content: {vessel.content} kg")
