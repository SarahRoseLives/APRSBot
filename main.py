import aprslib
import threading
import queue
import time

# APRS login details
CALLSIGN = "NOCALL"
PASSCODE = "123456"  # Your passcode here

# APRS server settings
SERVER = "rotate.aprs2.net"
PORT = 14580

# List of received message IDs to avoid duplicate ACKs
received_msgs = set()


def send_ack(client, msgNo, to_call):
    """Function to send ACK in a separate thread."""
    # Ensure the 'to_call' is 9 characters long, padded with spaces
    to_call_padded = f"{to_call:<9}"

    # If the msgNo contains alphabetic characters, append '}' to the end
    if any(char.isalpha() for char in msgNo):
        msgNo += "}"

    # Correctly format the ACK message
    ack_message = f"{CALLSIGN}>APRS::{to_call_padded}:ack{msgNo}"
    try:
        time.sleep(5)
        print(f"Sending ACK: {ack_message}")
        client.sendall(ack_message)  # Send as a string
        print(f"ACK sent for message {msgNo} to {to_call}")
    except Exception as e:
        print(f"Error sending ACK: {e}")


def send_response(client, to_call, response_message):
    """Function to send a response message in a separate thread."""
    # Ensure the 'to_call' is 9 characters long, padded with spaces
    to_call_padded = f"{to_call:<9}"

    # Function to split the message at the nearest space before the limit
    def split_message(message, limit=48):
        words = message.split()
        parts = []
        current_part = ""

        for word in words:
            # Check if adding the next word would exceed the limit
            if len(current_part) + len(word) + 1 > limit:
                parts.append(current_part)
                current_part = word
            else:
                if current_part:
                    current_part += " "
                current_part += word

        # Add the last part if there's any content left
        if current_part:
            parts.append(current_part)

        return parts

    messages = split_message(response_message)

    for msg in messages:
        # Format the response message
        response = f"{CALLSIGN}>APRS::{to_call_padded}:{msg}"
        try:
            print(f"Sending response: {response}")
            client.sendall(response)  # Send as a string
            print(f"Response sent to {to_call}")
        except Exception as e:
            print(f"Error sending response: {e}")
        time.sleep(5)  # Delay between sending multiple messages



def handle_packet(packet):
    """Callback function to process incoming packets."""
    print(f"Received packet: {packet}")  # Debugging output for each packet received

    # Ensure the key is correctly spelled and exists
    if "message_text" in packet and packet.get("addresse") == CALLSIGN:
        from_call = packet.get("from")
        msgNo = packet.get("msgNo")
        message_text = packet.get("message_text")

        # Check if we've already responded to this message
        if msgNo and msgNo not in received_msgs:
            print(f"Received message: {message_text} from {from_call}")

            # Add to set to avoid duplicate ACKs
            received_msgs.add(msgNo)

            # Respond with ACK in a separate thread
            print(f"Starting thread to send ACK for msgNo: {msgNo} from: {from_call}")
            threading.Thread(target=send_ack, args=(client, msgNo, from_call)).start()

        # Handle command responses using if statements
        message_text_lower = message_text.lower()
        if message_text_lower == "?":
            response_message = "Source: https://github.com/SarahRoseLives/APRSBot"
        elif message_text_lower == "status":
            response_message = "Bot is operational. Type 'help' for more."
        # Add more commands and responses here
        else:
            response_message = None

        if response_message:
            time.sleep(5)
            print(f"Received command '{message_text}' from {from_call}, sending response...")
            threading.Thread(target=send_response, args=(client, from_call, response_message)).start()


def connect_to_aprs():
    """Function to connect to the APRS network."""
    global client
    client = aprslib.IS(CALLSIGN, PASSCODE, port=PORT)

    # Debugging output for connection info
    print(f"Connecting to APRS-IS server {SERVER}:{PORT} as {CALLSIGN}")

    # Use the 'b' filter to receive only messages addressed to bot callsign
    client.set_filter(f"b/{CALLSIGN}")
    print(f"Filter set to listen only for messages addressed to {CALLSIGN}")

    try:
        client.connect(SERVER, PORT)
        print("Connected to APRS-IS server successfully")
        client.consumer(handle_packet, raw=False)
    except Exception as e:
        print(f"Error connecting to APRS-IS server: {e}")


if __name__ == "__main__":
    connect_to_aprs()
