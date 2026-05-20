# X-Forwarded-For — тестовый стенд
## Запуск

```bash
docker compose up --build
```

## Тестирование

### 1. Прямой запрос через nginx1 → app
```bash
curl http://localhost:8081/direct/
```

### 2. Прямой запрос через nginx2 → app
```bash
curl http://localhost:8082/
```

### 3. Цепочка: nginx1 → nginx3 → app
```bash
curl http://localhost:8081/chain/
```

### 4. Попытка подделать XFF
```bash
curl -H "X-Forwarded-For: 6.6.6.6" http://localhost:8081/direct/
# В ответе реальный IP, а не 6.6.6.6
```

```bash
curl -H "X-Forwarded-For: 6.6.6.6" http://localhost:8081/chain/
# В ответе реальный IP, <IP nginx1>  —  без 6.6.6.6
```

### 5. Просмотр в браузере
Откройте http://localhost:8081/direct/ или http://localhost:8081/chain/
