# Traceability: use case to requirement to code to test

Requirement IDs are from the Requirements List sheet of the team workbook.

## UC1 Place an order (523K0076)

| Requirement | Code | Test |
|---|---|---|
| FR1 choose hub, brand, items | `OrderingService.menu_for`, `choose_hub.html`, `order_form.html` | `test_customer_places_order_through_pages` |
| FR2 only items available at the hub | `MenuRepository.available_items`, `OrderingService.quote` | `test_item_not_available_at_hub` |
| FR3 address and distance limit | `pricing.delivery_fee` | `test_distance_validation`, `test_distance_outside_area_is_rejected` |
| FR4 delivery fee and surcharge | `pricing.calculate` | `test_delivery_fee_bands`, `test_total_adds_fee_and_rain...` |
| FR5 full price before confirming | `OrderingService.quote`, `order_preview.html` | `test_place_order_creates_placed_order_with_full_price` |
| FR6 one voucher per order | `Voucher.check_applicable`, `Voucher.discount_for` | `test_voucher_applied_and_counted`, `test_voucher_errors` |
| FR7 payment by customer type | `ALLOWED_PAYMENTS` | `test_payment_options_depend_on_customer_type` |
| FR8 order created as Placed | `OrderingService.place` | `test_place_order_creates_placed_order_with_full_price` |
| FR9 busy-hub warning | `Hub.state`, `OrderingService._suggestions` | `test_busy_hub_warns_and_suggests_quieter_hub` |
| FR13 stop at capacity | `OrderingService.quote` (raises `HubFullError`) | `test_full_hub_stops_accepting_orders` |

## UC2 Confirm or reject an incoming order (523V0017)

| Requirement | Code | Test |
|---|---|---|
| FR10 list new orders, oldest first | `KitchenService.incoming_orders`, `OrderRepository.incoming` | `test_incoming_orders_are_for_own_hub_oldest_first` |
| FR11 confirm and notify | `Order.confirm`, `KitchenService.confirm` | `test_confirm_changes_state_and_notifies_customer` |
| FR12 reject with reason and refund | `Order.reject`, `KitchenService.reject` | `test_reject_requires_reason_and_refunds` |
| FR14 show hub load | `KitchenService.hub_status`, `kitchen.html` | `test_hub_load_counts_confirmed_orders` |
| State machine | `models.TRANSITIONS`, `Order._move` | `test_order_state_machine_happy_path`, `test_invalid_transitions_are_blocked` |

## UC3 Manage vouchers (523K0076)

| Requirement | Code | Test |
|---|---|---|
| FR15 create | `VoucherService.create` | `test_create_read_update_deactivate`, `test_invalid_voucher_input_is_rejected` |
| FR16 view, search, filter | `VoucherService.list`, `VoucherRepository.search` | `test_create_read_update_deactivate` |
| FR17 update (not expired) | `VoucherService.update` | `test_expired_voucher_cannot_be_updated` |
| FR18 deactivate, history kept | `VoucherService.deactivate` | `test_deactivated_voucher_cannot_be_used_but_history_stays` |
| Voucher state machine | `Voucher.state` | `test_voucher_states` |

## UC4 Produce management reports (523V0017)

| Requirement | Code | Test |
|---|---|---|
| FR19 sales report | `ReportService.sales` | `test_sales_totals_only_delivered_orders`, `test_sales_filter_by_hub_and_brand` |
| FR20 hub workload | `ReportService.workload` | `test_workload_shows_peak_hour_against_capacity` |
| FR21 delivery performance | `ReportService.delivery` | `test_delivery_performance`, `test_failed_deliveries_are_counted` |
| FR22 CSV export | `reports.show` (`format=csv`), `Report.csv_rows` | `test_csv_rows_include_summary_and_tables`, `test_manager_reports_and_csv` |

## Not covered by the code

NFR load and availability targets, the shipper and office-staff roles, and real payment, SMS and maps.
