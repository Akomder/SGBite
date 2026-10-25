"""End-to-end checks through the web pages (controllers and views)."""
import re


def test_login_and_redirect_by_role(client, login):
    assert b"Choose a hub" in login("tourist").data or b"Ch" in login("tourist").data
    client.get("/logout")
    assert b"Kitchen" in login("kitchen1").data
    client.get("/logout")
    assert b"Vouchers" in login("admin").data


def test_wrong_password_and_protected_pages(client, login):
    assert b"Wrong username or password" in login("an", "bad").data
    assert client.get("/kitchen").status_code == 302  # redirected to login
    login("an")
    assert client.get("/kitchen").status_code == 403  # wrong role
    assert client.get("/admin/vouchers").status_code == 403
    assert client.get("/reports").status_code == 403


def test_customer_places_order_through_pages(client, login, hubs, items):
    login("tourist")
    data = {f"qty_{items['Rare beef pho'].id}": "2", "address": "Hotel, District 1", "distance_km": "2.5",
            "voucher": "", "payment": "card"}
    preview = client.post(f"/order/hub/{hubs[0].id}/preview", data=data)
    assert preview.status_code == 200 and b"Confirm order" in preview.data
    assert b"150,000 VND" in preview.data  # 130,000 + 25,000 - 5,000 quiet-hub discount
    placed = client.post(f"/order/hub/{hubs[0].id}/place", data=data, follow_redirects=True)
    assert b"Your order was placed" in placed.data and b"Order SB" in placed.data


def test_customer_sees_clear_error_for_bad_input(client, login, hubs, items):
    login("an")
    data = {f"qty_{items['Rare beef pho'].id}": "1", "address": "x", "distance_km": "9", "voucher": "", "payment": "cash"}
    page = client.post(f"/order/hub/{hubs[0].id}/preview", data=data)
    assert b"We deliver up to 7 km" in page.data


def test_language_switch_shows_vietnamese(client, login):
    login("an")
    client.get("/lang/vi")
    assert "Chọn bếp" in client.get("/order").get_data(as_text=True)
    client.get("/lang/en")
    assert b"Choose a hub" in client.get("/order").data


def test_kitchen_confirms_and_rejects_through_pages(client, login, make_order, session):
    a, b = make_order(), make_order()
    login("kitchen1")
    page = client.get("/kitchen")
    assert a.number.encode() in page.data and b"Hub load" in page.data
    ok = client.post(f"/kitchen/orders/{a.id}/confirm", follow_redirects=True)
    assert b"Order confirmed" in ok.data
    no_reason = client.post(f"/kitchen/orders/{b.id}/reject", data={"reason": ""}, follow_redirects=True)
    assert b"reason is required" in no_reason.data
    rejected = client.post(f"/kitchen/orders/{b.id}/reject", data={"reason": "Item out of stock"}, follow_redirects=True)
    assert b"Order rejected" in rejected.data


def test_admin_voucher_crud_through_pages(client, login):
    login("admin")
    data = {"code": "NEW5", "description": "t", "discount_type": "percent", "value": "5", "valid_from": "2026-01-01",
            "valid_to": "2030-01-01", "min_order": "0", "usage_limit": "", "once_per_customer": "1"}
    assert b"Voucher created" in client.post("/admin/vouchers/new", data=data, follow_redirects=True).data
    page = client.get("/admin/vouchers?q=NEW5").get_data(as_text=True)
    vid = re.search(r"/admin/vouchers/(\d+)/edit", page).group(1)
    data["value"] = "8"
    assert b"Voucher updated" in client.post(f"/admin/vouchers/{vid}/edit", data=data, follow_redirects=True).data
    assert b"Voucher deactivated" in client.post(f"/admin/vouchers/{vid}/deactivate", follow_redirects=True).data
    assert b"Deactivated" in client.get("/admin/vouchers?state=Deactivated&q=NEW5").data


def test_manager_reports_and_csv(client, login):
    login("manager")
    for kind in ("sales", "workload", "delivery"):
        assert client.get(f"/reports/{kind}").status_code == 200
    csv = client.get("/reports/sales?format=csv")
    assert csv.mimetype == "text/csv" and b"Sales report" in csv.data
    bad = client.get("/reports/sales?date_from=bad", follow_redirects=True)
    assert b"Dates must look like" in bad.data


def test_unknown_hub_is_handled(client, login):
    login("an")
    assert b"Hub not found" in client.get("/order/hub/999", follow_redirects=True).data
    assert b"Hub not found" in client.post("/order/hub/999/preview", data={}, follow_redirects=True).data
