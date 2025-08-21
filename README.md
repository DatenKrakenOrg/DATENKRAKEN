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

```bash
uv run streamlit run app.py
```

You will also need an **OpenWeather API key** in the `.env` file.

#### Installing uv

<a href="https://docs.astral.sh/uv/getting-started/installation/">See the official guide here</a>

### pio

Instead of the Arduino IDE, we use **PlatformIO (pio)** because it allows **better dependency declaration and rebuilds**.
The `platformio.ini` file defines the **library dependencies** and the **Arduino board** being used.

#### Install pio

<a href="https://docs.platformio.org/en/latest/integration/ide/pioide.html">See the official guide here</a>
