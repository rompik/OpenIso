-- Roll back Skey to a specific transaction (example query to get required geometry)
-- (Apply data from this query to restore the state)
SELECT * FROM geometry WHERE skey_id = ? AND transaction_id = ? ORDER BY id ASC;
