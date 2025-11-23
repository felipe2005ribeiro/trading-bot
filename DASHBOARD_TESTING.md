# Testing del Dashboard con Datos de Prueba

## Problema

El dashboard funciona perfectamente, pero está vacío porque el bot no ha ejecutado trades todavía en testnet.

## Solución

Creamos un script que inyecta datos de prueba realistas para poder ver el dashboard funcionando con:
- ✅ 6 trades cerrados (3 ganancias, 3 pérdidas)
- ✅ 2 posiciones abiertas con PnL en tiempo real
- ✅ Equity curve con 2 horas de historial
- ✅ Métricas calculadas (Win Rate, Profit Factor, etc.)

---

## Cómo Ejecutar

### Paso 1: Detener el Bot Actual

Si tienes el bot corriendo, deténlo con `Ctrl+C`

### Paso 2: Ejecutar Script de Prueba

```powershell
.\venv\Scripts\python scripts\test_dashboard.py
```

### Paso 3: Abrir Dashboard

Abre tu navegador en: **http://localhost:5000**

---

## Qué Verás

### 📊 Métricas Principales

- **Capital:** ~$10,460 (inicial $10,000 + PnL de trades)
- **Total Return:** ~+4.6%
- **Total Trades:** 6
- **Win Rate:** 50% (3 ganancias, 3 pérdidas)
- **Profit Factor:** ~2.5 (las ganancias son mayores que las pérdidas)
- **Max Drawdown:** Calculado automáticamente
- **Open Positions:** 2 posiciones activas

### 📈 Equity Curve

- Gráfica con 2 horas de historial
- Muestra crecimiento gradual del capital
- 24+ puntos de datos (cada 5 minutos)

### 🎯 Posiciones Abiertas

**1. BTC/USDT (EMA Scalping)**
- Entry: $95,280
- Current: $95,480 (+0.21%)
- Unrealized PnL: +$16.00
- Duration: ~25 minutos
- Stop Loss: $94,708.32
- Take Profit: $96,232.80

**2. ETH/USDT (SMA Cross)**
- Entry: $2,770
- Current: $2,785.50 (+0.56%)
- Unrealized PnL: +$46.50
- Duration: ~45 minutos
- Stop Loss: $2,714.40
- Take Profit: $2,880.80

### 📋 Historial de Trades

**Trades Ganadores:**
1. BTC/USDT - EMA_SCALP: +$95.00 (+1.0%) - Take Profit
2. ETH/USDT - SMA_CROSS: +$392.00 (+4.0%) - Take Profit
3. BNB/USDT - RSI_BB: +$9.45 (+1.0%) - Take Profit

**Trades Perdedores:**
4. SOL/USDT - EMA_SCALP: -$5.52 (-0.6%) - Stop Loss
5. ADA/USDT - SMA_CROSS: -$19.50 (-2.1%) - Stop Loss
6. DOT/USDT - RSI_BB: -$10.80 (-1.2%) - Stop Loss

**Total PnL:** +$460.63

---

## Output Esperado

```
============================================================
TRADING BOT DASHBOARD
============================================================

Starting dashboard server...

Dashboard URL: http://localhost:5000
Auto-refresh: Every 5 seconds
Status: Ready

Press Ctrl+C to stop
============================================================

============================================================
INJECTING TEST DATA FOR DASHBOARD
============================================================

Creating trade history...
  ✓ Created 6 closed trades
  ✓ Total PnL: $460.63
  ✓ Win Rate: 3/6
  ✓ New Capital: $10460.63

Creating open positions...
  ✓ Created 2 open positions
    - BTC/USDT: +$16.00 unrealized PnL
    - ETH/USDT: +$46.50 unrealized PnL

Populating equity curve...
  ✓ Created equity history with 25 data points

============================================================
TEST DATA INJECTION COMPLETE!
============================================================

Dashboard should now show:
  • Capital: $10460.63
  • Total Trades: 6
  • Win Rate: 50.0%
  • Open Positions: 2
  • Equity Curve: 25 points

Open dashboard: http://localhost:5000

Bot is running with test data...
Press Ctrl+C to stop
```

---

## Verificación

### 1. Todas las Cards Pobladas ✅

- Capital muestra valor real
- Return % calculado correctamente
- Win Rate: 50%
- Profit Factor calculado
- Drawdown mostrado
- 2 posiciones abiertas

### 2. Equity Curve Funcionando ✅

- Gráfica visible con línea morada/azul
- Eje X muestra timestamps
- Eje Y muestra capital en dólares
- Trend ascendente visible

### 3. Posiciones Abiertas ✅

- 2 cards con detalles completos
- PnL en vivo (verde para ganancias)
- Duración actualizada
- Precios de entry/current
- SL/TP visibles

### 4. Tabla de Trades ✅

- 6 trades listados
- Colores correctos (verde/rojo)
- Filtros funcionando (All/Wins/Losses)
- Información completa por trade
- Estrategias identificadas

### 5. Auto-Refresh ✅

- "Last updated" cambia cada 5 segundos
- Métricas se actualizan
- Status badge muestra "Running"

---

## Para Volver al Modo Normal

1. Detén el script de prueba (`Ctrl+C`)
2. Ejecuta el bot normal:
   ```powershell
   .\venv\Scripts\python scripts\run_bot.py
   ```

El dashboard volverá a mostrar datos reales del bot.

---

## Notas

- Los datos inyectados son **temporales** y se pierden al reiniciar
- Sirven **solo para validar** que el dashboard funciona correctamente
- Las posiciones abiertas tienen precios "current" fijos (no actualizan realmente)
- En producción, todo será data real del exchange

---

## Troubleshooting

**Q: El dashboard sigue vacío**
A: Asegúrate de que el script está corriendo y espera 5 segundos para auto-refresh

**Q: No veo la equity curve**
A: Refresca la página (F5) o haz click en el botón "Refresh" del chart

**Q: Las posiciones no actualizan su precio**
A: Son datos de prueba fijos. En el bot real, los precios se actualizan desde el exchange

**Q: Quiero cambiar los datos de prueba**
A: Edita `scripts/test_dashboard.py` y modifica los arrays `closed_trades` y `open_positions`

---

✅ **Dashboard 100% Funcional y Verificado!**
