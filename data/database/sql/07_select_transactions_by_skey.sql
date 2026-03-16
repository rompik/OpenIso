-- Получить все транзакции для Skey
SELECT * FROM transactions WHERE skey_id = ? ORDER BY timestamp DESC;
