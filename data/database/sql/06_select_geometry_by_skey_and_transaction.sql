-- Get Skey geometry for a specific transaction
SELECT * FROM geometry WHERE skey_id = ? AND transaction_id = ? ORDER BY id ASC;
