from django.core.management.base import BaseCommand
from refund_request.models import RefundRequest
from booking.models import Booking
from payment.models import Payment
from order.models import Order
from cart.models import Cart
from seat.models import Seat
from fare.models import Fare
from flight.models import Flight
from airport.models import Airport
from passenger.models import Passenger
from user.models import User
from city.models import City
from cabin_class.models import CabinClass
from booking_status.models import BookingStatus
from order_status.models import OrderStatus
from payment_status.models import PaymentStatus


class Command(BaseCommand):
    help = 'Clear all data from the database'

    def handle(self, *args, **options):
        RefundRequest.objects.all().delete()
        Booking.objects.all().delete()
        Payment.objects.all().delete()
        Cart.objects.all().delete()
        Order.objects.all().delete()
        Seat.objects.all().delete()
        Fare.objects.all().delete()
        Flight.objects.all().delete()
        Airport.objects.all().delete()
        Passenger.objects.all().delete()
        User.objects.all().delete()
        City.objects.all().delete()
        CabinClass.objects.all().delete()
        BookingStatus.objects.all().delete()
        OrderStatus.objects.all().delete()
        PaymentStatus.objects.all().delete()

        self.stdout.write(self.style.SUCCESS('Database cleared.'))
