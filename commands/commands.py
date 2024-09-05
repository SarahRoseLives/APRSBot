import os


def handle_command():
    """Return a list of available commands based on files in the commands folder."""
    # Path to the commands folder
    commands_folder = "commands"

    # List to hold command names
    command_list = []

    # Check if the commands folder exists
    if os.path.isdir(commands_folder):
        # Iterate through files in the commands folder
        for filename in os.listdir(commands_folder):
            if filename.endswith(".py") and filename != "__init__.py":
                # Remove the .py extension to get the command name
                command_name = filename[:-3]
                command_list.append(command_name)
    else:
        command_list.append("No commands folder found.")

    # Format the command list for output
    if command_list:
        return "Available commands:\n" + "\n".join(command_list)
    else:
        return "No commands available."
