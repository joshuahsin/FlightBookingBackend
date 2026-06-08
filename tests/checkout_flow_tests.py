import json
import pytest
from unittest.mock import patch, MagicMock
from django.urls import reverse


# ── Orders ────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestOrderCreate:
    def test_user_can_create_order(self, auth_client, order_status_created, user):
        response = auth_client.post('/api/order/', {
            'order_status': order_status_created.id,
            'total_amount': '300.00',
        })
        assert response.status_code == 201
        assert response.data['user']['id'] == user.id

    def test_admin_cannot_create_order(self, admin_client, order_status_created):
        response = admin_client.post('/api/order/', {
            'order_status': order_status_created.id,
            'total_amount': '300.00',
        })
        assert response.status_code == 403


@pytest.mark.django_db
class TestOrderList:
    def test_user_sees_own_orders(self, auth_client, order):
        response = auth_client.get('/api/order/')
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]['id'] == order.id

    def test_user_cannot_see_others_orders(self, other_auth_client, order):
        response = other_auth_client.get('/api/order/')
        assert response.status_code == 200
        assert len(response.data) == 0

    def test_admin_requires_filter(self, admin_client):
        response = admin_client.get('/api/order/')
        assert response.status_code == 400

    def test_admin_search_by_email(self, admin_client, order, user):
        response = admin_client.get(f'/api/order/?email={user.email}')
        assert response.status_code == 200
        assert any(o['id'] == order.id for o in response.data)

    def test_admin_search_by_confirmation_number(self, admin_client, order):
        response = admin_client.get(f'/api/order/?confirmation_number={order.confirmation_number}')
        assert response.status_code == 200
        assert response.data[0]['id'] == order.id

    def test_admin_search_no_match_returns_empty(self, admin_client):
        response = admin_client.get('/api/order/?email=nobody@test.com')
        assert response.status_code == 200
        assert len(response.data) == 0


@pytest.mark.django_db
class TestOrderCancel:
    def test_user_can_cancel_own_order(self, auth_client, order, order_status_cancelled, booking_status_cancelled):
        response = auth_client.post(f'/api/order/{order.id}/cancel/')
        assert response.status_code == 200
        order.refresh_from_db()
        assert order.order_status.code == 'CANCELLED'

    def test_cancel_cascades_to_bookings(self, auth_client, order, booking, flight, passenger2, seat2, booking_status_pending, order_status_cancelled, booking_status_cancelled):
        from booking.models import Booking
        booking2 = Booking.objects.create(order=order, flight=flight, passenger=passenger2, seat=seat2, booking_status=booking_status_pending)
        auth_client.post(f'/api/order/{order.id}/cancel/')
        booking.refresh_from_db()
        booking2.refresh_from_db()
        assert booking.booking_status.code == 'CANCELLED'
        assert booking2.booking_status.code == 'CANCELLED'

    def test_admin_cannot_cancel_order(self, admin_client, order):
        response = admin_client.post(f'/api/order/{order.id}/cancel/')
        assert response.status_code == 403

    def test_user_cannot_cancel_others_order(self, other_auth_client, order):
        response = other_auth_client.post(f'/api/order/{order.id}/cancel/')
        assert response.status_code == 403

    def test_cannot_cancel_terminal_order(self, auth_client, cancelled_order):
        response = auth_client.post(f'/api/order/{cancelled_order.id}/cancel/')
        assert response.status_code == 403


@pytest.mark.django_db
class TestRefundRequest:
    def test_user_can_submit_order_refund_request(self, auth_client, order):
        response = auth_client.post('/api/refund-request/', {'order': order.id, 'reason': 'changed plans'})
        assert response.status_code == 201
        assert response.data['status'] == 'PENDING'
        assert response.data['booking'] is None

    def test_user_can_submit_booking_refund_request(self, auth_client, order, booking):
        response = auth_client.post('/api/refund-request/', {'order': order.id, 'booking': booking.id})
        assert response.status_code == 201
        assert response.data['status'] == 'PENDING'
        assert response.data['booking'] == booking.id

    def test_duplicate_pending_request_rejected(self, auth_client, order):
        auth_client.post('/api/refund-request/', {'order': order.id})
        response = auth_client.post('/api/refund-request/', {'order': order.id})
        assert response.status_code == 403

    def test_admin_can_list_refund_requests(self, admin_client, auth_client, order):
        auth_client.post('/api/refund-request/', {'order': order.id})
        response = admin_client.get('/api/refund-request/')
        assert response.status_code == 200
        assert len(response.data) >= 1

    def test_admin_can_filter_by_status(self, admin_client, auth_client, order):
        auth_client.post('/api/refund-request/', {'order': order.id})
        response = admin_client.get('/api/refund-request/?status=PENDING')
        assert response.status_code == 200
        assert all(r['status'] == 'PENDING' for r in response.data)

    def test_admin_can_approve_refund_request(
        self, admin_client, auth_client, paid_order, payment, order_status_refunded, payment_status_refunded, booking_status_cancelled
    ):
        res = auth_client.post('/api/refund-request/', {'order': paid_order.id})
        rr_id = res.data['id']
        with patch('refund_request.views.stripe.Refund.create'):
            response = admin_client.post(f'/api/refund-request/{rr_id}/approve/')
        assert response.status_code == 200
        assert response.data['status'] == 'APPROVED'

    def test_admin_can_reject_refund_request(self, admin_client, auth_client, paid_order):
        res = auth_client.post('/api/refund-request/', {'order': paid_order.id})
        rr_id = res.data['id']
        response = admin_client.post(f'/api/refund-request/{rr_id}/reject/')
        assert response.status_code == 200
        assert response.data['status'] == 'REJECTED'

    def test_approve_stripe_failure_returns_502(
        self, admin_client, auth_client, paid_order, payment, payment_status_refunded
    ):
        res = auth_client.post('/api/refund-request/', {'order': paid_order.id})
        rr_id = res.data['id']
        import stripe
        with patch('refund_request.views.stripe.Refund.create', side_effect=stripe.error.StripeError('fail')):
            response = admin_client.post(f'/api/refund-request/{rr_id}/approve/')
        assert response.status_code == 502

    def test_user_cannot_list_refund_requests(self, auth_client):
        response = auth_client.get('/api/refund-request/')
        assert response.status_code == 403

    def test_user_cannot_approve(self, auth_client, admin_client, order):
        res = auth_client.post('/api/refund-request/', {'order': order.id})
        response = auth_client.post(f'/api/refund-request/{res.data["id"]}/approve/')
        assert response.status_code == 403


# ── Bookings ──────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestBookingList:
    def test_user_sees_own_bookings(self, auth_client, booking):
        response = auth_client.get('/api/booking/')
        assert response.status_code == 200
        assert any(b['id'] == booking.id for b in response.data)

    def test_user_cannot_see_others_bookings(self, other_auth_client, booking):
        response = other_auth_client.get('/api/booking/')
        assert response.status_code == 200
        assert len(response.data) == 0


@pytest.mark.django_db
class TestBookingCancel:
    def test_user_can_cancel_own_booking(self, auth_client, booking, booking_status_cancelled):
        response = auth_client.post(f'/api/booking/{booking.id}/cancel/')
        assert response.status_code == 200
        booking.refresh_from_db()
        assert booking.booking_status.code == 'CANCELLED'

    def test_admin_cannot_cancel_booking(self, admin_client, booking):
        response = admin_client.post(f'/api/booking/{booking.id}/cancel/')
        assert response.status_code == 403

    def test_user_cannot_cancel_others_booking(self, other_auth_client, booking, booking_status_cancelled):
        response = other_auth_client.post(f'/api/booking/{booking.id}/cancel/')
        assert response.status_code == 404 # Should be 404 since they shouldn't see the booking at all

    def test_cannot_cancel_terminal_booking(self, auth_client, booking, booking_status_cancelled):
        booking.booking_status = booking_status_cancelled
        booking.save()
        response = auth_client.post(f'/api/booking/{booking.id}/cancel/')
        assert response.status_code == 403


@pytest.mark.django_db
class TestBookingCheckIn:
    def test_user_can_check_in(self, auth_client, confirmed_booking, booking_status_checked_in):
        response = auth_client.post(f'/api/booking/{confirmed_booking.id}/check_in/')
        assert response.status_code == 200
        confirmed_booking.refresh_from_db()
        assert confirmed_booking.booking_status.code == 'CHECKED_IN'

    def test_check_in_requires_confirmed_status(self, auth_client, booking, booking_status_checked_in):
        response = auth_client.post(f'/api/booking/{booking.id}/check_in/')
        assert response.status_code == 403

    def test_admin_cannot_check_in(self, admin_client, confirmed_booking):
        response = admin_client.post(f'/api/booking/{confirmed_booking.id}/check_in/')
        assert response.status_code == 403


@pytest.mark.django_db
class TestBookingBoard:
    def test_admin_can_board(self, admin_client, confirmed_booking, booking_status_checked_in, booking_status_boarded):
        confirmed_booking.booking_status = booking_status_checked_in
        confirmed_booking.save()
        response = admin_client.post(f'/api/booking/{confirmed_booking.id}/board/')
        assert response.status_code == 200
        confirmed_booking.refresh_from_db()
        assert confirmed_booking.booking_status.code == 'BOARDED'

    def test_board_requires_checked_in_status(self, admin_client, confirmed_booking, booking_status_boarded):
        response = admin_client.post(f'/api/booking/{confirmed_booking.id}/board/')
        assert response.status_code == 403

    def test_user_cannot_board(self, auth_client, confirmed_booking, booking_status_checked_in):
        confirmed_booking.booking_status = booking_status_checked_in
        confirmed_booking.save()
        response = auth_client.post(f'/api/booking/{confirmed_booking.id}/board/')
        assert response.status_code == 403


# ── Payments ──────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestPaymentCreate:
    def test_user_can_create_payment(self, auth_client, order, payment_status_paid):
        response = auth_client.post('/api/payment/', {
            'order': order.id,
            'amount': '500.00',
            'stripe_payment_session_id': 'pi_new_abc',
            'payment_status': payment_status_paid.id,
        })
        assert response.status_code == 201

    def test_admin_cannot_create_payment(self, admin_client, order, payment_status_paid):
        response = admin_client.post('/api/payment/', {
            'order': order.id,
            'amount': '500.00',
            'stripe_payment_session_id': 'pi_new_def',
            'payment_status': payment_status_paid.id,
        })
        assert response.status_code == 403

    def test_user_cannot_pay_for_others_order(self, other_auth_client, order, payment_status_paid):
        response = other_auth_client.post('/api/payment/', {
            'order': order.id,
            'amount': '500.00',
            'stripe_payment_session_id': 'pi_new_ghi',
            'payment_status': payment_status_paid.id,
        })
        assert response.status_code == 403


@pytest.mark.django_db
class TestStripeWebhook:
    def _build_event(self, event_type, session_id, payment_status='paid'):
        return {
            'type': event_type,
            'data': {'object': {'id': session_id, 'payment_status': payment_status}},
        }

    def test_webhook_payment_succeeded(
        self, api_client, pending_payment, order_status_paid, booking_status_confirmed, payment_status_paid
    ):
        event = self._build_event('checkout.session.completed', pending_payment.stripe_payment_session_id)
        with patch('payment.views.stripe.Webhook.construct_event', return_value=event):
            response = api_client.post(
                '/api/payment/webhook/',
                data=json.dumps(event),
                content_type='application/json',
                HTTP_STRIPE_SIGNATURE='sig_test',
            )
        assert response.status_code == 200
        pending_payment.refresh_from_db()
        assert pending_payment.payment_status.code == 'COMPLETED'
        pending_payment.order.refresh_from_db()
        assert pending_payment.order.order_status.code == 'PAID'

    def test_webhook_payment_failed(
        self, api_client, payment, order_status_failed, payment_status_failed
    ):
        event = self._build_event('checkout.session.expired', payment.stripe_payment_session_id)
        with patch('payment.views.stripe.Webhook.construct_event', return_value=event):
            response = api_client.post(
                '/api/payment/webhook/',
                data=json.dumps(event),
                content_type='application/json',
                HTTP_STRIPE_SIGNATURE='sig_test',
            )
        assert response.status_code == 200
        payment.refresh_from_db()
        assert payment.payment_status.code == 'FAILED'

    def test_webhook_invalid_signature_returns_400(self, api_client):
        import stripe
        with patch('payment.views.stripe.Webhook.construct_event', side_effect=stripe.error.SignatureVerificationError('bad sig', 'sig')):
            response = api_client.post(
                '/api/payment/webhook/',
                data='{}',
                content_type='application/json',
                HTTP_STRIPE_SIGNATURE='bad_sig',
            )
        assert response.status_code == 400
