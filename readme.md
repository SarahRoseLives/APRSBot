# APRS Example Bot

This repository contains an example APRS (Automatic Packet Reporting System) bot that demonstrates how to create and customize your own APRS bot. The bot connects to the APRS-IS network, handles incoming messages, and responds to commands with predefined messages. 

## Features

- Connects to the APRS-IS network.
- Listens for incoming messages addressed to the bot.
- Sends acknowledgment (ACK) messages for received packets.
- Responds to specific commands with predefined responses.
- Easy to extend with additional commands and responses.

## Prerequisites

Before running the bot, ensure you have the following:

- Python 3.x installed.
- `aprslib` library. You can install it using pip:

  ```bash
  pip install aprslib
  ```

## Configuration

1. **Edit the Bot Configuration:**

   Open `main.py` and update the following fields with your APRS credentials:

   ```python
   CALLSIGN = "NOCALL"  # Replace with your APRS callsign
   PASSCODE = "12345"   # Replace with your APRS passcode
   ```

2. **Customize Commands:**

   You can add or modify commands and response by updating files in the 'commands' folder.



## Running the Bot

1. Clone the repository or download the `main.py` file.

   ```bash
   git clone https://github.com/SarahRoseLives/APRSBot.git
   cd APRSBot
   ```

2. Run the bot using Python:

   ```bash
   python main.py
   ```

   The bot will connect to the APRS-IS server, listen for incoming messages, and handle commands as defined.

## Usage

- **Command Handling:** The bot will respond to commands sent to it with the predefined responses in the `commands` dictionary.
- **Acknowledgments:** The bot will send an acknowledgment message for every received packet.

