"""English and Vietnamese labels for customer-facing pages. Layer: VIEW."""

TEXT = {
    "en": {
        "nav_order": "Order food", "nav_my_orders": "My orders", "nav_logout": "Log out",
        "login": "Log in", "username": "Username", "password": "Password",
        "choose_hub": "Choose a hub", "hub": "Hub", "load": "Load", "order_here": "Order from this hub",
        "state_quiet": "Quiet", "state_normal": "Normal", "state_busy": "Busy", "state_full": "Full: not accepting orders",
        "menu": "Menu", "qty": "Qty", "price": "Price", "brand": "Brand",
        "address": "Delivery address", "distance": "Distance from the hub (km, up to 7)",
        "voucher_code": "Voucher code (optional, one per order)", "payment": "Payment method",
        "pay_ewallet": "E-wallet", "pay_bank_qr": "Bank QR", "pay_card": "International card",
        "pay_cash": "Cash on delivery", "see_price": "See the full price",
        "items_subtotal": "Items", "delivery_fee": "Delivery fee", "rain_surcharge": "Rain surcharge",
        "quiet_discount": "Quiet-hub discount", "voucher_discount": "Voucher discount", "total": "Total",
        "confirm_order": "Confirm order", "back": "Back", "full_price": "Full price",
        "busy_warning": "This hub is busy. These hubs are quieter:", "no_suggestion": "No quieter hub is available right now.",
        "order": "Order", "status": "Status", "placed_at": "Placed at", "cancel_order": "Cancel order",
        "no_orders": "You have no orders yet.", "notifications": "Notifications", "payment_status": "Payment",
        "language": "Language", "view": "View", "items": "Items",
    },
    "vi": {
        "nav_order": "Đặt món", "nav_my_orders": "Đơn của tôi", "nav_logout": "Đăng xuất",
        "login": "Đăng nhập", "username": "Tên đăng nhập", "password": "Mật khẩu",
        "choose_hub": "Chọn bếp", "hub": "Bếp", "load": "Mức tải", "order_here": "Đặt từ bếp này",
        "state_quiet": "Vắng", "state_normal": "Bình thường", "state_busy": "Bận", "state_full": "Đầy: tạm ngừng nhận đơn",
        "menu": "Thực đơn", "qty": "SL", "price": "Giá", "brand": "Thương hiệu",
        "address": "Địa chỉ giao hàng", "distance": "Khoảng cách từ bếp (km, tối đa 7)",
        "voucher_code": "Mã voucher (không bắt buộc, một mã mỗi đơn)", "payment": "Hình thức thanh toán",
        "pay_ewallet": "Ví điện tử", "pay_bank_qr": "QR ngân hàng", "pay_card": "Thẻ quốc tế",
        "pay_cash": "Tiền mặt khi nhận hàng", "see_price": "Xem tổng giá",
        "items_subtotal": "Tiền món", "delivery_fee": "Phí giao hàng", "rain_surcharge": "Phụ phí mưa",
        "quiet_discount": "Giảm giá bếp vắng", "voucher_discount": "Giảm giá voucher", "total": "Tổng cộng",
        "confirm_order": "Xác nhận đặt hàng", "back": "Quay lại", "full_price": "Tổng giá",
        "busy_warning": "Bếp này đang bận. Các bếp vắng hơn:", "no_suggestion": "Hiện chưa có bếp nào vắng hơn.",
        "order": "Đơn hàng", "status": "Trạng thái", "placed_at": "Đặt lúc", "cancel_order": "Hủy đơn",
        "no_orders": "Bạn chưa có đơn hàng nào.", "notifications": "Thông báo", "payment_status": "Thanh toán",
        "language": "Ngôn ngữ", "view": "Xem", "items": "Món",
    },
}

STATUS_VI = {
    "Placed": "Đã đặt", "Confirmed": "Đã xác nhận", "Rejected": "Bị từ chối", "Cancelled": "Đã hủy",
    "Preparing": "Đang chuẩn bị", "Ready": "Sẵn sàng", "Out for delivery": "Đang giao",
    "Delivered": "Đã giao", "Failed": "Giao thất bại",
}


def translate(lang: str, key: str) -> str:
    return TEXT.get(lang, TEXT["en"]).get(key) or TEXT["en"].get(key, key)


def status_label(lang: str, status: str) -> str:
    return STATUS_VI.get(status, status) if lang == "vi" else status
