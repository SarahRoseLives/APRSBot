import aprslib
import threading
import queue
import time
import importlib
import os

# APRS login details
CALLSIGN = "NOCALL"
PASSCODE = "123456"  # Your passcode here

# APRS server settings
SERVER = "rotate.aprs2.net"
PORT = 14580

# Path to the commands folder
COMMANDS_FOLDER = "modules"

# List of received message IDs to avoid duplicate ACKs
received_msgs = set()

# Dictionary to hold command functions
command_functions = {}

def load_commands():
    """Dynamically load command modules from the commands folder."""
    for filename in os.listdir(COMMANDS_FOLDER):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = filename[:-3]
            module = importlib.import_module(f"{COMMANDS_FOLDER}.{module_name}")
            if hasattr(module, 'handle_command'):
                command_functions[module_name] = module.handle_command
            else:
                print(f"Module {module_name} does not have a 'handle_command' function.")

def send_ack(client, msgNo, to_call):
    """Function to send ACK in a separate thread."""
    to_call_padded = f"{to_call:<9}"
    if any(char.isalpha() for char in msgNo):
        msgNo += "}"
    ack_message = f"{CALLSIGN}>APRS::{to_call_padded}:ack{msgNo}"
    try:
        print(f"Sending ACK: {ack_message}")
        client.sendall(ack_message)
        print(f"ACK sent for message {msgNo} to {to_call}")
        time.sleep(5)
    except Exception as e:
        print(f"Error sending ACK: {e}")


def send_response(client, to_call, response_message):
    """Function to send a response message in a separate thread, splitting at spaces."""
    to_call_padded = f"{to_call:<9}"

    def split_message(message, max_length):
        """Helper function to split message at spaces."""
        words = message.split()
        messages = []
        current_message = ""
        for word in words:
            if len(current_message) + len(word) + 1 > max_length:
                messages.append(current_message)
                current_message = word
            else:
                if current_message:
                    current_message += " "
                current_message += word
        if current_message:
            messages.append(current_message)
        return messages

    # Split the response message at spaces to avoid cutting off words
    messages = split_message(response_message, 48)

    for msg in messages:
        response = f"{CALLSIGN}>APRS::{to_call_padded}:{msg}"
        try:
            print(f"Sending response: {response}")
            client.sendall(response)
            print(f"Response sent to {to_call}")
        except Exception as e:
            print(f"Error sending response: {e}")
        time.sleep(5)


def handle_packet(packet):
    """Callback function to process incoming packets."""
    print(f"Received packet: {packet}")
    if "message_text" in packet and packet.get("addresse") == CALLSIGN:
        from_call = packet.get("from")
        msgNo = packet.get("msgNo")
        message_text = packet.get("message_text")

        if msgNo and msgNo not in received_msgs:
            print(f"Received message: {message_text} from {from_call}")
            received_msgs.add(msgNo)
            print(f"Starting thread to send ACK for msgNo: {msgNo} from: {from_call}")
            threading.Thread(target=send_ack, args=(client, msgNo, from_call)).start()

        message_text_lower = message_text.lower()
        command_function = command_functions.get(message_text_lower)
        if command_function:
            response_message = command_function()
            if response_message:
                time.sleep(5)
                print(f"Received command '{message_text}' from {from_call}, sending response...")
                threading.Thread(target=send_response, args=(client, from_call, response_message)).start()

def connect_to_aprs():
    """Function to connect to the APRS network."""
    global client
    client = aprslib.IS(CALLSIGN, PASSCODE, port=PORT)
    print(f"Connecting to APRS-IS server {SERVER}:{PORT} as {CALLSIGN}")
    client.set_filter(f"b/{CALLSIGN}")
    print(f"Filter set to listen only for messages addressed to {CALLSIGN}")

    try:
        client.connect(SERVER, PORT)
        print("Connected to APRS-IS server successfully")
        client.consumer(handle_packet, raw=False)
    except Exception as e:
        print(f"Error connecting to APRS-IS server: {e}")

if __name__ == "__main__":
    load_commands()
    connect_to_aprs()
