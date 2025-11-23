# ⚙️ Guía de Configuración - Crypto Trading Bot

Esta guía explica en detalle todas las variables de configuración disponibles en el archivo `.env`.

---

## 📝 Estructura del Archivo .env

El archivo `.env` controla todo el comportamiento del bot. Cada variable tiene un propósito específico.

---

## 🔑 BINANCE API CONFIGURATION

### BINANCE_TESTNET_API_KEY
**Tipo**: String  
**Requerido**: Sí (para testnet)  
**Ejemplo**: `BINANCE_TESTNET_API_KEY=abc123def456ghi789`

Tu clave API de Binance Testnet. Obténla en https://testnet.binance.vision/

### BINANCE_TESTNET_API_SECRET
**Tipo**: String  
**Requerido**: Sí (para testnet)  
**Ejemplo**: `BINANCE_TESTNET_API_SECRET=xyz987uvw654rst321`

Tu clave secreta de Binance Testnet.

### BINANCE_API_KEY
**Tipo**: String  
**Requerido**: Sí (solo para producción)  
**Ejemplo**: `BINANCE_API_KEY=prod_abc123`

Tu clave API de Binance PRODUCCIÓN. **Solo usa cuando estés listo para trading real.**

### BINANCE_API_SECRET
**Tipo**: String  
**Requerido**: Sí (solo para producción)  
**Ejemplo**: `BINANCE_API_SECRET=prod_xyz987`

Tu clave secreta de Binance PRODUCCIÓN.

### USE_TESTNET
**Tipo**: Boolean (true/false)  
**Default**: `true`  
**Recomendado**: `true` (siempre al comenzar)  
**Ejemplo**: `USE_TESTNET=true`

Si está en `true`, usa Binance Testnet (dinero ficticio, gratis).  
Si está en `false`, usa Binance Producción (dinero real).

---

## 💱 TRADING CONFIGURATION

### SYMBOLS
**Tipo**: String (lista separada por comas)  
**Default**: `BTC/USDT,ETH/USDT`  
**Ejemplo**: `SYMBOLS=BTC/USDT,ETH/USDT,BNB/USDT`

Lista de pares de trading a monitorear. El bot analizará cada uno independientemente.

**Formatos aceptados**:
- `BTC/USDT` - Bitcoin vs USDT
- `ETH/USDT` - Ethereum vs USDT
- `BNB/USDT` - Binance Coin vs USDT

**Recomendaciones**:
- Comienza con 1-3 pares
- Usa pares líquidos (alto volumen)
- USDT es la quote currency más común

### TIMEFRAME
**Tipo**: String  
**Default**: `1h`  
**Opciones**: `1m`, `5m`, `15m`, `30m`, `1h`, `4h`, `1d`  
**Ejemplo**: `TIMEFRAME=1h`

Intervalo de tiempo de cada vela (candlestick) para el análisis.

**Guía de selección**:
- `1m`, `5m` - Muy corto plazo, señales frecuentes, más ruido
- `15m`, `30m` - Corto plazo, balance entre señales y estabilidad
- `1h` - **Recomendado para comenzar**, buen balance
- `4h` - Mediano plazo, señales más confiables pero menos frecuentes
- `1d` - Largo plazo, señales muy poco frecuentes

### INITIAL_CAPITAL
**Tipo**: Float  
**Default**: `10000`  
**Ejemplo**: `INITIAL_CAPITAL=10000`

Capital inicial en USDT para backtesting y cálculos de riesgo.

**Recomendaciones**:
- Para testnet: Cualquier valor (es ficticio)
- Para producción: Tu capital real disponible
- Mínimo recomendado: $100 en producción

---

## 🛡️ RISK MANAGEMENT

### RISK_PER_TRADE
**Tipo**: Float (porcentaje)  
**Default**: `2`  
**Rango recomendado**: `1-5`  
**Ejemplo**: `RISK_PER_TRADE=2`

Porcentaje máximo de tu capital a arriesgar por operación.

**Ejemplos**:
- Con $10,000 y `RISK_PER_TRADE=2`: Arriesgas máximo $200 por trade
- Con $1,000 y `RISK_PER_TRADE=1`: Arriesgas máximo $10 por trade

**Recomendaciones**:
- **Conservador**: 1%
- **Moderado**: 2% (recomendado)
- **Agresivo**: 3-5%
- **No recomendado**: >5%

### MAX_POSITIONS
**Tipo**: Integer  
**Default**: `3`  
**Rango recomendado**: `1-5`  
**Ejemplo**: `MAX_POSITIONS=3`

Número máximo de posiciones abiertas simultáneamente.

**Ejemplos**:
- `MAX_POSITIONS=1`: Solo una operación a la vez
- `MAX_POSITIONS=3`: Hasta 3 pares diferentes simultáneamente

**Recomendaciones**:
- Con poco capital (<$1000): 1-2
- Capital medio ($1000-$10000): 2-3
- Capital alto (>$10000): 3-5

### STOP_LOSS_PERCENT
**Tipo**: Float (porcentaje)  
**Default**: `2`  
**Ejemplo**: `STOP_LOSS_PERCENT=2`

Porcentaje de pérdida donde se cierra automáticamente la posición.

**Ejemplo**:
- Compras a $100, con `STOP_LOSS_PERCENT=2`
- Stop loss se coloca a $98 (2% abajo)
- Si el precio cae a $98, se vende automáticamente

**Recomendaciones**:
- Mercados volátiles (crypto): 2-5%
- Más conservador: 1-2%
- Más agresivo: 5-10%

### TAKE_PROFIT_PERCENT
**Tipo**: Float (porcentaje)  
**Default**: `4`  
**Ejemplo**: `TAKE_PROFIT_PERCENT=4`

Porcentaje de ganancia donde se cierra automáticamente la posición.

**Ejemplo**:
- Compras a $100, con `TAKE_PROFIT_PERCENT=4`
- Take profit se coloca a $104 (4% arriba)
- Si el precio sube a $104, se vende automáticamente

**Recomendaciones**:
- Ratio risk:reward de 1:2 es ideal
- Si `STOP_LOSS=2%`, entonces `TAKE_PROFIT=4%` o más
- Ajustar según la volatilidad del mercado

### MAX_PORTFOLIO_EXPOSURE
**Tipo**: Float (porcentaje)  
**Default**: `50`  
**Ejemplo**: `MAX_PORTFOLIO_EXPOSURE=50`

Porcentaje máximo del capital total que puede estar invertido.

**Ejemplo**:
- Capital: $10,000
- `MAX_PORTFOLIO_EXPOSURE=50`
- Máximo $5,000 puede estar en posiciones abiertas

**Recomendaciones**:
- Conservador: 30-40%
- Moderado: 50% (recomendado)
- Agresivo: 70-80%

---

## 📊 STRATEGY CONFIGURATION

### SMA_SHORT_PERIOD
**Tipo**: Integer  
**Default**: `20`  
**Rango típico**: `10-50`  
**Ejemplo**: `SMA_SHORT_PERIOD=20`

Período de la SMA corta (rápida) en velas.

**Ejemplos comunes**:
- `10` - Muy rápida, más señales pero más ruido
- `20` - **Recomendado**, buen balance
- `50` - Lenta, señales más confiables

### SMA_LONG_PERIOD
**Tipo**: Integer  
**Default**: `50`  
**Rango típico**: `50-200`  
**Ejemplo**: `SMA_LONG_PERIOD=50`

Período de la SMA larga (lenta) en velas.

**Ejemplos comunes**:
- `50` - **Recomendado para comenzar**
- `100` - Media, señales poco frecuentes
- `200` - Muy lenta, señales muy confiables pero raras

**Combinaciones populares**:
- `20/50` - Balance (recomendado)
- `50/200` - Largo plazo (golden/death cross clásico)
- `10/30` - Corto plazo, más señales

---

## 🤖 EXECUTION MODE

### EXECUTE_REAL
**Tipo**: Boolean (true/false)  
**Default**: `false`  
**Recomendado**: `false` (SIEMPRE al comenzar)  
**Ejemplo**: `EXECUTE_REAL=false`

**MUY IMPORTANTE**:
- `false` - **MODO SIMULACIÓN**: El bot NO ejecuta órdenes reales, solo loguea
- `true` - **MODO REAL**: El bot SÍ ejecuta órdenes reales en el exchange

**Escenarios**:

| USE_TESTNET | EXECUTE_REAL | Resultado |
|-------------|--------------|-----------|
| true        | false        | ✅ **Simulación en testnet** (recomendado para aprender) |
| true        | true         | ✅ Órdenes reales en testnet (dinero ficticio) |
| false       | false        | ⚠️ Simulación en producción (solo logs) |
| false       | true         | ⚠️ **ÓRDENES REALES CON DINERO REAL** |

**Recomendación de progresión**:
1. **Semana 1-2**: `USE_TESTNET=true`, `EXECUTE_REAL=false` (aprender)
2. **Semana 3-4**: `USE_TESTNET=true`, `EXECUTE_REAL=true` (probar en testnet)
3. **Después**: `USE_TESTNET=false`, `EXECUTE_REAL=false` (simular en producción)
4. **Solo cuando estés seguro**: `USE_TESTNET=false`, `EXECUTE_REAL=true` (dinero real)

---

## ⏱️ BOT CONFIGURATION

### UPDATE_INTERVAL
**Tipo**: Integer (segundos)  
**Default**: `300` (5 minutos)  
**Ejemplo**: `UPDATE_INTERVAL=300`

Cada cuántos segundos el bot revisa el mercado y busca señales.

**Ejemplos**:
- `60` - Cada 1 minuto (para timeframes cortos)
- `300` - Cada 5 minutos (recomendado para 1h)
- `900` - Cada 15 minutos
- `3600` - Cada 1 hora (para timeframes largos)

**Recomendaciones por timeframe**:
- `1m`, `5m` → `60-120` segundos
- `15m`, `30m` → `180-300` segundos
- `1h` → `300-600` segundos (recomendado: 300)
- `4h` → `900-1800` segundos

---

## 📋 BACKTESTING CONFIGURATION

### COMMISSION_RATE
**Tipo**: Float (porcentaje)  
**Default**: `0.1`  
**Ejemplo**: `COMMISSION_RATE=0.1`

Comisión del exchange por operación (0.1% = 0.1).

**Comisiones típicas de Binance**:
- Sin BNB: 0.1%
- Con BNB: 0.075%
- VIP 0: 0.1%

### SLIPPAGE_RATE
**Tipo**: Float (porcentaje)  
**Default**: `0.05`  
**Ejemplo**: `SLIPPAGE_RATE=0.05`

Diferencia entre precio esperado y precio ejecutado (0.05% = 0.05).

**Recomendaciones**:
- Mercado líquido (BTC, ETH): 0.05%
- Mercado menos líquido: 0.1-0.2%

---

## 📝 LOGGING

### LOG_LEVEL
**Tipo**: String  
**Default**: `INFO`  
**Opciones**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`  
**Ejemplo**: `LOG_LEVEL=INFO`

Nivel de detalle de los logs:
- `DEBUG` - Todo, incluyendo detalles técnicos
- `INFO` - **Recomendado**, eventos importantes
- `WARNING` - Solo advertencias y errores
- `ERROR` - Solo errores
- `CRITICAL` - Solo errores críticos

### LOG_TO_FILE
**Tipo**: Boolean  
**Default**: `true`  
**Ejemplo**: `LOG_TO_FILE=true`

Si `true`, guarda logs en archivos en `logs/`.

### LOG_TO_CONSOLE
**Tipo**: Boolean  
**Default**: `true`  
**Ejemplo**: `LOG_TO_CONSOLE=true`

Si `true`, muestra logs en la consola/terminal.

---

## 💡 Configuraciones Recomendadas

### Para Aprender (Testnet Simulación)
```ini
USE_TESTNET=true
EXECUTE_REAL=false
SYMBOLS=BTC/USDT
TIMEFRAME=1h
INITIAL_CAPITAL=10000
RISK_PER_TRADE=2
MAX_POSITIONS=1
UPDATE_INTERVAL=300
LOG_LEVEL=INFO
```

### Para Backtesting
```ini
USE_TESTNET=true
SYMBOLS=BTC/USDT,ETH/USDT
TIMEFRAME=1h
INITIAL_CAPITAL=10000
RISK_PER_TRADE=2
COMMISSION_RATE=0.1
SLIPPAGE_RATE=0.05
```

### Para Paper Trading (Testnet Real)
```ini
USE_TESTNET=true
EXECUTE_REAL=true
SYMBOLS=BTC/USDT,ETH/USDT
TIMEFRAME=1h
RISK_PER_TRADE=1
MAX_POSITIONS=2
UPDATE_INTERVAL=300
```

### Para Producción (Precaución!)
```ini
USE_TESTNET=false
EXECUTE_REAL=true
SYMBOLS=BTC/USDT
TIMEFRAME=1h
INITIAL_CAPITAL=<tu-capital-real>
RISK_PER_TRADE=1
MAX_POSITIONS=1
STOP_LOSS_PERCENT=2
TAKE_PROFIT_PERCENT=4
UPDATE_INTERVAL=300
LOG_LEVEL=INFO
```

---

## 🔒 Seguridad

**NUNCA compartas tu archivo `.env`**:
- Contiene tus API keys
- Puede dar acceso a tu cuenta
- Asegúrate de que `.env` está en `.gitignore`

**Buenas prácticas**:
- Usa API keys con permisos limitados
- Habilita solo "Spot Trading" (no retiros)
- Usa whitelist de IPs si es posible
- Rotación de keys periódicamente en producción

---

¿Preguntas? Consulta [README.md](README.md) o [INSTALL.md](INSTALL.md)
