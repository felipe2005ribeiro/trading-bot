# 🤖 Bot de Trading Automático para Criptomonedas

> **Sistema de trading automático de nivel profesional para criptomonedas con características avanzadas, monitoreo en tiempo real y opciones de deployment listas para producción.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Binance](https://img.shields.io/badge/Exchange-Binance-yellow.svg)](https://www.binance.com)

**[English](README.md) | Español**

---

## ⚠️ **DISCLAIMER**

**Este software es solo para fines educativos y de investigación. El trading de criptomonedas conlleva riesgos significativos y puede resultar en la pérdida total de tu capital. Usa este bot bajo tu propia responsabilidad.**

- ❌ **NO garantizamos rentabilidad**
- ❌ **NO nos hacemos responsables de pérdidas**
- ✅ **Siempre comienza con testnet**
- ✅ **Entiende completamente cómo funciona antes de usar dinero real**

---

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Inicio Rápido](#-inicio-rápido)
- [Instalación](#-instalación)
- [Configuración](#-configuración)
- [Uso](#-uso)
- [Deployment](#-deployment)
- [Arquitectura](#-arquitectura)
- [Estrategias](#-estrategias)
- [Seguridad](#-seguridad)
- [Contribuir](#-contribuir)
- [Licencia](#-licencia)

---

## ✨ Características

### 🤖 **Trading Automatizado**
- ✅ Monitoreo y análisis de mercado 24/7
- ✅ Ejecución automática de señales
- ✅ Gestión de posiciones en tiempo real
- ✅ Auto-reinicio en caso de falla
- ✅ Soporte multi-símbolo (BTC, ETH, SOL, etc.)

### 📊 **Backtesting Avanzado**
- ✅ Simulación histórica con datos reales de mercado
- ✅ Comisiones y slippage configurables
- ✅ Métricas completas: ratios de Sharpe, Sortino, Calmar
- ✅ Análisis de drawdown y win rate
- ✅ Visualización de equity curve
- ✅ Exportación a CSV para análisis adicional

### 📈 **Estrategias de Trading**
- ✅ **SMA Crossover** - Señales de Golden/Death Cross
- ✅ **RSI + Bollinger Bands** - Detección de sobrecompra/sobreventa
- ✅ **EMA Scalping** - EMA rápido/lento con confirmación de volumen
- ✅ **Análisis Multi-Timeframe** - Confirmación de tendencia (4h → 1h)
- ✅ Fácilmente extensible para estrategias personalizadas

### 🛡️ **Gestión de Riesgo**
- ✅ **Position Sizing** - Asignación de capital basada en porcentaje
- ✅ **Stop Loss & Take Profit** - Puntos de salida automáticos
- ✅ **Trailing Stop** - Bloqueo dinámico de ganancias
- ✅ **Kill Switch** - Detención automática por máximo drawdown
- ✅ **Circuit Breaker** - Pausa en volatilidad/volumen extremos
- ✅ **Límite de Posiciones** - Control de exposición del portafolio
- ✅ **Protección por Pérdidas Consecutivas** - Detiene después de X pérdidas

### 🖥️ **Dashboard en Tiempo Real**
- ✅ Estadísticas de trading en vivo
- ✅ Visualización de equity curve
- ✅ Seguimiento de posiciones abiertas
- ✅ Historial de trades
- ✅ Datos de mercado en tiempo real
- ✅ Métricas de rendimiento

### 🗄️ **Integración de Base de Datos**
- ✅ Persistencia con SQLite
- ✅ Logging automático de trades
- ✅ Snapshots de posiciones
- ✅ Almacenamiento de datos históricos
- ✅ Analíticas de rendimiento
- ✅ Capacidades de consulta para análisis

### 📱 **Notificaciones de Telegram**
- ✅ Alertas de trades en tiempo real
- ✅ Actualizaciones de posiciones
- ✅ Notificaciones de errores
- ✅ Resúmenes diarios de rendimiento
- ✅ Actualizaciones de estado del bot

### 🚀 **Listo para Deployment**
- ✅ Oracle Cloud - Opción gratis para siempre
- ✅ DigitalOcean - Desde $4/mes
- ✅ Soporte para Docker
- ✅ Configuración de servicio systemd
- ✅ Políticas de auto-reinicio
- ✅ Configuración basada en variables de entorno

### 🔒 **Seguridad**
- ✅ API keys vía variables de entorno
- ✅ Sin credenciales hardcodeadas
- ✅ .gitignore apropiado
- ✅ Separación testnet/producción
- ✅ Validación de órdenes
- ✅ Logging completo

---

## 🚀 Inicio Rápido

```bash
# 1. Clonar repositorio
git clone https://github.com/Astolfu/trading-bot.git
cd trading-bot

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar entorno
cp .env.example .env
# Edita .env con tu configuración

# 5. Ejecutar backtest
python scripts/run_backtest.py --symbols BTCUSDT --days 90

# 6. Ejecutar bot (testnet)
python scripts/run_bot.py
```

Accede al dashboard en: `http://localhost:5000`

---

## 📦 Instalación

### Prerrequisitos

- Python 3.10 o superior
- pip (gestor de paquetes Python)
- Git
- Cuenta de Binance (para API keys)

### Instalación Paso a Paso

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/Astolfu/trading-bot.git
   cd trading-bot
   ```

2. **Crear entorno virtual**
   ```bash
   python -m venv venv
   
   # Activar en Windows
   venv\Scripts\activate
   
   # Activar en Linux/Mac
   source venv/bin/activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Obtener API Keys de Binance**
   - **Testnet:** [testnet.binance.vision](https://testnet.binance.vision/)
   - **Producción:** [binance.com](https://www.binance.com/) → Cuenta → Gestión de API

5. **Configurar entorno**
   ```bash
   cp .env.example .env
   ```
   Edita `.env` y agrega tus API keys y preferencias.

6. **Configurar Telegram (Opcional)**
   - Crea bot con [@BotFather](https://t.me/BotFather)
   - Obtén tu Chat ID
   - Agrega al `.env`
   
   Ver [TELEGRAM_SETUP.md](TELEGRAM_SETUP.md) para guía detallada.

---

## ⚙️ Configuración

### Configuración Esencial

```ini
# API del Exchange
BINANCE_TESTNET_API_KEY=tu_key_testnet
BINANCE_TESTNET_API_SECRET=tu_secret_testnet
USE_TESTNET=true

# Trading
EXECUTE_REAL=true  # true = ejecutar órdenes, false = solo simulación
SYMBOLS=BTCUSDT,ETHUSDT,SOLUSDT
TIMEFRAME=1h
INITIAL_CAPITAL=10000

# Gestión de Riesgo
RISK_PER_TRADE=2  # 2% del capital por trade
MAX_POSITIONS=5
STOP_LOSS_PERCENT=2
TAKE_PROFIT_PERCENT=4
MAX_DRAWDOWN_PERCENT=10

# Estrategias
DEFAULT_STRATEGY=EMA_SCALP  # SMA_CROSS, RSI_BB, EMA_SCALP
```

Ver [CONFIGURATION.md](CONFIGURATION.md) para todas las opciones.

---

## 📖 Uso

### Backtesting

```bash
# Backtest básico
python scripts/run_backtest.py --symbols BTCUSDT --days 90

# Backtest multi-símbolo
python scripts/run_backtest.py --symbols BTCUSDT,ETHUSDT,SOLUSDT --days 180

# Rango de fechas personalizado
python scripts/run_backtest.py \
    --symbols BTCUSDT \
    --start 2024-01-01 \
    --end 2024-12-31 \
    --timeframe 1h
```

### Ejecutar el Bot

```bash
# Iniciar bot (testnet recomendado)
python scripts/run_bot.py

# El bot:
# - Se conectará a Binance
# - Inicializará la base de datos
# - Iniciará dashboard en puerto 5000
# - Comenzará a monitorear mercados
# - Ejecutará trades basados en señales
```

### Acceso al Dashboard

Abre en navegador: `http://localhost:5000`

Características:
- Equity curve en tiempo real
- Posiciones activas
- Historial de trades
- Métricas de rendimiento

### Consultas de Base de Datos

```bash
# Ver contenido de base de datos
python scripts/check_database.py

# Simular un trade de prueba
python scripts/simulate_trade.py
```

---

## 🌐 Deployment

### Opción 1: Oracle Cloud (Gratis para Siempre - Recomendado)

1. Crear cuenta en Oracle Cloud
2. Lanzar instancia VM (ARM recomendado - hasta 24GB RAM gratis)
3. Configurar bot con systemd
4. Configurar firewall

**Costo:** $0/mes (tier Always Free)  
**Setup:** 45-60 minutos

Ver [oracle_cloud_deployment_guide.md](docs/oracle_cloud_deployment_guide.md)

### Opción 2: DigitalOcean ($4/mes)

1. Crear Droplet (512MB RAM)
2. Clonar repositorio
3. Instalar dependencias
4. Configurar servicio systemd

**Costo:** $4/mes (crédito $200 para nuevos usuarios)  
**Setup:** 30 minutos

### Opción 3: Docker (Cualquier Plataforma)

```bash
# Construir imagen
docker build -t trading-bot .

# Ejecutar contenedor
docker run -d --env-file .env -p 5000:5000 trading-bot
```

**Nota:** Para trading en producción, Oracle Cloud es recomendado ya que es gratis para siempre y Binance no bloquea sus IPs.

---

## 🏗️ Arquitectura

```
trading-bot/
├── bot/                    # Bot principal de trading
│   ├── trading_bot.py      # Lógica central del bot
│   └── order_manager.py    # Ejecución de órdenes
├── strategies/             # Estrategias de trading
│   ├── sma_cross.py        # SMA Crossover
│   ├── rsi_bb.py           # RSI + Bollinger Bands
│   └── ema_scalping.py     # EMA Scalping
├── risk/                   # Gestión de riesgo
│   ├── risk_manager.py     # Position sizing
│   └── position_manager.py # Seguimiento de posiciones
├── database/               # Persistencia de datos
│   ├── db_manager.py       # Gestor SQLite
│   └── schema.sql          # Esquema de base de datos
├── dashboard/              # Dashboard web
│   ├── server.py           # Servidor Flask
│   └── templates/          # Templates HTML
├── core/                   # Utilidades core
│   ├── exchange_connector.py
│   ├── market_data.py
│   └── logger.py
├── notifications/          # Alertas
│   └── telegram_notifier.py
├── backtesting/            # Motor de backtesting
│   ├── backtester.py
│   └── metrics.py
└── scripts/                # Scripts ejecutables
    ├── run_bot.py
    └── run_backtest.py
```

---

## 📊 Estrategias

### 1. SMA Crossover

**Señales:**
- **Compra:** SMA20 cruza por encima de SMA50 (Golden Cross)
- **Venta:** SMA20 cruza por debajo de SMA50 (Death Cross)

**Mejor para:** Tendencias de mediano a largo plazo

### 2. RSI + Bollinger Bands

**Señales:**
- **Compra:** RSI < 30 Y precio toca banda inferior BB
- **Venta:** RSI > 70 Y precio toca banda superior BB

**Mejor para:** Mercados laterales

### 3. EMA Scalping

**Señales:**
- **Compra:** EMA8 cruza por encima de EMA21 + pico de volumen
- **Venta:** EMA8 cruza por debajo de EMA21

**Mejor para:** Mercados activos con buen volumen

### Filtro Multi-Timeframe

Confirma tendencia en timeframe superior (4h) antes de ejecutar señales en 1h.

**Configurable por símbolo.**

---

## 🔐 Seguridad

### Protección de API Keys

✅ **Nunca hardcodear keys** - Usar variables de entorno  
✅ **Testnet primero** - Validar antes de producción  
✅ **Keys de solo lectura** - Deshabilitar retiros  
✅ **Whitelist de IP** - Restringir acceso a API  
✅ **Git ignorado** - `.env` nunca commiteado  

### Seguridad en Trading

✅ **Kill Switch** - Auto-detención por máximo drawdown  
✅ **Circuit Breaker** - Pausa en volatilidad extrema  
✅ **Límites de Posición** - Máximo de posiciones concurrentes  
✅ **Validación de Órdenes** - Verificar antes de ejecutar  
✅ **Logs** - Trail de auditoría completo  

---

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Por favor:

1. Haz fork del repositorio
2. Crea rama de feature (`git checkout -b feature/CaracteristicaAsombrosa`)
3. Commit tus cambios (`git commit -m 'Agregar CaracteristicaAsombrosa'`)
4. Push a la rama (`git push origin feature/CaracteristicaAsombrosa`)
5. Abre un Pull Request

### Setup de Desarrollo

```bash
# Instalar dependencias de dev
pip install -r requirements-dev.txt

# Ejecutar tests
pytest

# Formatear código
black .

# Lint
flake8
```

---

## 📝 Documentación

- **[INSTALL.md](INSTALL.md)** - Guía de instalación detallada
- **[CONFIGURATION.md](CONFIGURATION.md)** - Todas las opciones de configuración
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Guía de deployment en VPS
- **[TELEGRAM_SETUP.md](TELEGRAM_SETUP.md)** - Configuración de bot de Telegram
- **[FEATURES.es.md](FEATURES.es.md)** - Características detalladas en español
- **[Guías de Deployment](docs/)** - Oracle Cloud, Docker

---

## 📈 Rendimiento

**Resultados de Backtest (180 días, BTCUSDT/ETHUSDT/SOLUSDT):**

- **Retorno Total:** +7.72%
- **Win Rate:** 55.26%
- **Máximo Drawdown:** -3.12%
- **Ratio de Sharpe:** 0.89
- **Factor de Beneficio:** 1.28

*El rendimiento pasado no garantiza resultados futuros.*

---

## 🛣️ Roadmap

### Características Planificadas

- [ ] Exchanges adicionales (Bybit, Kucoin)
- [ ] Estrategias ML avanzadas
- [ ] Optimización de portafolio
- [ ] App móvil
- [ ] Dashboard de analíticas avanzadas
- [ ] Optimización de backtesting (grid search)
- [ ] Características de trading social

Ver [improvement_roadmap.md](docs/improvement_roadmap.md) para detalles.

---

## 📜 Licencia

Este proyecto es open source bajo la Licencia MIT - ver archivo [LICENSE](LICENSE).

**Usar bajo tu propio riesgo. No se proporcionan garantías.**

---

## 🙏 Agradecimientos

Construido con:
- [ccxt](https://github.com/ccxt/ccxt) - Librería de exchanges de criptomonedas
- [pandas](https://pandas.pydata.org/) - Análisis de datos
- [ta](https://github.com/bukosabino/ta) - Análisis técnico
- [Flask](https://flask.palletsprojects.com/) - Framework web
- [Chart.js](https://www.chartjs.org/) - Gráficos del dashboard

---

## 📞 Soporte

- **Issues:** [GitHub Issues](https://github.com/Astolfu/trading-bot/issues)
- **Discusiones:** [GitHub Discussions](https://github.com/Astolfu/trading-bot/discussions)
- **Documentación:** Revisa la carpeta `/docs`

---

## ⚡ Enlaces Rápidos

- [Vista de Características](#-características)
- [Guía de Instalación](#-instalación)
- [Guía de Configuración](CONFIGURATION.md)
- [Opciones de Deployment](#-deployment)
- [Setup de Telegram](TELEGRAM_SETUP.md)
- [Guías de Contribución](#-contribuir)

---

**¡Feliz Trading! 📈🚀**

*Recuerda: Opera responsablemente. Solo invierte lo que puedas permitirte perder.*

---

**¡Dale una estrella ⭐ a este repo si te resulta útil!**
