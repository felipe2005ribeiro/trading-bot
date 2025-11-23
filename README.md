# 🤖 Crypto Trading Bot - Sistema de Trading Automático

Sistema completo de trading automático para criptomonedas con backtesting avanzado, paper trading en Binance Testnet, estrategias configurables y gestión de riesgo integrada.

## ⚠️ DISCLAIMER

**Este software es solo para fines educativos y de investigación. El trading de criptomonedas conlleva riesgos significativos y puede resultar en la pérdida total de su capital. Use este bot bajo su propia responsabilidad.**

- ❌ **NO garantizamos rentabilidad**
- ❌ **NO nos hacemos responsables de pérdidas**
- ✅ **Recomendamos comenzar siempre en testnet**
- ✅ **Entienda completamente cómo funciona antes de usar dinero real**

---

## ✨ Características

### 🔍 Backtesting Avanzado
- ✅ Simulación histórica con datos reales de mercado
- ✅ Comisiones y slippage configurables
- ✅ Métricas completas: Sharpe, Sortino, Calmar ratios, drawdown, win rate
- ✅ Equity curve con visualización gráfica
- ✅ Exportación de trades y resultados a CSV

### 🤖 Bot de Paper Trading 24/7
- ✅ Conexión a Binance Spot Testnet
- ✅ Análisis de mercado automático cada X minutos
- ✅ Ejecución automática de señales de trading
- ✅ Monitoreo continuo de posiciones abiertas
- ✅ Stop loss y take profit automáticos
- ✅ Logging completo y detallado
- ✅ Registro de todos los trades en CSV

### 📊 Estrategias
- ✅ **SMA Crossover Strategy** (Golden Cross / Death Cross)
  - Golden Cross: SMA20 cruza arriba de SMA50 → Señal de COMPRA
  - Death Cross: SMA20 cruza abajo de SMA50 → Señal de VENTA
- ✅ Arquitectura extensible para añadir más estrategias fácilmente

### 🛡️ Gestión de Riesgo
- ✅ Position sizing basado en porcentaje de capital
- ✅ Stop loss y take profit configurables
- ✅ Límite de posiciones simultáneas
- ✅ Límite de exposición total del portfolio
- ✅ Validación de trades antes de ejecución

### ⚙️ Configuración
- ✅ Todo configurable vía archivo `.env`
- ✅ Soporte para testnet y producción
- ✅ Modo simulación (sin ejecutar órdenes reales)
- ✅ Múltiples símbolos y timeframes
- ✅ Parámetros de estrategia personalizables

---

## 📁 Estructura del Proyecto

```
crypto-trading-bot/
├── config/                 # Configuración del sistema
│   ├── __init__.py
│   └── config.py          # Carga variables de .env
├── core/                  # Módulos fundamentales
│   ├── __init__.py
│   ├── logger.py          # Sistema de logging
│   ├── exchange_connector.py  # Conexión con exchanges (ccxt)
│   └── market_data.py     # Descarga y procesamiento de datos
├── risk/                  # Gestión de riesgo
│   ├── __init__.py
│   ├── risk_manager.py    # Cálculo de tamaños de posición
│   └── position_manager.py # Tracking de posiciones
├── strategies/            # Estrategias de trading
│   ├── __init__.py
│   ├── base_strategy.py   # Clase base abstracta
│   └── sma_cross.py       # Estrategia SMA crossover
├── backtesting/           # Sistema de backtesting
│   ├── __init__.py
│   ├── backtester.py      # Motor de backtesting
│   ├── metrics.py         # Cálculo de métricas
│   └── equity_curve.py    # Visualización de resultados
├── bot/                   # Bot de trading
│   ├── __init__.py
│   ├── trading_bot.py     # Bot principal 24/7
│   └── order_manager.py   # Gestión de órdenes
├── scripts/               # Scripts ejecutables
│   ├── run_backtest.py    # Ejecutar backtesting
│   └── run_bot.py         # Ejecutar bot de trading
├── data/                  # Datos históricos (auto-creado)
├── logs/                  # Archivos de log (auto-creado)
├── results/               # CSVs de resultados (auto-creado)
├── .env.example           # Plantilla de configuración
├── .gitignore
├── requirements.txt       # Dependencias Python
├── README.md             # Este archivo
├── INSTALL.md            # Guía de instalación
├── CONFIGURATION.md      # Guía de configuración
└── DEPLOYMENT.md         # Guía de despliegue en VPS
```

---

## 🚀 Quick Start

### 1. Instalación

```bash
# Clonar el repositorio (o descargar los archivos)
git clone <tu-repositorio>
cd crypto-trading-bot

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configuración

```bash
# Copiar plantilla de configuración
copy .env.example .env

# Editar .env con tus preferencias y API keys
# Nota: Para testnet, obtén tus keys en https://testnet.binance.vision/
```

### 3. Ejecutar Backtesting

```bash
python scripts/run_backtest.py --symbols BTC/USDT --days 90
```

### 4. Ejecutar Bot (Testnet)

```bash
# Asegúrate de tener USE_TESTNET=true y EXECUTE_REAL=false en .env
python scripts/run_bot.py
```

Para instrucciones detalladas, consulta [INSTALL.md](INSTALL.md)

---

## 📖 Documentación

- **[INSTALL.md](INSTALL.md)** - Guía completa de instalación paso a paso
- **[CONFIGURATION.md](CONFIGURATION.md)** - Explicación de todas las variables de configuración
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Cómo desplegar el bot en un VPS 24/7

---

## 🔧 Tecnologías Utilizadas

- **Python 3.8+** - Lenguaje principal
- **ccxt** - Librería universal para exchanges de criptomonedas
- **pandas** - Análisis y manipulación de datos
- **numpy** - Cálculos numéricos
- **ta** - Indicadores técnicos (SMA, EMA, RSI, MACD, etc.)
- **matplotlib** - Visualización de equity curves
- **python-dotenv** - Gestión de variables de entorno

---

## 📊 Ejemplo de Uso

### Backtesting

```bash
# Backtest de BTC/USDT últimos 90 días
python scripts/run_backtest.py --symbols BTC/USDT --days 90

# Backtest personalizado
python scripts/run_backtest.py \
    --symbols BTC/USDT,ETH/USDT \
    --start 2023-01-01 \
    --end 2023-12-31 \
    --timeframe 1h \
    --capital 10000
```

### Ejecutar Bot

```bash
# Bot en modo testnet (recomendado)
python scripts/run_bot.py

# El bot se ejecutará continuamente hasta que presiones Ctrl+C
```

---

## 🛠️ Configuración Básica (.env)

```ini
# APIs de Binance Testnet (obtén en https://testnet.binance.vision/)
BINANCE_TESTNET_API_KEY=tu_api_key_aqui
BINANCE_TESTNET_API_SECRET=tu_api_secret_aqui

# Usar testnet (siempre true al comenzar)
USE_TESTNET=true

# NO ejecutar órdenes reales (siempre false para paper trading)
EXECUTE_REAL=false

# Símbolos a tradear
SYMBOLS=BTC/USDT,ETH/USDT

# Timeframe de análisis
TIMEFRAME=1h

# Capital inicial
INITIAL_CAPITAL=10000

# Riesgo por operación (2% recomendado)
RISK_PER_TRADE=2

# Estrategia SMA
SMA_SHORT_PERIOD=20
SMA_LONG_PERIOD=50

# Intervalo de actualización (segundos)
UPDATE_INTERVAL=300
```

---

## 📈 Roadmap - Mejoras Futuras

### Estrategias Avanzadas
- [ ] RSI + Bollinger Bands
- [ ] MACD + Signal
- [ ] Ichimoku Cloud
- [ ] Multi-timeframe analysis
- [ ] Machine Learning (LSTM, Random Forest)
- [ ] Sentiment analysis

### Gestión de Riesgo Mejorada
- [ ] Trailing stop loss dinámico
- [ ] Portfolio rebalancing
- [ ] Kelly Criterion para position sizing
- [ ] Kill switch por drawdown
- [ ] Correlación entre pares

### Notificaciones
- [ ] Telegram bot para alertas
- [ ] Email notifications
- [ ] Discord webhooks
- [ ] SMS para eventos críticos

### Análisis y Optimización
- [ ] Grid search para parámetros
- [ ] Walk-forward analysis
- [ ] Monte Carlo simulation
- [ ] A/B testing de estrategias

### Infraestructura
- [ ] Database (PostgreSQL/MongoDB)
- [ ] Dashboard web en tiempo real
- [ ] API REST para control remoto
- [ ] Docker containerization
- [ ] Multi-exchange support

---

## ⚠️ Advertencias de Seguridad

### 🔐 Protección de API Keys

1. **NUNCA** compartas tus API keys
2. **NUNCA** subas el archivo `.env` a repositorios públicos
3. Usa claves de **solo lectura** o **solo trading** (no retiros)
4. Habilita **whitelist de IPs** en Binance si es posible
5. Comienza **SIEMPRE** con testnet

### 💰 Gestión de Capital

1. **No inviertas** más de lo que puedas perder
2. **Comienza con cantidades pequeñas** en producción
3. **Monitorea constantemente** el comportamiento del bot
4. **Entiende completamente** cómo funciona la estrategia
5. **Diversifica** - no pongas todo tu capital en un solo bot

### 🐛 Testing

1. **Prueba extensivamente** en testnet primero
2. **Verifica** todos los logs y resultados
3. **Simula** diferentes condiciones de mercado
4. **Revisa** la gestión de errores y reconexión
5. **Monitorea** el bot al menos las primeras 24-48 horas

---

## 📝 Licencia

Este proyecto es de código abierto para fines educativos. Úsalo bajo tu propia responsabilidad.

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Haz fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/NuevaCaracteristica`)
3. Commit tus cambios (`git commit -m 'Añadir NuevaCaracteristica'`)
4. Push a la rama (`git push origin feature/NuevaCaracteristica`)
5. Abre un Pull Request

---

## 📞 Soporte

Si encuentras bugs o tienes preguntas:
- Abre un issue en GitHub
- Revisa la documentación en los archivos .md
- Consulta los logs en `logs/` para debugging

---

## 🙏 Agradecimientos

Construido con:
- [ccxt](https://github.com/ccxt/ccxt) - Librería universal para exchanges
- [ta](https://github.com/bukosabino/ta) - Análisis técnico
- [pandas](https://pandas.pydata.org/) - Análisis de datos
- [matplotlib](https://matplotlib.org/) - Visualización

---

**¡Happy Trading! 📈🚀**

*Recuerda: El pasado no garantiza resultados futuros. Trade responsablemente.*
