# 🚀 Guía de Despliegue en VPS - Crypto Trading Bot

Esta guía te enseñará cómo desplegar el bot en un servidor VPS para que funcione 24/7.

---

## 🌐 ¿Por Qué Usar un VPS?

Un VPS (Virtual Private Server) te permite:
- ✅ Tener el bot corriendo 24/7 sin interrupciones
- ✅ No depender de tu computadora personal
- ✅ Mejor conexión y latencia al exchange
- ✅ Mayor confiabilidad y uptime
- ✅ Acceso remoto desde cualquier lugar

---

## 💰 Proveedores de VPS Recomendados

### Opción 1: DigitalOcean (Recomendado)
- **Precio**: Desde $4-6/mes
- **Link**: https://www.digitalocean.com/
- **Plan recomendado**: Droplet básico (1GB RAM, 1 vCPU)
- **Pro**: Interfaz simple, buena documentación

### Opción 2: Vultr
- **Precio**: Desde $3.50/mes
- **Link**: https://www.vultr.com/
- **Plan recomendado**: Cloud Compute Regular
- **Pro**: Muy económico

### Opción 3: AWS EC2 (Free Tier)
- **Precio**: Gratis por 12 meses (con límites)
- **Link**: https://aws.amazon.com/ec2/
- **Plan**: t2.micro o t3.micro
- **Pro**: Gratis el primer año

### Opción 4: Google Cloud
- **Precio**: Crédito gratis inicial
- **Link**: https://cloud.google.com/compute
- **Pro**: $300 en créditos para nuevos usuarios

---

## 🖥️ Requisitos del VPS

### Mínimo Recomendado
- **RAM**: 1GB
- **CPU**: 1 core
- **Almacenamiento**: 10GB
- **Sistema Operativo**: Ubuntu 20.04 / 22.04 LTS
- **Ancho de banda**: Ilimitado (o al menos 1TB/mes)

### Ideal
- **RAM**: 2GB
- **CPU**: 2 cores
- **Almacenamiento**: 25GB SSD

---

## 📦 Paso 1: Crear y Configurar VPS

### 1.1 Crear el VPS

En tu proveedor elegido:
1. Crea una cuenta
2. Selecciona **Ubuntu 22.04 LTS** como sistema operativo
3. Elige el plan (mínimo 1GB RAM)
4. Selecciona región (cercana a Binance servers: Singapur, Japón, US-East)
5. Configura SSH key (recomendado) o usa contraseña
6. Crea el servidor

### 1.2 Conectarse al VPS

#### Desde Windows:
Usa PuTTY o Windows Terminal (PowerShell):
```powershell
ssh root@tu_ip_del_vps
```

#### Desde Linux/macOS:
```bash
ssh root@tu_ip_del_vps
```

---

## 🔧 Paso 2: Configurar el Servidor

### 2.1 Actualizar el Sistema

```bash
# Actualizar lista de paquetes
sudo apt update

# Actualizar paquetes instalados
sudo apt upgrade -y
```

### 2.2 Instalar Python y Herramientas

```bash
# Instalar Python 3 y pip
sudo apt install -y python3 python3-pip python3-venv

# Instalar git
sudo apt install -y git

# Verificar instalación
python3 --version
pip3 --version
git --version
```

### 2.3 Crear Usuario No-Root (Recomendado)

```bash
# Crear usuario
sudo adduser botuser

# Dar permisos sudo
sudo usermod -aG sudo botuser

# Cambiar a nuevo usuario
su - botuser
```

---

## 📥 Paso 3: Instalar el Bot

### 3.1 Clonar el Repositorio

```bash
# Ir al directorio home
cd ~

# Clonar el proyecto (o subir tus archivos)
git clone <tu-repositorio> crypto-trading-bot

# O si no usas git, sube archivos con SCP/SFTP

cd crypto-trading-bot
```

### 3.2 Instalar Dependencias

```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate

# Actualizar pip
pip install --upgrade pip

# Instalar dependencias
pip install -r requirements.txt
```

### 3.3 Configurar el Bot

```bash
# Copiar plantilla de configuración
cp .env.example .env

# Editar configuración
nano .env
```

Configura tus API keys y parámetros. Presiona `Ctrl+X`, luego `Y`, luego `Enter` para guardar.

### 3.4 Probar el Bot

```bash
# Test de conexión
python scripts/run_bot.py

# Debería conectar y comenzar a funcionar
# Presiona Ctrl+C para detener
```

---

## 🔄 Paso 4: Ejecutar Bot 24/7

Hay dos opciones: **systemd** (recomendado) o **PM2**

### Opción A: systemd (Recomendado para Linux)

#### 4.1 Crear Servicio

```bash
# Crear archivo de servicio
sudo nano /etc/systemd/system/trading-bot.service
```

Pega este contenido (ajusta las rutas):

```ini
[Unit]
Description=Crypto Trading Bot
After=network.target

[Service]
Type=simple
User=botuser
WorkingDirectory=/home/botuser/crypto-trading-bot
Environment="PATH=/home/botuser/crypto-trading-bot/venv/bin"
ExecStart=/home/botuser/crypto-trading-bot/venv/bin/python /home/botuser/crypto-trading-bot/scripts/run_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 4.2 Activar y Ejecutar

```bash
# Recargar systemd
sudo systemctl daemon-reload

# Habilitar inicio automático
sudo systemctl enable trading-bot

# Iniciar el bot
sudo systemctl start trading-bot

# Ver estado
sudo systemctl status trading-bot

# Ver logs en tiempo real
sudo journalctl -u trading-bot -f
```

#### 4.3 Comandos Útiles

```bash
# Detener el bot
sudo systemctl stop trading-bot

# Reiniciar el bot
sudo systemctl restart trading-bot

# Ver logs completos
sudo journalctl -u trading-bot --no-pager

# Deshabilitar inicio automático
sudo systemctl disable trading-bot
```

### Opción B: PM2 (Alternativa)

#### 4.1 Instalar PM2

```bash
# Instalar Node.js y npm
sudo apt install -y nodejs npm

# Instalar PM2 globalmente
sudo npm install -g pm2
```

#### 4.2 Crear archivo de configuración

```bash
nano ecosystem.config.js
```

Contenido:

```javascript
module.exports = {
  apps: [{
    name: 'trading-bot',
    script: 'venv/bin/python',
    args: 'scripts/run_bot.py',
    interpreter: 'none',
    cwd: '/home/botuser/crypto-trading-bot',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '500M',
    error_file: 'logs/pm2-error.log',
    out_file: 'logs/pm2-out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
  }]
};
```

#### 4.3 Ejecutar con PM2

```bash
# Iniciar bot
pm2 start ecosystem.config.js

# Ver status
pm2 status

# Ver logs
pm2 logs trading-bot

# Detener
pm2 stop trading-bot

# Reiniciar
pm2 restart trading-bot

# Habilitar inicio automático
pm2 startup
pm2 save
```

---

## 📊 Paso 5: Monitoreo y Mantenimiento

### 5.1 Revisar Logs

```bash
# Con systemd:
sudo journalctl -u trading-bot -f

# Con PM2:
pm2 logs trading-bot

# Logs del bot directamente:
tail -f logs/trading_bot_*.log
```

### 5.2 Revisar Resultados

```bash
# Ver trades ejecutados
cat results/trades_*.csv

# Ver con less para navegación
less results/trades_$(date +%Y%m%d).csv
```

### 5.3 Acceso Remoto a Archivos

Desde tu PC local, puedes descargar archivos:

```bash
# Descargar logs
scp botuser@tu_vps_ip:/home/botuser/crypto-trading-bot/logs/*.log ./local_logs/

# Descargar resultados CSV
scp botuser@tu_vps_ip:/home/botuser/crypto-trading-bot/results/*.csv ./local_results/
```

### 5.4 Configurar Cron para Backups

```bash
# Editar crontab
crontab -e

# Añadir línea para backup diario de resultados (a las 00:00)
0 0 * * * cp -r /home/botuser/crypto-trading-bot/results /home/botuser/backups/results_$(date +\%Y\%m\%d)

# Limpiar backups antiguos (más de 30 días)
0 1 * * * find /home/botuser/backups -type d -mtime +30 -exec rm -rf {} \;
```

---

## 🔒 Paso 6: Seguridad

### 6.1 Configurar Firewall

```bash
# Instalar UFW
sudo apt install -y ufw

# Permitir SSH
sudo ufw allow  22/tcp

# Habilitar firewall
sudo ufw enable

# Ver status
sudo ufw status
```

### 6.2 Configurar Fail2Ban (Protección SSH)

```bash
# Instalar fail2ban
sudo apt install -y fail2ban

# Iniciar servicio
sudo systemctl start fail2ban
sudo systemctl enable fail2ban
```

### 6.3 Actualizar Regularmente

```bash
# Script de actualización semanal
sudo apt update && sudo apt upgrade -y
```

### 6.4 Backup de .env

```bash
# NO subas .env a git, haz backup manual
cp .env .env.backup

# Guárdalo en un lugar seguro (tu PC local)
scp botuser@vps_ip:/home/botuser/crypto-trading-bot/.env ./local_backup/.env
```

---

## 🔧 Paso 7: Actualización del Bot

Cuando quieras actualizar el código del bot:

```bash
# Conectar al VPS
ssh botuser@tu_vps_ip

# Ir al directorio del bot
cd ~/crypto-trading-bot

# Detener el bot
sudo systemctl stop trading-bot
# O con PM2: pm2 stop trading-bot

# Hacer backup de .env
cp .env .env.backup

# Actualizar código (si usas git)
git pull origin main

# O subir nuevos archivos con SCP desde tu PC local

# Activar entorno virtual
source venv/bin/activate

# Actualizar dependencias
pip install -r requirements.txt --upgrade

# Restaurar .env si fue sobrescrito
cp .env.backup .env

# Reiniciar bot
sudo systemctl start trading-bot
# O con PM2: pm2 restart trading-bot

# Verificar que funciona
sudo systemctl status trading-bot
# O: pm2 logs trading-bot
```

---

## 📱 Paso 8: Alertas y Notificaciones (Opcional)

### 8.1 Configurar Email de Alertas

Puedes configurar el servidor para enviar emails cuando el bot se detiene:

```bash
# Instalar mailutils
sudo apt install -y mailutils

# Editar el servicio systemd
sudo nano /etc/systemd/system/trading-bot.service

# Añadir en la sección [Service]:
# OnFailure=email-notification@%n.service
```

### 8.2 Telegram Bot (Futuro)

En futuras versiones, el bot incluirá notificaciones de Telegram automáticas.

---

## 💡 Consejos de Optimización

### Reducir Uso de RAM

```bash
# Añadir swap si tienes solo 1GB RAM
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Hacer permanente
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### Logs Rotation

```bash
# Crear configuración de logrotate
sudo nano /etc/logrotate.d/trading-bot
```

Contenido:

```
/home/botuser/crypto-trading-bot/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
```

---

## 🐛 Solución de Problemas VPS

### Bot No Inicia

```bash
# Ver logs de error
sudo journalctl -u trading-bot -n 50 --no-pager

# Verificar permisos
ls -la /home/botuser/crypto-trading-bot/

# Verificar que el entorno virtual funciona
source venv/bin/activate
python scripts/run_bot.py
```

### Sin Conexión a Internet

```bash
# Verificar conectividad
ping -c 4 google.com

# Verificar DNS
nslookup binance.com
```

### Bot Se Detiene Aleatoriamente

```bash
# Revisar uso de recursos
htop
# O
free -h
df -h

# Ver errores del sistema
dmesg | tail

# Aumentar swap si es necesario (ver arriba)
```

### No Puedo Conectar por SSH

```bash
# Desde el panel web de tu VPS provider:
# 1. Abrir consola web
# 2. Verificar servicio SSH
sudo systemctl status sshd

# 3. Reiniciar SSH
sudo systemctl restart sshd

# 4. Verificar firewall
sudo ufw status
```

---

## 📊 Monitoreo Avanzado (Opcional)

### Configurar Grafana + Prometheus

Para monitoreo profesional del bot, puedes configurar:
1. Prometheus para recolectar métricas
2. Grafana para visualización
3. AlertManager para alertas

(Guía avanzada disponible en futuras versiones)

---

## 🎯 Checklist Final

Antes de dejar el bot corriendo en producción:

- [ ] Bot funciona correctamente en testnet
- [ ] Configuración `.env` verificada
- [ ] Servicio systemd/PM2 configurado
- [ ] Logs guardan correctamente
- [ ] Firewall configurado
- [ ] Backup de `.env` guardado
- [ ] Monitoreo de logs configurado
- [ ] Probado por al menos 48 horas
- [ ] API keys con permisos mínimos necesarios
- [ ] Entiendes completamente cómo funciona

---

¡Felicidades! Tu bot ahora está corriendo 24/7 en un VPS. 🎉

**Próximos pasos**:
1. Monitorea logs diariamente la primera semana
2. Revisa resultados semanalmente
3. Ajusta parámetros según rendimiento
4. Mantén el sistema actualizado

**Recuerda**: SIEMPRE comienza con testnet y cantidades pequeñas en producción.
