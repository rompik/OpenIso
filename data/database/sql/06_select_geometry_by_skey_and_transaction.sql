-- Получить геометрию Skey для определённой транзакции
SELECT * FROM geometry WHERE skey_id = ? AND transaction_id = ? ORDER BY id ASC;
