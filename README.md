# IoT Platform

- An IoT platform powered by [`mosquitto`](https://github.com/eclipse/mosquitto) and Flask

## Features

- [x] Log

## TODO

- [ ] Clients Specifications (Interface Documents)
- [ ] Camera Integration
- [ ] Wi-Fi Devices
- [ ] Breath Detection via Wi-Fi
- [ ] Robot Integration

## Usage

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

## Clients Specifications

- In order to interact with our sever, clients must
  - have the following `mqtt` interfaces [published](#publish) or [subscripted](#subscriptions).
  - have the following [`Params`](#params) maintained.

### `Params`

```toml
deviceType = "" # Type
deviceId = ""   # Id
```

### Subscriptions

#### `/client/{deviceType}/{deviceId}/online`

- Called when client is connected to `mqtt` server.
- This allow the server to register the corresponding client.

#### `/client/{deviceType}/{deviceId}/offline`

- Called when client is offline.
- This allow the server to delete corresponding client.

#### `/client/{deviceType}/{deviceId}/start`

- Called when client is starting to work.
- This allow the server to change status of the client.

#### ...

### Publish

#### `/client/{deviceType}/{deviceId}/[wav|pgm|pgn]`

- Called when binary data is transferred
