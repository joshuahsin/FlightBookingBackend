def booking_list_cache_key(user_id):
    return f"flightbooking:booking_list:user_{user_id}"

def order_list_cache_key(user_id):
    return f"flightbooking:order_list:user_{user_id}"

def payment_list_cache_key(user_id):
    return f"flightbooking:payment_list:user_{user_id}"
