# your_app/management/commands/seed.py

from django.core.management.base import BaseCommand
from airport.models import Airport
from booking.models import Booking
from booking_status.models import BookingStatus
from cabin_class.models import CabinClass
from cart.models import Cart
from flight.models import Flight
from fare.models import Fare
from order.models import Order
from order_status.models import OrderStatus
from passenger.models import Passenger
from payment.models import Payment
from payment_status.models import PaymentStatus
from seat.models import Seat
from user.models import User
from city.models import City


class Command(BaseCommand):
    def handle(self, *args, **options):
        #CITIES
        los_angeles, _ = City.objects.get_or_create(name="Los Angeles", country="United States", defaults={"time_zone": "America/Los_Angeles"})
        new_york, _ = City.objects.get_or_create(name="New York", country="United States", defaults={"time_zone": "America/New_York"})
        portland, _ = City.objects.get_or_create(name="Portland", country="United States", defaults={"time_zone": "America/Los_Angeles"})
        denver, _ = City.objects.get_or_create(name="Denver", country="United States", defaults={"time_zone": "America/Denver"})

        #AIRPORTS
        lax, _ = Airport.objects.get_or_create(airport_code="LAX", defaults={"airport_name": "Los Angeles International Airport", "city": los_angeles})
        lga, _ = Airport.objects.get_or_create(airport_code="LGA", defaults={"airport_name": "Laguardia Airport", "city": new_york})
        pdx, _ = Airport.objects.get_or_create(airport_code="PDX", defaults={"airport_name": "Portland International Airport", "city": portland})
        den, _ = Airport.objects.get_or_create(airport_code="DEN", defaults={"airport_name": "Denver International Airport", "city": denver})

        #CABIN CLASS
        eco, _ = CabinClass.objects.get_or_create(cabin_class_name="Economy", defaults={"baggage_allowance": 1, "refundable": False})
        prem_eco, _ = CabinClass.objects.get_or_create(cabin_class_name="Premium Economy", defaults={"baggage_allowance": 2, "refundable": True})
        bus, _ = CabinClass.objects.get_or_create(cabin_class_name="Business", defaults={"baggage_allowance": 3, "refundable": True})

        #FLIGHTS
        lga_to_lax, _ = Flight.objects.get_or_create(departure_airport=lga, arrival_airport=lax, departure_date_time="2026-01-16T15:30:00-05:00", defaults={"arrival_date_time": "2026-01-16T18:30:00-08:00"})
        lax_to_lga, _ = Flight.objects.get_or_create(departure_airport=lax, arrival_airport=lga, departure_date_time="2026-01-19T20:30:00-08:00", defaults={"arrival_date_time": "2026-01-19T23:30:00-05:00"})
        den_to_pdx, _ = Flight.objects.get_or_create(departure_airport=den, arrival_airport=pdx, departure_date_time="2026-01-16T13:30:00-06:00", defaults={"arrival_date_time": "2026-01-16T15:30:00-05:00"})
        pdx_to_den, _ = Flight.objects.get_or_create(departure_airport=pdx, arrival_airport=den, departure_date_time="2026-01-18T17:30:00-05:00", defaults={"arrival_date_time": "2026-01-18T19:30:00-06:00"})

        #FARE
        Fare.objects.get_or_create(flight=lga_to_lax, cabin_class=eco, defaults={"fare_price": 200, "seats_available": 70})
        Fare.objects.get_or_create(flight=lga_to_lax, cabin_class=prem_eco, defaults={"fare_price": 300, "seats_available": 30})
        Fare.objects.get_or_create(flight=lga_to_lax, cabin_class=bus, defaults={"fare_price": 500, "seats_available": 10})
        Fare.objects.get_or_create(flight=den_to_pdx, cabin_class=eco, defaults={"fare_price": 150, "seats_available": 70})
        Fare.objects.get_or_create(flight=den_to_pdx, cabin_class=prem_eco, defaults={"fare_price": 250, "seats_available": 30})
        bus_den_to_pdx_fare, _ = Fare.objects.get_or_create(flight=den_to_pdx, cabin_class=bus, defaults={"fare_price": 450, "seats_available": 10})
        bus_pdx_to_den_fare, _ = Fare.objects.get_or_create(flight=pdx_to_den, cabin_class=bus, defaults={"fare_price": 500, "seats_available": 10})

        #BOOKING STATUS
        BookingStatus.objects.get_or_create(code="PENDING", defaults={"name": "Pending", "description": "Booking is pending confirmation", "is_terminal": False})
        confirmed, _ = BookingStatus.objects.get_or_create(code="CONFIRMED", defaults={"name": "Confirmed", "description": "Confirmed booking", "is_terminal": False})
        checked_in, _ = BookingStatus.objects.get_or_create(code="CHECKED_IN", defaults={"name": "Checked in", "description": "Passenger checked in", "is_terminal": False})
        BookingStatus.objects.get_or_create(code="BOARDED", defaults={"name": "Boarded", "description": "Plane Boarding Time", "is_terminal": False})
        BookingStatus.objects.get_or_create(code="COMPLETED", defaults={"name": "Flight Completed", "description": "Flight completed successfully", "is_terminal": True})
        BookingStatus.objects.get_or_create(code="CANCELLED", defaults={"name": "Cancelled", "description": "Flight was cancelled", "is_terminal": True})
        BookingStatus.objects.get_or_create(code="REFUNDED", defaults={"name": "Refunded", "description": "Booking was refunded", "is_terminal": True})
        BookingStatus.objects.get_or_create(code="NO_SHOW", defaults={"name": "No Show", "description": "Passenger did not board", "is_terminal": True})

        #ORDER STATUS
        order_created, _ = OrderStatus.objects.get_or_create(code="CREATED", defaults={"name": "Created", "description": "Created", "is_terminal": False})
        order_paid, _ = OrderStatus.objects.get_or_create(code="PAID", defaults={"name": "Paid", "description": "Paid", "is_terminal": False})
        OrderStatus.objects.get_or_create(code="FAILED", defaults={"name": "Failed", "description": "Failed", "is_terminal": True})
        order_cancelled, _ = OrderStatus.objects.get_or_create(code="CANCELLED", defaults={"name": "Cancelled", "description": "Cancelled", "is_terminal": True})
        OrderStatus.objects.get_or_create(code="PARTIALLY_REFUNDED", defaults={"name": "Partially Refunded", "description": "Partially Refunded", "is_terminal": True})
        OrderStatus.objects.get_or_create(code="REFUNDED", defaults={"name": "Refunded", "description": "Refunded", "is_terminal": True})

        #PAYMENT STATUS
        PaymentStatus.objects.get_or_create(code="PENDING", defaults={"name": "Pending", "description": "Payment Processing", "is_terminal": False})
        complete_payment, _ = PaymentStatus.objects.get_or_create(code="COMPLETED", defaults={"name": "Completed", "description": "Payment Completed Successfully", "is_terminal": False})
        PaymentStatus.objects.get_or_create(code="FAILED", defaults={"name": "Failed", "description": "Payment Failed", "is_terminal": True})
        PaymentStatus.objects.get_or_create(code="REFUNDED", defaults={"name": "Refunded", "description": "Payment Refunded", "is_terminal": True})

        #USER
        josh, _ = User.objects.get_or_create(username="josh1234", defaults={"password": "awejgopejds", "role": "user", "first_name": "Joshua", "last_name": "Hsin", "email": "jhsin1@uci.edu", "phone_number": "+19112345679", "preferred_contact_method": "email"})
        george, _ = User.objects.get_or_create(username="george123", defaults={"password": "uhiugyufyu", "role": "user", "first_name": "George", "last_name": "Hsin", "email": "georgehsin@gmail.com", "phone_number": "+19117355678", "preferred_contact_method": "text"})
        john, _ = User.objects.get_or_create(username="john321", defaults={"password": "joiwejgoijwaes", "role": "user", "first_name": "John", "last_name": "Paul", "email": "johnpaul@hotmail.com", "phone_number": "+19112345673", "preferred_contact_method": "email"})
        User.objects.get_or_create(username="admin", defaults={"password": "admin", "role": "admin", "first_name": "admin", "last_name": "admin", "email": "admin@gmail.com"})

        #PASSENGER
        josh_passenger, _ = Passenger.objects.get_or_create(first_name="Joshua", last_name="Hsin", date_of_birth="1972-04-22", defaults={"passport_number": "E1450384"})
        george_passenger, _ = Passenger.objects.get_or_create(first_name="George", last_name="Hsin", date_of_birth="1973-02-20", defaults={"passport_number": "E1450385"})
        kevin_passenger, _ = Passenger.objects.get_or_create(first_name="Kevin", last_name="Nguyen", date_of_birth="1994-06-15", defaults={"passport_number": "E1450386"})
        kelly_passenger, _ = Passenger.objects.get_or_create(first_name="Kelly", last_name="Tran", date_of_birth="1992-10-12", defaults={"passport_number": "E1450387"})

        #SEAT
        for row in range(1, 4):
            for letter in ['A', 'B', 'C', 'D', 'E', 'F']:
                Seat.objects.get_or_create(flight=lga_to_lax, row_number=row, seat_letter=letter, defaults={"cabin_class": bus, "occupied": False})
        for row in range(4, 8):
            for letter in ['A', 'B', 'C', 'D', 'E', 'F']:
                Seat.objects.get_or_create(flight=lga_to_lax, row_number=row, seat_letter=letter, defaults={"cabin_class": prem_eco, "occupied": False})
        for row in range(8, 22):
            for letter in ['A', 'B', 'C', 'D', 'E', 'F']:
                Seat.objects.get_or_create(flight=lga_to_lax, row_number=row, seat_letter=letter, defaults={"cabin_class": eco, "occupied": False})

        for row in range(1, 4):
            for letter in ['A', 'B', 'C', 'D', 'E', 'F']:
                Seat.objects.get_or_create(flight=lax_to_lga, row_number=row, seat_letter=letter, defaults={"cabin_class": bus, "occupied": False})
        for row in range(4, 8):
            for letter in ['A', 'B', 'C', 'D', 'E', 'F']:
                Seat.objects.get_or_create(flight=lax_to_lga, row_number=row, seat_letter=letter, defaults={"cabin_class": prem_eco, "occupied": False})
        for row in range(8, 21):
            for letter in ['A', 'B', 'C', 'D', 'E', 'F']:
                Seat.objects.get_or_create(flight=lax_to_lga, row_number=row, seat_letter=letter, defaults={"cabin_class": eco, "occupied": False})

        den_eco_seat1, _ = Seat.objects.get_or_create(flight=den_to_pdx, row_number=20, seat_letter="E", defaults={"cabin_class": eco, "occupied": False})
        den_eco_seat2, _ = Seat.objects.get_or_create(flight=den_to_pdx, row_number=20, seat_letter="D", defaults={"cabin_class": eco, "occupied": False})
        Seat.objects.get_or_create(flight=den_to_pdx, row_number=8, seat_letter="C", defaults={"cabin_class": prem_eco, "occupied": True})
        Seat.objects.get_or_create(flight=den_to_pdx, row_number=2, seat_letter="A", defaults={"cabin_class": bus, "occupied": True})

        lga_eco_seat1, _ = Seat.objects.get_or_create(flight=lga_to_lax, row_number=21, seat_letter="C", defaults={"cabin_class": eco, "occupied": False})
        lga_eco_seat2, _ = Seat.objects.get_or_create(flight=lga_to_lax, row_number=21, seat_letter="B", defaults={"cabin_class": eco, "occupied": False})

        #ORDER
        josh_order, _ = Order.objects.get_or_create(confirmation_number="JOSH01", defaults={"user": josh, "order_status": order_paid, "total_amount": 536.43})
        george_order, _ = Order.objects.get_or_create(confirmation_number="GEO01", defaults={"user": george, "order_status": order_paid, "total_amount": 846.34})

        #BOOKING
        Booking.objects.get_or_create(order=josh_order, flight=den_to_pdx, passenger=josh_passenger, defaults={"seat": den_eco_seat1, "booking_status": checked_in})
        Booking.objects.get_or_create(order=josh_order, flight=den_to_pdx, passenger=kelly_passenger, defaults={"seat": den_eco_seat2, "booking_status": checked_in})
        Booking.objects.get_or_create(order=george_order, flight=lga_to_lax, passenger=george_passenger, defaults={"seat": lga_eco_seat1, "booking_status": confirmed})
        Booking.objects.get_or_create(order=george_order, flight=lga_to_lax, passenger=kevin_passenger, defaults={"seat": lga_eco_seat2, "booking_status": confirmed})

        #PAYMENT
        Payment.objects.get_or_create(stripe_payment_session_id="cs_test_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6", defaults={"order": josh_order, "amount": 536.43, "payment_status": complete_payment})
        Payment.objects.get_or_create(stripe_payment_session_id="cs_test_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z7", defaults={"order": george_order, "amount": 846.34, "payment_status": complete_payment})

        #CART
        Cart.objects.get_or_create(user=john, defaults={"is_active": True, "departure_flight": den_to_pdx, "return_flight": pdx_to_den, "departure_fare": bus_den_to_pdx_fare, "return_fare": bus_pdx_to_den_fare})

        print("Successfully seeded all objects!")
