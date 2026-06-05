import pytest
from datetime import date, timedelta
from django.utils import timezone
from rest_framework.test import APIClient

from airport.models import Airport
from booking.models import Booking
from booking_status.models import BookingStatus
from cabin_class.models import CabinClass
from city.models import City
from flight.models import Flight
from order.models import Order
from order_status.models import OrderStatus
from passenger.models import Passenger
from payment.models import Payment
from payment_status.models import PaymentStatus
from seat.models import Seat
from user.models import User


@pytest.fixture(autouse=True)
def use_locmem_cache(settings):
    settings.CACHES = {
        "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}
    }


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username='testuser',
        email='user@test.com',
        password='password',
        role='user',
        phone_number='+11234567890',
    )


@pytest.fixture
def other_user(db):
    return User.objects.create_user(
        username='otheruser',
        email='other@test.com',
        password='password',
        role='user',
        phone_number='+19876543210',
    )


@pytest.fixture
def admin(db):
    return User.objects.create_user(
        username='adminuser',
        email='admin@test.com',
        password='password',
        role='admin',
        phone_number='+10000000000',
    )


@pytest.fixture
def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def other_auth_client(api_client, other_user):
    client = APIClient()
    client.force_authenticate(user=other_user)
    return client


@pytest.fixture
def admin_client(admin):
    client = APIClient()
    client.force_authenticate(user=admin)
    return client


# --- Status fixtures ---

@pytest.fixture
def order_status_created(db):
    return OrderStatus.objects.create(code='CREATED', name='Created', description='Order created', is_terminal=False)


@pytest.fixture
def order_status_paid(db):
    return OrderStatus.objects.create(code='PAID', name='Paid', description='Order paid', is_terminal=False)


@pytest.fixture
def order_status_cancelled(db):
    return OrderStatus.objects.create(code='CANCELLED', name='Cancelled', description='Order cancelled', is_terminal=True)


@pytest.fixture
def order_status_refunded(db):
    return OrderStatus.objects.create(code='REFUNDED', name='Refunded', description='Order refunded', is_terminal=True)


@pytest.fixture
def order_status_failed(db):
    return OrderStatus.objects.create(code='FAILED', name='Failed', description='Order failed', is_terminal=True)


@pytest.fixture
def booking_status_pending(db):
    return BookingStatus.objects.create(code='PENDING', name='Pending', description='Awaiting payment', is_terminal=False)


@pytest.fixture
def booking_status_confirmed(db):
    return BookingStatus.objects.create(code='CONFIRMED', name='Confirmed', description='Payment confirmed', is_terminal=False)


@pytest.fixture
def booking_status_checked_in(db):
    return BookingStatus.objects.create(code='CHECKED_IN', name='Checked In', description='Passenger checked in', is_terminal=False)


@pytest.fixture
def booking_status_boarded(db):
    return BookingStatus.objects.create(code='BOARDED', name='Boarded', description='Passenger boarded', is_terminal=False)


@pytest.fixture
def booking_status_cancelled(db):
    return BookingStatus.objects.create(code='CANCELLED', name='Cancelled', description='Booking cancelled', is_terminal=True)


@pytest.fixture
def payment_status_paid(db):
    return PaymentStatus.objects.create(code='PAID', name='Paid', description='Payment successful', is_terminal=False)


@pytest.fixture
def payment_status_failed(db):
    return PaymentStatus.objects.create(code='FAILED', name='Failed', description='Payment failed', is_terminal=True)


@pytest.fixture
def payment_status_refunded(db):
    return PaymentStatus.objects.create(code='REFUNDED', name='Refunded', description='Payment refunded', is_terminal=True)


# --- Domain fixtures ---

@pytest.fixture
def city(db):
    return City.objects.create(name='Los Angeles', country='US', time_zone='America/Los_Angeles')


@pytest.fixture
def airport(db, city):
    return Airport.objects.create(airport_code='LAX', airport_name='LAX Airport', city=city)


@pytest.fixture
def arrival_airport(db, city):
    return Airport.objects.create(airport_code='JFK', airport_name='JFK Airport', city=city)


@pytest.fixture
def flight(db, airport, arrival_airport):
    return Flight.objects.create(
        departure_airport=airport,
        arrival_airport=arrival_airport,
        departure_date_time=timezone.now() + timedelta(days=7),
        arrival_date_time=timezone.now() + timedelta(days=7, hours=5),
    )


@pytest.fixture
def cabin_class(db):
    return CabinClass.objects.create(cabin_class_name='Economy', baggage_allowance=23, refundable=False)


@pytest.fixture
def seat(db, flight, cabin_class):
    return Seat.objects.create(flight=flight, cabin_class=cabin_class, row_number=1, seat_letter='A', occupied=False)


@pytest.fixture
def seat2(db, flight, cabin_class):
    return Seat.objects.create(flight=flight, cabin_class=cabin_class, row_number=1, seat_letter='B', occupied=False)


@pytest.fixture
def passenger2(db):
    return Passenger.objects.create(
        first_name='Jane',
        last_name='Doe',
        date_of_birth=date(1992, 6, 15),
        passport_number='B98765432',
    )


@pytest.fixture
def passenger(db):
    return Passenger.objects.create(
        first_name='John',
        last_name='Smith',
        date_of_birth=date(1990, 1, 1),
        passport_number='A12345678',
    )


@pytest.fixture
def order(db, user, order_status_created):
    return Order.objects.create(
        user=user,
        order_status=order_status_created,
        total_amount='500.00',
        confirmation_number='ABC123',
    )


@pytest.fixture
def paid_order(db, user, order_status_paid):
    return Order.objects.create(
        user=user,
        order_status=order_status_paid,
        total_amount='500.00',
        confirmation_number='PAID01',
    )


@pytest.fixture
def cancelled_order(db, user, order_status_cancelled):
    return Order.objects.create(
        user=user,
        order_status=order_status_cancelled,
        total_amount='500.00',
        confirmation_number='CAN001',
    )


@pytest.fixture
def booking(db, order, flight, passenger, seat, booking_status_pending):
    return Booking.objects.create(
        order=order,
        flight=flight,
        passenger=passenger,
        seat=seat,
        booking_status=booking_status_pending,
    )


@pytest.fixture
def confirmed_booking(db, paid_order, flight, passenger, seat, booking_status_confirmed):
    return Booking.objects.create(
        order=paid_order,
        flight=flight,
        passenger=passenger,
        seat=seat,
        booking_status=booking_status_confirmed,
    )


@pytest.fixture
def payment(db, paid_order, payment_status_paid):
    return Payment.objects.create(
        order=paid_order,
        amount='500.00',
        stripe_payment_session_id='pi_test_123',
        payment_status=payment_status_paid,
    )
