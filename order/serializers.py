from django.db import transaction
from rest_framework import serializers

from booking.models import Booking
from booking_status.models import BookingStatus
from flight.models import Flight
from order.models import Order
from order_status.models import OrderStatus
from order_status.serializers import OrderStatusEmbeddedSerializer
from passenger.models import Passenger
from seat.models import Seat
from user.models import User
from user.serializers import UserSerializer


class OrderBookingLineSerializer(serializers.Serializer):
    flight = serializers.PrimaryKeyRelatedField(queryset=Flight.objects.all())
    passenger = serializers.PrimaryKeyRelatedField(queryset=Passenger.objects.all())
    seat = serializers.PrimaryKeyRelatedField(queryset=Seat.objects.all())
    booking_status = serializers.PrimaryKeyRelatedField(
        queryset=BookingStatus.objects.all(),
        required=False,
        allow_null=True,
    )
    fare_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default='0.00')


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
    )
    order_status = serializers.PrimaryKeyRelatedField(
        queryset=OrderStatus.objects.all()
    )
    bookings = OrderBookingLineSerializer(many=True, write_only=True, required=False)

    class Meta:
        model = Order
        fields = [
            'id',
            'user',
            'order_status',
            'total_amount',
            'confirmation_number',
            'created_at',
            'updated_at',
            'bookings',
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['user'] = UserSerializer(instance.user).data if instance.user else None
        data['order_status'] = (
            OrderStatusEmbeddedSerializer(instance.order_status).data
            if instance.order_status else None
        )
        return data

    @staticmethod
    def _default_booking_status():
        return (
            BookingStatus.objects.filter(code='CONFIRMED').first()
            or BookingStatus.objects.first()
        )

    @transaction.atomic
    def create(self, validated_data):
        print("VALIDATED DATA:", validated_data)
        bookings_data = validated_data.pop('bookings', None) or []
        order = Order.objects.create(**validated_data)
        default_status = self._default_booking_status()
        for line in bookings_data:
            print("LINE:", line)
            flight = line['flight']
            passenger = line['passenger']
            seat = line['seat']
            if seat.flight_id != flight.id:
                raise serializers.ValidationError(
                    {'bookings': f'Seat {seat.id} does not belong to flight {flight.id}.'}
                )
            booking_status = line.get('booking_status') or default_status
            if booking_status is None:
                raise serializers.ValidationError(
                    {'bookings': 'No booking_status provided and no default status in database.'}
                )
            print("BOOKING STATUS:", booking_status)
            Booking.objects.create(
                order=order,
                flight=flight,
                passenger=passenger,
                seat=seat,
                booking_status=booking_status,
                fare_price=line.get('fare_price', '0.00'),
            )
            Seat.objects.filter(pk=seat.pk).update(occupied=True)
        return order
