-- Sum of orders per date
SELECT
    DATE_FORMAT(ord.created_at, '%Y-%m-%d') as date
    , SUM(ordi.quantity * ordi.price) as sum
FROM orders_order as ord
    JOIN orders_orderitem as ordi
        ON ord.id = ordi.order_id
GROUP BY date