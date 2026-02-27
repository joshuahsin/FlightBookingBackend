# your_app/management/commands/seed.py

from django.core.management.base import BaseCommand
from airport.models import Airport  # replace with your model
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
        los_angeles = City.objects.create(name="Los Angeles", country="United States", time_zone="America/Los_Angeles")
        new_york = City.objects.create(name="New York", country="United States", time_zone="America/New_York")
        portland = City.objects.create(name="Portland", country="United States", time_zone="America/Los_Angeles")
        denver = City.objects.create(name="Denver", country="United States", time_zone="America/Denver")

        #AIRPORTS
        lax = Airport.objects.create(airport_code="LAX", airport_name="Los Angeles International Airport", city=los_angeles)
        lga = Airport.objects.create(airport_code="LGA", airport_name="Laguardia Airport", city=new_york)
        pdx = Airport.objects.create(airport_code="PDX", airport_name = "Portland International Airport", city=portland)
        den = Airport.objects.create(airport_code="DEN", airport_name = "Denver International Airport", city=denver)
        print(Airport.objects.get_queryset())

        #FLIGHTS
        lga_to_lax = Flight.objects.create(departure_airport=lga, arrival_airport=lax, departure_date_time="2026-01-16T15:30:00-05:00", arrival_date_time="2026-01-16T18:30:00-08:00")
        den_to_pdx = Flight.objects.create(departure_airport=den, arrival_airport=pdx, departure_date_time="2026-01-16T13:30:00-06:00", arrival_date_time="2026-01-16T15:30:00-05:00")
        pdx_to_den = Flight.objects.create(departure_airport=pdx, arrival_airport=den, departure_date_time="2026-01-18T17:30:00-05:00", arrival_date_time="2026-01-18T19:30:00-06:00")
        print(Flight.objects.get_queryset())

        #CABIN_CLASS
        eco = CabinClass.objects.create(cabin_class_name="Economy", baggage_allowance=1, refundable=False)
        prem_eco = CabinClass.objects.create(cabin_class_name="Premium Economy", baggage_allowance=2, refundable=True)
        bus = CabinClass.objects.create(cabin_class_name="Business", baggage_allowance=3, refundable=True)
        print(CabinClass.objects.get_queryset())

        #FARE
        Fare.objects.create(flight=lga_to_lax, cabin_class=eco, fare_price=200, seats_available=70)
        Fare.objects.create(flight=lga_to_lax, cabin_class=prem_eco, fare_price=300, seats_available=30)
        Fare.objects.create(flight=lga_to_lax, cabin_class=bus, fare_price=500, seats_available=10)

        Fare.objects.create(flight=den_to_pdx, cabin_class=eco, fare_price=150, seats_available=70)
        Fare.objects.create(flight=den_to_pdx, cabin_class=prem_eco, fare_price=250, seats_available=30)
        bus_den_to_pdx_fare = Fare.objects.create(flight=den_to_pdx, cabin_class=bus, fare_price=450, seats_available=10)
        bus_pdx_to_den_fare = Fare.objects.create(flight=pdx_to_den, cabin_class=bus, fare_price=500, seats_available=10)
        print(Fare.objects.get_queryset())

        #USER
        josh = User.objects.create_user(username="josh1234", password="awejgopejds", role="user", first_name="Joshua", last_name="Hsin", email="jhsin1@uci.edu", phone_number="+19112345679", preferred_contact_method="email")
        george = User.objects.create_user(username="george123",password="uhiugyufyu", role="user", first_name="George", last_name="Hsin", email="georgehsin@gmail.com", phone_number="+19117355678", preferred_contact_method="text")
        john = User.objects.create_user(username="john321", password="joiwejgoijwaes", role="user", first_name="John", last_name="Paul", email="johnpaul@hotmail.com", phone_number="+19112345673", preferred_contact_method="email")
        User.objects.create_user(username="admin", password="admin", role="admin", first_name="admin", last_name="admin", email="admin@gmail.com")
        print(User.objects.get_queryset())

        #BOOKING STATUS
        BookingStatus.objects.create(code="CONFIRMED", name="Confirmed", description="Confirmed booking", is_terminal=False)
        ticketed = BookingStatus.objects.create(code="TICKETED", name="Ticketed", description="Ticket given to user", is_terminal=False)
        checked_in = BookingStatus.objects.create(code="CHECKED_IN", name="Checked in", description="Passenger checked in", is_terminal=False)
        BookingStatus.objects.create(code="BOARDING", name="Boarding", description="Plane Boarding Time", is_terminal=False)
        BookingStatus.objects.create(code="IN_FLIGHT", name="Flying", description="Plane is en route", is_terminal=False)
        #BookingStatus.objects.create(code="SCHEDULE_CHANGE", name="Schedule Change", description="Plane departure and/or landing time changed", is_terminal=False)
        #BookingStatus.objects.create(code="REFUND_PENDING", name="Refund Pending", description="User requested refund", is_terminal=False)

        BookingStatus.objects.create(code="COMPLETED", name="Flight Completed", description="Flight completed successfully", is_terminal=True)
        BookingStatus.objects.create(code="NO_SHOW", name="No Show", description="Passenger did not board", is_terminal=True)
        BookingStatus.objects.create(code="CANCELLED", name="Cancelled", description="Flight was cancelled", is_terminal=True)
        print(BookingStatus.objects.get_queryset())

        #SEAT
        lga_eco_seat1 = Seat.objects.create(flight=lga_to_lax, cabin_class=eco, seat_number="15C", occupied=False)
        lga_eco_seat2 = Seat.objects.create(flight=lga_to_lax, cabin_class=eco, seat_number="15B", occupied=False)
        Seat.objects.create(flight=lga_to_lax, cabin_class=prem_eco, seat_number="10B", occupied=True)
        Seat.objects.create(flight=lga_to_lax, cabin_class=bus, seat_number="3B", occupied=True)

        den_eco_seat1 = Seat.objects.create(flight=den_to_pdx, cabin_class=eco, seat_number="20E", occupied=False)
        den_eco_seat2 = Seat.objects.create(flight=den_to_pdx, cabin_class=eco, seat_number="20D", occupied=False)
        Seat.objects.create(flight=den_to_pdx, cabin_class=prem_eco, seat_number="8C", occupied=True)
        Seat.objects.create(flight=den_to_pdx, cabin_class=bus, seat_number="2A", occupied=True)
        print(Seat.objects.get_queryset())

        #PASSENGER
        josh_passenger = Passenger.objects.create(first_name="Joshua", last_name="Hsin", date_of_birth="1972-04-22", passport_number="E1450384")
        george_passenger = Passenger.objects.create(first_name="George", last_name="Hsin", date_of_birth="1973-02-20", passport_number="E1450385")

        kevin_passenger = Passenger.objects.create(first_name="Kevin", last_name="Nguyen", date_of_birth="1994-06-15", passport_number="E1450386")
        kelly_passenger = Passenger.objects.create(first_name="Kelly", last_name="Tran", date_of_birth="1992-10-12", passport_number="E1450387")
        print(Passenger.objects.get_queryset())

        #ORDER_STATUS
        order_created = OrderStatus.objects.create(code="CREATED", name="Created", description="Created", is_terminal=False)
        order_paid = OrderStatus.objects.create(code="PAID", name="Paid", description="Paid", is_terminal=False)
        order_confirmed = OrderStatus.objects.create(code="CONFIRMED", name="Confirmed", description="Confirmed", is_terminal=False)

        order_failed = OrderStatus.objects.create(code="FAILED", name="Failed", description="Failed", is_terminal=True)
        order_cancelled = OrderStatus.objects.create(code="CANCELLED", name="Cancelled", description="Cancelled", is_terminal=True)
        order_refunded = OrderStatus.objects.create(code="REFUNDED", name="Refunded", description="Refunded", is_terminal=True)

        #ORDER
        #print(len("CONFIRMED"))
        josh_order = Order.objects.create(user=josh, order_status=order_confirmed, total_amount=536.43)
        george_order = Order.objects.create(user=george, order_status=order_confirmed, total_amount=846.34)
        #john_order = Order.objects.create(user_id=john, order_status="PROCESSING_PAYMENT", total_amount=734.04)
        print(Order.objects.get_queryset())

        #BOOKING
        Booking.objects.create(order=josh_order, flight=den_to_pdx, user=josh, passenger=josh_passenger, seat=den_eco_seat1, confirmation_number="A12F35", booking_status=checked_in)
        Booking.objects.create(order=josh_order, flight=den_to_pdx, user=josh, passenger=kelly_passenger, seat=den_eco_seat2, confirmation_number="A12F36", booking_status=checked_in)

        Booking.objects.create(order=george_order, flight=lga_to_lax, user=george, passenger=george_passenger, seat=lga_eco_seat1, confirmation_number="A12F37", booking_status=ticketed)
        Booking.objects.create(order=george_order, flight=lga_to_lax, user=george, passenger=kevin_passenger, seat=lga_eco_seat2, confirmation_number="A12F38", booking_status=ticketed)
        print(Booking.objects.get_queryset())

        #PAYMENT STATUS
        PaymentStatus.objects.create(code="PENDING", name="Pending", description="Payment Processing", is_terminal=False)
        complete_payment = PaymentStatus.objects.create(code="COMPLETED", name="Completed", description="Payment Completed Successfully", is_terminal=False)
        PaymentStatus.objects.create(code="FAILED", name="Failed", description="Payment Failed", is_terminal=True)
        PaymentStatus.objects.create(code="REFUNDED", name="Refunded", description="Payment Refunded", is_terminal=True)

        #PAYMENT
        Payment.objects.create(order=josh_order, amount=536.43, payment_method="CREDIT", payment_status=complete_payment, payment_date_time="2026-01-16T12:30:00-08:00")
        Payment.objects.create(order=george_order, amount=846.34, payment_method="PAYPAL", payment_status=complete_payment, payment_date_time="2026-01-16T15:25:33-08:00")
        #Payment.objects.create(order_id=john_order, amount=734.04, payment_method="DEBIT", payment_status="PROCESSING")
        print(Payment.objects.get_queryset())

        #CART
        john_cart = Cart.objects.create(user=john, is_active=True, departure_flight=den_to_pdx, return_flight=pdx_to_den, departure_fare=bus_den_to_pdx_fare, return_fare=bus_pdx_to_den_fare)
        print(Cart.objects.get_queryset())

        #CART ITEM
        #CartItem.objects.create(cart=john_cart, flight=den_to_pdx, fare=bus_den_to_pdx_fare)
        #print(CartItem.objects.get_queryset())

        print("Successfully created all objects!")