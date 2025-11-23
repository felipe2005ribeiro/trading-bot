# 📦 Guía de Instalación - Crypto Trading Bot

Esta guía te llevará paso a paso por la instalación completa del sistema de trading automático.

---

## 📋 Requisitos Previos

### Sistema Operativo
- ✅ Windows 10/11
- ✅ Linux (Ubuntu 20.04+, Debian, etc.)
- ✅ macOS 10.15+

### Software Necesario

1. **Python 3.8 o superior**
   - Verifica tu versión: `python --version` o `python3 --version`
   - Descarga desde: https://www.python.org/downloads/

2. **pip** (gestor de paquetes de Python)
   - Generalmente viene con Python
   - Verifica: `pip --version` o `pip3 --version`

3. **git** (opcional, para clonar el repositorio)
   - Verifica: `git --version`
   - Descarga desde: https://git-scm.com/downloads

---

## 🚀 Paso 1: Obtener el Código

### Opción A: Clonar con Git (Recomendado)

```bash
git clone <url-del-repositorio>
cd crypto-trading-bot
```

### Opción B: Descargar ZIP

1. Descarga el archivo ZIP del proyecto
2. Extrae en la ubicación deseada
3. Abre terminal/consola en esa carpeta

---

## 🐍 Paso 2: Crear Entorno Virtual

Es **altamente recomendado** usar un entorno virtual para aislar las dependencias.

### En Windows:

```powershell
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
venv\Scripts\activate

# Verás (venv) al inicio de tu línea de comando
```

### En Linux/macOS:

```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate

# Verás (venv) al inicio de tu línea de comando
```

> **Nota**: Cada vez que abras una nueva terminal, debes activar el entorno virtual nuevamente.

---

## 📥 Paso 3: Instalar Dependencias

Con el entorno virtual activado:

```bash
# Actualizar pip a la última versión
pip install --upgrade pip

# Instalar todas las dependencias del proyecto
pip install -r requirements.txt
```

Esto instalará:
- `ccxt` - Conexión con exchanges
- `pandas` - Análisis de datos
- `numpy` - Cálculos numéricos
- `ta` - Indicadores técnicos
- `matplotlib` - Gráficos
- `python-dotenv` - Variables de entorno
- `requests` - HTTP requests

**Tiempo estimado**: 2-5 minutos dependiendo de tu conexión

---

## 🔑 Paso 4: Obtener API Keys de Binance Testnet

### 4.1 Crear Cuenta en Binance Testnet

1. Ve a: **https://testnet.binance.vision/**
2. Haz clic en **"Register"**
3. Proporciona un email válido
4. Verifica tu email
5. Inicia sesión

### 4.2 Generar API Keys

1. Una vez dentro, ve a **API Key Management**
2. Haz clic en **"Create API"**
3. Dale un nombre descriptivo (ej: "Trading Bot Test")
4. **Guarda tu API Key y Secret** en un lugar seguro
5. Habilita **"Enable Spot & Margin Trading"** si es necesario

> ⚠️ **IMPORTANTE**: Estas son keys de **TESTNET** con dinero ficticio. Son GRATUITAS y seguras para practicar.

### 4.3 Obtener Fondos de Prueba

1. En el dashboard de testnet, busca **"Faucet"** o **"Get Test Funds"**
2. Solicita BTC, ETH, USDT de prueba
3. Verifica que los fondos lleguen a tu cuenta

---

## ⚙️ Paso 5: Configurar el Bot

### 5.1 Crear Archivo de Configuración

```bash
# Windows
copy .env.example .env

# Linux/macOS
cp .env.example .env
```

### 5.2 Editar .env

Abre el archivo `.env` con tu editor de texto favorito y configura:

```ini
# ===================================
# BINANCE API CONFIGURATION
# ===================================
# Pega aquí tus API keys de testnet
BINANCE_TESTNET_API_KEY=tu_api_key_de_testnet_aqui
BINANCE_TESTNET_API_SECRET=tu_secret_de_testnet_aqui

# Dejar vacío por ahora (para producción futura)
BINANCE_API_KEY=
BINANCE_API_SECRET=

# SIEMPRE true al comenzar
USE_TESTNET=true

# ===================================
# TRADING CONFIGURATION
# ===================================
SYMBOLS=BTC/USDT,ETH/USDT
TIMEFRAME=1h
INITIAL_CAPITAL=10000

# ===================================
# RISK MANAGEMENT
# ===================================
RISK_PER_TRADE=2
MAX_POSITIONS=3
STOP_LOSS_PERCENT=2
TAKE_PROFIT_PERCENT=4
MAX_PORTFOLIO_EXPOSURE=50

# ===================================
# STRATEGY CONFIGURATION
# ===================================
SMA_SHORT_PERIOD=20
SMA_LONG_PERIOD=50

# ===================================
# EXECUTION MODE
# ===================================
# SIEMPRE false para paper trading
EXECUTE_REAL=false

# ===================================
# BOT CONFIGURATION
# ===================================
# Revisar mercado cada 5 minutos (300 seg)
UPDATE_INTERVAL=300

# ===================================
# LOGGING
# ===================================
LOG_LEVEL=INFO
LOG_TO_FILE=true
LOG_TO_CONSOLE=true
```

> **Importante**: 
> - `USE_TESTNET=true` - Usa Binance Testnet
> - `EXECUTE_REAL=false` - Solo simula, no ejecuta órdenes reales

---

## ✅ Paso 6: Verificar Instalación

### 6.1 Verificar Estructura de Archivos

Asegúrate de tener:
```
crypto-trading-bot/
├── config/
├── core/
├── risk/
├── strategies/
├── backtesting/
├── bot/
├── scripts/
├── .env (tu archivo de configuración)
├── .env.example
├── requirements.txt
└── README.md
```

### 6.2 Test de Conexión

Crea un script de prueba `test_connection.py`:

```python
from config.config import Config
from core.exchange_connector import ExchangeConnector

# Validar configuración
try:
    Config.validate()
    print("✅ Configuración válida")
except Exception as e:
    print(f"❌ Error en configuración: {e}")
    exit(1)

# Probar conexión
try:
    exchange = ExchangeConnector()
    balance = exchange.get_balance('USDT')
    print(f"✅ Conexión exitosa!")
    print(f"   Balance USDT: {balance['total']:.2f}")
except Exception as e:
    print(f"❌ Error de conexión: {e}")
    exit(1)

print("\n🎉 ¡Todo está funcionando correctamente!")
```

Ejecuta:
```bash
python test_connection.py
```

Deberías ver:
```
✅ Configuración válida
✅ Conexión exitosa!
   Balance USDT: 10000.00

🎉 ¡Todo está funcionando correctamente!
```

---

## 🧪 Paso 7: Pruebas Iniciales

### 7.1 Ejecutar Backtesting

```bash
# Backtest simple de BTC últimos 30 días
python scripts/run_backtest.py --symbols BTC/USDT --days 30
```

Deberías ver:
- Descarga de datos históricos
- Ejecución del backtesting
- Métricas de rendimiento
- Archivos generados en `results/`

### 7.2 Ejecutar Bot en Modo Simulación (Opcional)

```bash
python scripts/run_bot.py
```

Verás que el bot:
- Se conecta al exchange
- Revisa el balance
- Analiza el mercado
- Genera señales (si las hay)
- Se ejecuta cada 5 minutos

**Presiona Ctrl+C para detener el bot**

---

## 🎯 Próximos Pasos

¡Felicidades! Ya tienes el bot instalado y funcionando. Ahora:

1. **Lee [CONFIGURATION.md](CONFIGURATION.md)** para entender todas las opciones de configuración
2. **Experimenta con el backtesting** cambiando parámetros de la estrategia
3. **Deja correr el bot** en testnet por unos días para ver cómo funciona
4. **Revisa los logs** en `logs/` y resultados en `results/`
5. Cuando te sientas cómodo, consulta **[DEPLOYMENT.md](DEPLOYMENT.md)** para desplegar en VPS

---

## 🐛 Solución de Problemas

### Error: "Module not found"

```bash
# Asegúrate de tener el entorno virtual activado
# Reinstala las dependencias
pip install -r requirements.txt
```

### Error: "API authentication failed"

- Verifica que tus API keys sean correctas en `.env`
- Asegúrate de estar usando keys de **TESTNET**
- Verifica que `USE_TESTNET=true`

### Error: "Permission denied" (Linux/Mac)

```bash
# Da permisos de ejecución a los scripts
chmod +x scripts/*.py
```

### Error: "No module named 'config'"

```bash
# Ejecuta los scripts desde la raíz del proyecto, no desde scripts/
cd crypto-trading-bot
python scripts/run_backtest.py
```

### El bot no encuentra señales

- Es normal, las señales SMA son poco frecuentes
- Prueba con datos históricos más largos (90+ días)
- Ajusta los períodos SMA en `.env`
- Revisa los logs para ver el análisis

---

## 📞 Obtener Ayuda

Si tienes problemas:

1. **Revisa los logs** en `logs/trading_bot_YYYYMMDD.log`
2. **Verifica tu configuración** en `.env`
3. **Consulta la documentación** en los archivos .md
4. **Abre un issue** en GitHub con:
   - Descripción del problema
   - Mensaje de error completo
   - Tu configuración (SIN las API keys)
   - Pasos para reproducir el error

---

## 🔄 Actualización del Bot

```bash
# Si clonaste con git
git pull origin main

# Actualizar dependencias
pip install -r requirements.txt --upgrade
```

---

¡Listo! Ahora tienes el bot completamente instalado y listo para usar. 🚀
