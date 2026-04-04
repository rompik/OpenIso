-- Get all transactions for Skey
SELECT * FROM transactions WHERE skey_id = ? ORDER BY timestamp DESC;
