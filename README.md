# IoT Platform

- An IoT platform powered by [`mosquitto`](https://github.com/eclipse/mosquitto) and Flask

## Features

- [x] Log
- [ ] Camera Integration
- [ ] Wi-Fi devices
- [ ] Breath Detection via Wi-Fi

## Run

### 1. Python Env Setup

#### Conda

<!-- TODO: Add Real Conda env backup Setup -->

```shell
conda create -n iot-platform python=3.11.3
conda install pip
pip install -r requirements.txt
```

#### via PyCharm

- Select `pyenv`

### 2. `mosquitto` Installation

- Install `mosquitto` binary by following instructions [here](https://mosquitto.org/download/).
- Add the following to `mosquitto` configurations. You may load it at hot via `-c` options.

```conf
listener 1883 0.0.0.0
allow_anonymous true
```

### 3. `mosquitto` _MUST_ be up before Server

#### Linux

```shell
./mosquitto/mosquitto_linux -c ./mosquitto/mosquitto.conf
```

### 4. Start Server

```shell
python wsgi.py
```
