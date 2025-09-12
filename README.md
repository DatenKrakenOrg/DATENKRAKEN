# DATENKRAKEN

The DATENKRAKEN project focuses on gathering data on **temperature, humidity, VOC Index, and noise** in a room.
These data are collected via an **Arduino** with corresponding sensors and displayed on a **website** for the user.

For more information you can look into our [documentation](https://datenkrakenorg.github.io/DATENKRAKEN/).

## Setup

### Pre-Commits

Pre-commits are executed on every commit to prevent the push of secrets.

#### Install Pre-Commits

```bash
pipx install pre-commit
```

**Navigate into the project folder:**

```bash
pre-commit install
pre-commit run
```

### uv

`uv` is a **Python package and project manager**.

* To sync packages, run:

```bash
uv sync
```

* To run the website locally:

Go into the frontend folder and run
```bash
uv run streamlit run src/app.py
```

You will also need an **OpenWeather API key** in the `.env` file in frontend/:

```
WEATHER_API_KEY=xxxx
```

Also you need to fill in the .env variables in the following directories:
- frontend/
- subscription_script/
- database/

An example for each .env is provided in the associated directory.


#### Installing uv

<a href="https://docs.astral.sh/uv/getting-started/installation/">See the official guide here</a>

### pio

Instead of the Arduino IDE, we use **PlatformIO (pio)** because it allows **better dependency declaration and rebuilds**.
The `platformio.ini` file defines the **library dependencies** and the **Arduino board** being used.

#### Install pio

<a href="https://docs.platformio.org/en/latest/integration/ide/pioide.html">See the official guide here</a>

#### Use pio

To use pio you just have to go into the arduino folder and then execute `pio run` to install all dependencies and compile the code.

## Setup with Docker

### Environment Variables

To run the project with Docker Compose, you need to provide a `.env` file in the project root. This file contains all necessary environment variables for the frontend, database, and subscription script services.

An example `.env` file is provided as `example.env` in the repository root. Copy it and fill in your secrets and configuration:

```bash
cp example.env .env
# Edit .env and set your values
```

**Important:**
- For local Docker Compose deployments, set `DB_HOST=timescaledb:5432` for all services that connect to the database.
- Make sure to set a valid `WEATHER_API_KEY` and your MQTT broker credentials.

### Start All Services

To build and start all services (frontend, database, subscription script) run:

```bash
docker compose up --build
```

This will start all containers and automatically use the variables from your `.env` file.

You can access the frontend at [http://localhost:6501](http://localhost:6501) by default.

### Stopping and Cleaning Up

To stop all services:

```bash
docker compose down
```

To remove all containers, networks, and volumes (including database data):

```bash
docker compose down -v --remove-orphans
```

---

