# Guía de Configuración de Notificaciones Telegram

Este documento explica cómo configurar las notificaciones de Telegram para tu trading bot.

## 📋 Requisitos Previos

- Una cuenta de Telegram (app móvil o desktop)
- 10 minutos de tu tiempo

---

## 🤖 Paso 1: Crear tu Bot de Telegram

1. **Abre Telegram** y busca el usuario `@BotFather`

2. **Inicia conversación** con BotFather y envía el comando:
   ```
   /newbot
   ```

3. **Sigue las instrucciones:**
   - Te pedirá un nombre para tu bot (ej: "Mi Trading Bot")
   - Te pedirá un username (debe terminar en `bot`, ej: `mi_trading_bot`)

4. **Guarda el Token:**
   BotFather te enviará un mensaje como:
   ```
   Done! Congratulations on your new bot...
   
   Use this token to access the HTTP API:
   1234567890:ABCdefGHIjklMNOpqrsTUVwxyz-123456
   ```
   
   **¡COPIA Y GUARDA ESTE TOKEN!** Lo necesitarás para el `.env`

---

## 🆔 Paso 2: Obtener tu Chat ID

Hay dos métodos. Usa el que prefieras:

### **Método A: Usando otro Bot (Más fácil)**

1. Busca el bot `@userinfobot` en Telegram

2. Inicia conversación y te mostrará tu información:
   ```
   Id: 123456789
   ```

3. **Copia ese número** (tu Chat ID)

### **Método B: Usando tu navegador**

1. Busca tu bot (el que creaste en Paso 1)

2. Envíale cualquier mensaje (ej: "Hola")

3. Abre tu navegador y ve a:
   ```
   https://api.telegram.org/bot<TU_TOKEN>/getUpdates
   ```
   (Reemplaza `<TU_TOKEN>` con el token del Paso 1)

4. Busca en el JSON que aparece:
   ```json
   "chat":{"id":123456789
   ```
   
5. **Copia ese número** (tu Chat ID)

---

## ⚙️ Paso 3: Configurar el Bot

1. **Abre tu archivo `.env`**

2. **Busca esta sección** (al final del archivo):
   ```ini
   # TELEGRAM NOTIFICATIONS
   TELEGRAM_ENABLED=false
   TELEGRAM_BOT_TOKEN=
   TELEGRAM_CHAT_ID=
   ```

3. **Actualiza con tus datos:**
   ```ini
   # TELEGRAM NOTIFICATIONS
   TELEGRAM_ENABLED=true
   TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz-123456
   TELEGRAM_CHAT_ID=123456789
   ```

4. **Guarda el archivo**

---

## ✅ Paso 4: Probar las Notificaciones

1. **Reinicia el bot:**
   ```powershell
   .\venv\Scripts\python scripts\run_bot.py
   ```

2. **Deberías recibir un mensaje en Telegram:**
   ```
   🤖 Trading Bot Started

   Mode: 🟢 LIVE (o 🟡 SIMULATION)
   Exchange: Testnet
   Symbols: BTC/USDT, ETH/USDT...
   Strategy: BOTH
   Capital: $10,000.00
   Time: 2025-11-21 10:30:00
   ```

3. **¡Si lo recibes, está funcionando!** 🎉

---

## 📨 Tipos de Notificaciones que Recibirás

### 1. Señales de Trading
```
🟢 SEÑAL DE COMPRA

Par: BTC/USDT
Estrategia: SMA_CROSS
Precio: $95,432.50
Stop Loss: $93,523.90
Take Profit: $99,249.80
Hora: 15:23:45
```

### 2. Órdenes Ejecutadas
```
✅ ORDEN EJECUTADA

BTC/USDT: Compra de 0.105 BTC
Precio: $95,432.50
Valor: $10,020.41
Hora: 15:23:47
```

### 3. Posiciones Cerradas
```
💰 POSICIÓN CERRADA

ETH/USDT (BUY)
Razón: Take Profit alcanzado
PnL: +$234.50 (+2.34%)
Duración: 4h 23m
Hora: 19:46:12
```

### 4. Kill Switch Activado
```
🚨 KILL SWITCH ACTIVADO

⚠️ Maximum drawdown exceeded: 10.5% >= 10%

Drawdown: 10.50%
Pérdidas consecutivas: 3
Estado: Trading detenido automáticamente
Hora: 2025-11-21 14:22:10
```

---

## 🔒 Seguridad

### ⚠️ Importante:
- **NUNCA compartas tu Bot Token** con nadie
- El token da acceso completo a tu bot
- Si crees que se filtró, elimínalo desde @BotFather con `/revoke` y crea uno nuevo

### ✅ Recomendaciones:
- Mantén tu `.env` privado (ya está en `.gitignore`)
- Solo tú deberías tener acceso al Chat ID
- Puedes crear un grupo privado en Telegram y usar el Group ID para recibir notificaciones ahí

---

## 🛠️ Solución de Problemas

### No recibo notificaciones

**1. Verifica que está activado:**
```ini
TELEGRAM_ENABLED=true  # No "false"
```

**2. Revisa los logs del bot:**
Deberías ver:
```
Telegram notifications enabled
```

Si ves:
```
Telegram enabled but credentials missing. Disabling notifications.
```
Significa que el Token o Chat ID están vacíos o incorrectos.

**3. Prueba el bot manualmente:**
Abre tu navegador y ve a:
```
https://api.telegram.org/bot<TU_TOKEN>/sendMessage?chat_id=<TU_CHAT_ID>&text=Test
```

Si recibes el mensaje "Test", tus credenciales son correctas.

### Error de Telegram API

Si ves errores como `Telegram API error: 401` o `403`:
- **401**: Token inválido. Verifica que lo copiaste completo.
- **403**: El bot fue bloqueado. Abre Telegram, busca tu bot y haz clic en "Start" o "Restart".

---

## 📚 Desactivar Notificaciones

Si quieres desactivar temporalmente las notificaciones sin borrar tus credenciales:

```ini
TELEGRAM_ENABLED=false
```

El bot seguirá funcionando normalmente, solo no enviará mensajes a Telegram.

---

## ✨ ¡Listo!

Ahora tu bot te mantendrá informado en tiempo real sobre:
- ✅ Señales detectadas
- ✅ Trades ejecutados
- ✅ Posiciones cerradas con PnL
- ✅ Alertas de Kill Switch
- ✅ Errores críticos

Puedes monitorear tu bot desde cualquier lugar donde tengas Telegram. 📱🚀
