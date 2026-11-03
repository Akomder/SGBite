-- brands
INSERT INTO brands (id, name) VALUES (1, 'SaigonBite Pho');
INSERT INTO brands (id, name) VALUES (2, 'SaigonBite Rice');
INSERT INTO brands (id, name) VALUES (3, 'SaigonBite Banh Mi');
SELECT setval(pg_get_serial_sequence('brands', 'id'), (SELECT max(id) FROM brands));

-- hubs
INSERT INTO hubs (id, name, address, capacity, rain_mode) VALUES (1, 'Hub District 1', '12 Nguyen Hue, District 1', 10, false);
INSERT INTO hubs (id, name, address, capacity, rain_mode) VALUES (2, 'Hub Thu Duc', '45 Vo Van Ngan, Thu Duc', 8, false);
SELECT setval(pg_get_serial_sequence('hubs', 'id'), (SELECT max(id) FROM hubs));

-- vouchers
INSERT INTO vouchers (id, code, description, discount_type, value, valid_from, valid_to, min_order, usage_limit, used_count, once_per_customer, active) VALUES (1, 'WELCOME10', '10%% off the items', 'percent', 10, '2026-09-29 09:11:00.188452', '2026-12-28 09:11:00.188452', 100000, 100, 0, true, true);
INSERT INTO vouchers (id, code, description, discount_type, value, valid_from, valid_to, min_order, usage_limit, used_count, once_per_customer, active) VALUES (2, 'SAVE20K', '20,000 VND off', 'fixed', 20000, '2026-09-29 09:11:00.188452', '2026-12-28 09:11:00.188452', 150000, NULL, 0, true, true);
INSERT INTO vouchers (id, code, description, discount_type, value, valid_from, valid_to, min_order, usage_limit, used_count, once_per_customer, active) VALUES (3, 'OLD5', 'Expired example', 'percent', 5, '2026-07-31 09:11:00.188452', '2026-09-29 09:11:00.188452', 0, NULL, 0, true, true);
SELECT setval(pg_get_serial_sequence('vouchers', 'id'), (SELECT max(id) FROM vouchers));

-- menu_items
INSERT INTO menu_items (id, brand_id, name_vi, name_en, price) VALUES (1, 1, 'Phở bò tái', 'Rare beef pho', 65000);
INSERT INTO menu_items (id, brand_id, name_vi, name_en, price) VALUES (2, 1, 'Phở gà', 'Chicken pho', 55000);
INSERT INTO menu_items (id, brand_id, name_vi, name_en, price) VALUES (3, 2, 'Cơm tấm sườn', 'Broken rice with pork chop', 60000);
INSERT INTO menu_items (id, brand_id, name_vi, name_en, price) VALUES (4, 2, 'Cơm gà xối mỡ', 'Crispy chicken rice', 58000);
INSERT INTO menu_items (id, brand_id, name_vi, name_en, price) VALUES (5, 3, 'Bánh mì thịt nướng', 'Grilled pork banh mi', 35000);
INSERT INTO menu_items (id, brand_id, name_vi, name_en, price) VALUES (6, 3, 'Bánh mì trứng', 'Egg banh mi', 25000);
SELECT setval(pg_get_serial_sequence('menu_items', 'id'), (SELECT max(id) FROM menu_items));

-- users
INSERT INTO users (id, username, password_hash, full_name, role, customer_type, phone, email, hub_id) VALUES (1, 'an', 'pbkdf2:sha256:1000$6yXoQyRQnnPaK65S$530fca792534e6ae74a4aaf6ecdb79072d7b7badc942447aad642c806de95154', 'Nguyen Van An', 'customer', 'local', '0901234567', NULL, NULL);
INSERT INTO users (id, username, password_hash, full_name, role, customer_type, phone, email, hub_id) VALUES (2, 'tourist', 'pbkdf2:sha256:1000$KRBwctsdvdqW3Eq8$cb790c0f124ef219eddc315ca3117083c0ba7cb25ea01914101575b01b4aed14', 'Emma Jones', 'customer', 'tourist', NULL, 'emma@example.com', NULL);
INSERT INTO users (id, username, password_hash, full_name, role, customer_type, phone, email, hub_id) VALUES (3, 'kitchen1', 'pbkdf2:sha256:1000$zqK6UMykqDpIrIxb$8ea4b626d11b3d02a7d004f7cde61ff4dc8d27c673378cf2a045c959bbe8181b', 'Kitchen staff Hub D1', 'kitchen', NULL, NULL, NULL, 1);
INSERT INTO users (id, username, password_hash, full_name, role, customer_type, phone, email, hub_id) VALUES (4, 'kitchen2', 'pbkdf2:sha256:1000$QkJfn7hV5PEyDo8N$642d59780cc1894f6a2691e6703387689409a947423b24e69d59617c22c3eec0', 'Kitchen staff Hub Thu Duc', 'kitchen', NULL, NULL, NULL, 2);
INSERT INTO users (id, username, password_hash, full_name, role, customer_type, phone, email, hub_id) VALUES (5, 'admin', 'pbkdf2:sha256:1000$6QeM7zw4nk5lgMvG$2c9e0a717b82e444d71be3b14035c435b30b12bd906199caeb21224d801faf39', 'Admin', 'admin', NULL, NULL, NULL, NULL);
INSERT INTO users (id, username, password_hash, full_name, role, customer_type, phone, email, hub_id) VALUES (6, 'manager', 'pbkdf2:sha256:1000$zotqKtDdp8fWNDP7$4b91ab832b37e4f5e4841c3724d10887e613b9dddc63f45884402f198b6051b9', 'Manager', 'manager', NULL, NULL, NULL, NULL);
SELECT setval(pg_get_serial_sequence('users', 'id'), (SELECT max(id) FROM users));

-- hub_menu_items
INSERT INTO hub_menu_items (hub_id, menu_item_id, available) VALUES (1, 1, true);
INSERT INTO hub_menu_items (hub_id, menu_item_id, available) VALUES (1, 2, true);
INSERT INTO hub_menu_items (hub_id, menu_item_id, available) VALUES (1, 3, true);
INSERT INTO hub_menu_items (hub_id, menu_item_id, available) VALUES (1, 4, true);
INSERT INTO hub_menu_items (hub_id, menu_item_id, available) VALUES (1, 5, true);
INSERT INTO hub_menu_items (hub_id, menu_item_id, available) VALUES (1, 6, true);
INSERT INTO hub_menu_items (hub_id, menu_item_id, available) VALUES (2, 1, true);
INSERT INTO hub_menu_items (hub_id, menu_item_id, available) VALUES (2, 2, true);
INSERT INTO hub_menu_items (hub_id, menu_item_id, available) VALUES (2, 3, true);
INSERT INTO hub_menu_items (hub_id, menu_item_id, available) VALUES (2, 4, true);
INSERT INTO hub_menu_items (hub_id, menu_item_id, available) VALUES (2, 5, true);
INSERT INTO hub_menu_items (hub_id, menu_item_id, available) VALUES (2, 6, false);

-- orders
INSERT INTO orders (id, number, customer_id, hub_id, status, delivery_address, distance_km, items_subtotal, delivery_fee, rain_surcharge, quiet_discount, voucher_id, voucher_discount, total, payment_method, payment_status, reject_reason, created_at, confirmed_at, delivered_at) VALUES (1, 'SB261027-00001', 2, 2, 'Delivered', 'Demo address', 5.9, 150000, 35000, 0, 0, NULL, 0, 185000, 'cash', 'Collected', NULL, '2026-10-27 19:30:00', '2026-10-27 19:33:00', '2026-10-27 20:01:00');
INSERT INTO orders (id, number, customer_id, hub_id, status, delivery_address, distance_km, items_subtotal, delivery_fee, rain_surcharge, quiet_discount, voucher_id, voucher_discount, total, payment_method, payment_status, reject_reason, created_at, confirmed_at, delivered_at) VALUES (2, 'SB261027-00002', 1, 1, 'Delivered', 'Demo address', 5.1, 231000, 35000, 0, 0, NULL, 0, 266000, 'cash', 'Collected', NULL, '2026-10-27 12:39:00', '2026-10-27 12:42:00', '2026-10-27 13:04:00');
INSERT INTO orders (id, number, customer_id, hub_id, status, delivery_address, distance_km, items_subtotal, delivery_fee, rain_surcharge, quiet_discount, voucher_id, voucher_discount, total, payment_method, payment_status, reject_reason, created_at, confirmed_at, delivered_at) VALUES (3, 'SB261025-00003', 1, 1, 'Delivered', 'Demo address', 2.2, 55000, 25000, 0, 0, NULL, 0, 80000, 'ewallet', 'Paid', NULL, '2026-10-25 13:11:00', '2026-10-25 13:14:00', '2026-10-25 14:00:00');
INSERT INTO orders (id, number, customer_id, hub_id, status, delivery_address, distance_km, items_subtotal, delivery_fee, rain_surcharge, quiet_discount, voucher_id, voucher_discount, total, payment_method, payment_status, reject_reason, created_at, confirmed_at, delivered_at) VALUES (4, 'SB261024-00004', 1, 2, 'Delivered', 'Demo address', 0.9, 168000, 15000, 0, 0, NULL, 0, 183000, 'cash', 'Collected', NULL, '2026-10-24 11:38:00', '2026-10-24 11:41:00', '2026-10-24 12:22:00');
INSERT INTO orders (id, number, customer_id, hub_id, status, delivery_address, distance_km, items_subtotal, delivery_fee, rain_surcharge, quiet_discount, voucher_id, voucher_discount, total, payment_method, payment_status, reject_reason, created_at, confirmed_at, delivered_at) VALUES (5, 'SB261026-00005', 2, 2, 'Delivered', 'Demo address', 3.3, 145000, 25000, 0, 0, NULL, 0, 170000, 'cash', 'Collected', NULL, '2026-10-26 11:16:00', '2026-10-26 11:19:00', '2026-10-26 12:03:00');
INSERT INTO orders (id, number, customer_id, hub_id, status, delivery_address, distance_km, items_subtotal, delivery_fee, rain_surcharge, quiet_discount, voucher_id, voucher_discount, total, payment_method, payment_status, reject_reason, created_at, confirmed_at, delivered_at) VALUES (6, 'SB261019-00006', 1, 2, 'Delivered', 'Demo address', 4.7, 203000, 35000, 0, 0, NULL, 0, 238000, 'ewallet', 'Paid', NULL, '2026-10-19 13:07:00', '2026-10-19 13:10:00', '2026-10-19 14:01:00');
INSERT INTO orders (id, number, customer_id, hub_id, status, delivery_address, distance_km, items_subtotal, delivery_fee, rain_surcharge, quiet_discount, voucher_id, voucher_discount, total, payment_method, payment_status, reject_reason, created_at, confirmed_at, delivered_at) VALUES (7, 'SB261027-00007', 2, 2, 'Delivered', 'Demo address', 3.1, 301000, 25000, 0, 0, NULL, 0, 326000, 'cash', 'Collected', NULL, '2026-10-27 13:21:00', '2026-10-27 13:24:00', '2026-10-27 13:55:00');
INSERT INTO orders (id, number, customer_id, hub_id, status, delivery_address, distance_km, items_subtotal, delivery_fee, rain_surcharge, quiet_discount, voucher_id, voucher_discount, total, payment_method, payment_status, reject_reason, created_at, confirmed_at, delivered_at) VALUES (8, 'SB261026-00008', 2, 2, 'Delivered', 'Demo address', 5.3, 260000, 35000, 0, 0, NULL, 0, 295000, 'cash', 'Collected', NULL, '2026-10-26 18:30:00', '2026-10-26 18:33:00', '2026-10-26 19:29:00');
INSERT INTO orders (id, number, customer_id, hub_id, status, delivery_address, distance_km, items_subtotal, delivery_fee, rain_surcharge, quiet_discount, voucher_id, voucher_discount, total, payment_method, payment_status, reject_reason, created_at, confirmed_at, delivered_at) VALUES (9, 'SB261021-00009', 1, 2, 'Failed', 'Demo address', 5.5, 50000, 35000, 0, 0, NULL, 0, 85000, 'ewallet', 'Paid', NULL, '2026-10-21 19:09:00', '2026-10-21 19:12:00', NULL);
INSERT INTO orders (id, number, customer_id, hub_id, status, delivery_address, distance_km, items_subtotal, delivery_fee, rain_surcharge, quiet_discount, voucher_id, voucher_discount, total, payment_method, payment_status, reject_reason, created_at, confirmed_at, delivered_at) VALUES (10, 'SB261022-00010', 2, 1, 'Failed', 'Demo address', 1.1, 105000, 15000, 0, 0, NULL, 0, 120000, 'card', 'Paid', NULL, '2026-10-22 19:09:00', '2026-10-22 19:12:00', NULL);
INSERT INTO orders (id, number, customer_id, hub_id, status, delivery_address, distance_km, items_subtotal, delivery_fee, rain_surcharge, quiet_discount, voucher_id, voucher_discount, total, payment_method, payment_status, reject_reason, created_at, confirmed_at, delivered_at) VALUES (11, 'SB261021-00011', 2, 1, 'Delivered', 'Demo address', 2.1, 296000, 25000, 0, 0, NULL, 0, 321000, 'cash', 'Collected', NULL, '2026-10-21 19:57:00', '2026-10-21 20:00:00', '2026-10-21 20:56:00');
INSERT INTO orders (id, number, customer_id, hub_id, status, delivery_address, distance_km, items_subtotal, delivery_fee, rain_surcharge, quiet_discount, voucher_id, voucher_discount, total, payment_method, payment_status, reject_reason, created_at, confirmed_at, delivered_at) VALUES (12, 'SB261020-00012', 2, 1, 'Delivered', 'Demo address', 3.6, 240000, 25000, 0, 0, NULL, 0, 265000, 'card', 'Paid', NULL, '2026-10-20 19:04:00', '2026-10-20 19:07:00', '2026-10-20 20:06:00');
INSERT INTO orders (id, number, customer_id, hub_id, status, delivery_address, distance_km, items_subtotal, delivery_fee, rain_surcharge, quiet_discount, voucher_id, voucher_discount, total, payment_method, payment_status, reject_reason, created_at, confirmed_at, delivered_at) VALUES (13, 'SB261024-00013', 2, 1, 'Delivered', 'Demo address', 5.1, 190000, 35000, 0, 0, NULL, 0, 225000, 'card', 'Paid', NULL, '2026-10-24 19:41:00', '2026-10-24 19:44:00', '2026-10-24 20:36:00');
INSERT INTO orders (id, number, customer_id, hub_id, status, delivery_address, distance_km, items_subtotal, delivery_fee, rain_surcharge, quiet_discount, voucher_id, voucher_discount, total, payment_method, payment_status, reject_reason, created_at, confirmed_at, delivered_at) VALUES (14, 'SB261022-00014', 2, 2, 'Delivered', 'Demo address', 4.4, 286000, 35000, 0, 0, NULL, 0, 321000, 'card', 'Paid', NULL, '2026-10-22 19:59:00', '2026-10-22 20:02:00', '2026-10-22 20:52:00');
INSERT INTO orders (id, number, customer_id, hub_id, status, delivery_address, distance_km, items_subtotal, delivery_fee, rain_surcharge, quiet_discount, voucher_id, voucher_discount, total, payment_method, payment_status, reject_reason, created_at, confirmed_at, delivered_at) VALUES (15, 'SB261027-00015', 2, 2, 'Delivered', 'Demo address', 2.2, 175000, 25000, 0, 0, NULL, 0, 200000, 'card', 'Paid', NULL, '2026-10-27 19:10:00', '2026-10-27 19:13:00', '2026-10-27 20:08:00');
INSERT INTO orders (id, number, customer_id, hub_id, status, delivery_address, distance_km, items_subtotal, delivery_fee, rain_surcharge, quiet_discount, voucher_id, voucher_discount, total, payment_method, payment_status, reject_reason, created_at, confirmed_at, delivered_at) VALUES (16, 'SB261026-00016', 2, 2, 'Delivered', 'Demo address', 4.2, 225000, 35000, 0, 0, NULL, 0, 260000, 'card', 'Paid', NULL, '2026-10-26 13:48:00', '2026-10-26 13:51:00', '2026-10-26 14:15:00');
INSERT INTO orders (id, number, customer_id, hub_id, status, delivery_address, distance_km, items_subtotal, delivery_fee, rain_surcharge, quiet_discount, voucher_id, voucher_discount, total, payment_method, payment_status, reject_reason, created_at, confirmed_at, delivered_at) VALUES (17, 'SB261026-00017', 1, 2, 'Delivered', 'Demo address', 1.2, 65000, 15000, 0, 0, NULL, 0, 80000, 'ewallet', 'Paid', NULL, '2026-10-26 20:12:00', '2026-10-26 20:15:00', '2026-10-26 20:59:00');
INSERT INTO orders (id, number, customer_id, hub_id, status, delivery_address, distance_km, items_subtotal, delivery_fee, rain_surcharge, quiet_discount, voucher_id, voucher_discount, total, payment_method, payment_status, reject_reason, created_at, confirmed_at, delivered_at) VALUES (18, 'SB261022-00018', 1, 2, 'Delivered', 'Demo address', 6.2, 225000, 35000, 0, 0, NULL, 0, 260000, 'cash', 'Collected', NULL, '2026-10-22 12:44:00', '2026-10-22 12:47:00', '2026-10-22 13:11:00');
INSERT INTO orders (id, number, customer_id, hub_id, status, delivery_address, distance_km, items_subtotal, delivery_fee, rain_surcharge, quiet_discount, voucher_id, voucher_discount, total, payment_method, payment_status, reject_reason, created_at, confirmed_at, delivered_at) VALUES (19, 'SB261026-00019', 1, 2, 'Delivered', 'Demo address', 6.2, 120000, 35000, 0, 0, NULL, 0, 155000, 'ewallet', 'Paid', NULL, '2026-10-26 19:26:00', '2026-10-26 19:29:00', '2026-10-26 20:14:00');
INSERT INTO orders (id, number, customer_id, hub_id, status, delivery_address, distance_km, items_subtotal, delivery_fee, rain_surcharge, quiet_discount, voucher_id, voucher_discount, total, payment_method, payment_status, reject_reason, created_at, confirmed_at, delivered_at) VALUES (20, 'SB261025-00020', 1, 2, 'Failed', 'Demo address', 3.9, 70000, 25000, 0, 0, NULL, 0, 95000, 'ewallet', 'Paid', NULL, '2026-10-25 12:38:00', '2026-10-25 12:41:00', NULL);
INSERT INTO orders (id, number, customer_id, hub_id, status, delivery_address, distance_km, items_subtotal, delivery_fee, rain_surcharge, quiet_discount, voucher_id, voucher_discount, total, payment_method, payment_status, reject_reason, created_at, confirmed_at, delivered_at) VALUES (21, 'SB261019-00021', 2, 1, 'Delivered', 'Demo address', 2.5, 60000, 25000, 0, 0, NULL, 0, 85000, 'cash', 'Collected', NULL, '2026-10-19 19:27:00', '2026-10-19 19:30:00', '2026-10-19 20:10:00');
INSERT INTO orders (id, number, customer_id, hub_id, status, delivery_address, distance_km, items_subtotal, delivery_fee, rain_surcharge, quiet_discount, voucher_id, voucher_discount, total, payment_method, payment_status, reject_reason, created_at, confirmed_at, delivered_at) VALUES (22, 'SB261022-00022', 2, 2, 'Delivered', 'Demo address', 3.5, 180000, 25000, 0, 0, NULL, 0, 205000, 'cash', 'Collected', NULL, '2026-10-22 11:20:00', '2026-10-22 11:23:00', '2026-10-22 12:03:00');
INSERT INTO orders (id, number, customer_id, hub_id, status, delivery_address, distance_km, items_subtotal, delivery_fee, rain_surcharge, quiet_discount, voucher_id, voucher_discount, total, payment_method, payment_status, reject_reason, created_at, confirmed_at, delivered_at) VALUES (23, 'SB261028-00023', 2, 1, 'Delivered', 'Demo address', 2.0, 130000, 15000, 0, 0, NULL, 0, 145000, 'card', 'Paid', NULL, '2026-10-28 12:52:00', '2026-10-28 12:55:00', '2026-10-28 13:52:00');
INSERT INTO orders (id, number, customer_id, hub_id, status, delivery_address, distance_km, items_subtotal, delivery_fee, rain_surcharge, quiet_discount, voucher_id, voucher_discount, total, payment_method, payment_status, reject_reason, created_at, confirmed_at, delivered_at) VALUES (24, 'SB261024-00024', 1, 2, 'Delivered', 'Demo address', 5.6, 240000, 35000, 0, 0, NULL, 0, 275000, 'ewallet', 'Paid', NULL, '2026-10-24 18:31:00', '2026-10-24 18:34:00', '2026-10-24 19:03:00');
INSERT INTO orders (id, number, customer_id, hub_id, status, delivery_address, distance_km, items_subtotal, delivery_fee, rain_surcharge, quiet_discount, voucher_id, voucher_discount, total, payment_method, payment_status, reject_reason, created_at, confirmed_at, delivered_at) VALUES (25, 'SB261028-00025', 1, 1, 'Delivered', 'Demo address', 4.9, 190000, 35000, 0, 0, NULL, 0, 225000, 'ewallet', 'Paid', NULL, '2026-10-28 20:22:00', '2026-10-28 20:25:00', '2026-10-28 21:24:00');
INSERT INTO orders (id, number, customer_id, hub_id, status, delivery_address, distance_km, items_subtotal, delivery_fee, rain_surcharge, quiet_discount, voucher_id, voucher_discount, total, payment_method, payment_status, reject_reason, created_at, confirmed_at, delivered_at) VALUES (26, 'SB261027-00026', 1, 1, 'Delivered', 'Demo address', 4.6, 120000, 35000, 0, 0, NULL, 0, 155000, 'ewallet', 'Paid', NULL, '2026-10-27 13:00:00', '2026-10-27 13:03:00', '2026-10-27 14:01:00');
INSERT INTO orders (id, number, customer_id, hub_id, status, delivery_address, distance_km, items_subtotal, delivery_fee, rain_surcharge, quiet_discount, voucher_id, voucher_discount, total, payment_method, payment_status, reject_reason, created_at, confirmed_at, delivered_at) VALUES (27, 'SB261027-00027', 2, 2, 'Failed', 'Demo address', 5.5, 226000, 35000, 0, 0, NULL, 0, 261000, 'card', 'Paid', NULL, '2026-10-27 18:53:00', '2026-10-27 18:56:00', NULL);
INSERT INTO orders (id, number, customer_id, hub_id, status, delivery_address, distance_km, items_subtotal, delivery_fee, rain_surcharge, quiet_discount, voucher_id, voucher_discount, total, payment_method, payment_status, reject_reason, created_at, confirmed_at, delivered_at) VALUES (28, 'SB261020-00028', 2, 2, 'Delivered', 'Demo address', 6.3, 160000, 35000, 0, 0, NULL, 0, 195000, 'card', 'Paid', NULL, '2026-10-20 12:27:00', '2026-10-20 12:30:00', '2026-10-20 12:56:00');
INSERT INTO orders (id, number, customer_id, hub_id, status, delivery_address, distance_km, items_subtotal, delivery_fee, rain_surcharge, quiet_discount, voucher_id, voucher_discount, total, payment_method, payment_status, reject_reason, created_at, confirmed_at, delivered_at) VALUES (29, 'SB261022-00029', 2, 1, 'Delivered', 'Demo address', 2.5, 65000, 25000, 0, 0, NULL, 0, 90000, 'cash', 'Collected', NULL, '2026-10-22 12:25:00', '2026-10-22 12:28:00', '2026-10-22 12:57:00');
INSERT INTO orders (id, number, customer_id, hub_id, status, delivery_address, distance_km, items_subtotal, delivery_fee, rain_surcharge, quiet_discount, voucher_id, voucher_discount, total, payment_method, payment_status, reject_reason, created_at, confirmed_at, delivered_at) VALUES (30, 'SB261026-00030', 1, 1, 'Delivered', 'Demo address', 3.0, 173000, 25000, 0, 0, NULL, 0, 198000, 'ewallet', 'Paid', NULL, '2026-10-26 12:39:00', '2026-10-26 12:42:00', '2026-10-26 13:28:00');
SELECT setval(pg_get_serial_sequence('orders', 'id'), (SELECT max(id) FROM orders));

-- order_items
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (1, 1, 6, 2, 25000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (2, 1, 5, 1, 35000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (3, 1, 1, 1, 65000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (4, 2, 2, 1, 55000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (5, 2, 4, 2, 58000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (6, 2, 3, 1, 60000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (7, 3, 2, 1, 55000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (8, 4, 4, 1, 58000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (9, 4, 2, 2, 55000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (10, 5, 6, 1, 25000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (11, 5, 3, 2, 60000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (12, 6, 4, 1, 58000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (13, 6, 3, 2, 60000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (14, 6, 6, 1, 25000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (15, 7, 3, 2, 60000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (16, 7, 4, 2, 58000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (17, 7, 1, 1, 65000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (18, 8, 5, 2, 35000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (19, 8, 1, 2, 65000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (20, 8, 3, 1, 60000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (21, 9, 6, 2, 25000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (22, 10, 2, 1, 55000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (23, 10, 6, 2, 25000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (24, 11, 2, 2, 55000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (25, 11, 5, 2, 35000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (26, 11, 4, 2, 58000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (27, 12, 2, 2, 55000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (28, 12, 1, 2, 65000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (29, 13, 5, 2, 35000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (30, 13, 3, 2, 60000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (31, 14, 3, 2, 60000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (32, 14, 4, 2, 58000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (33, 14, 6, 2, 25000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (34, 15, 2, 1, 55000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (35, 15, 5, 2, 35000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (36, 15, 6, 2, 25000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (37, 16, 5, 1, 35000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (38, 16, 3, 1, 60000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (39, 16, 1, 2, 65000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (40, 17, 1, 1, 65000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (41, 18, 2, 1, 55000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (42, 18, 6, 2, 25000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (43, 18, 3, 2, 60000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (44, 19, 5, 2, 35000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (45, 19, 6, 2, 25000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (46, 20, 5, 2, 35000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (47, 21, 3, 1, 60000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (48, 22, 2, 2, 55000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (49, 22, 5, 2, 35000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (50, 23, 1, 2, 65000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (51, 24, 1, 2, 65000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (52, 24, 2, 2, 55000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (53, 25, 3, 2, 60000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (54, 25, 5, 2, 35000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (55, 26, 3, 2, 60000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (56, 27, 4, 2, 58000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (57, 27, 2, 2, 55000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (58, 28, 2, 2, 55000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (59, 28, 6, 2, 25000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (60, 29, 1, 1, 65000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (61, 30, 2, 1, 55000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (62, 30, 3, 1, 60000);
INSERT INTO order_items (id, order_id, menu_item_id, quantity, unit_price) VALUES (63, 30, 4, 1, 58000);
SELECT setval(pg_get_serial_sequence('order_items', 'id'), (SELECT max(id) FROM order_items));
