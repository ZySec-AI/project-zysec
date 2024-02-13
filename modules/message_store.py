# Define the MessageStore class
class MessageStore:
    def __init__(self):
        self.messages = {}

    def update_message(self, page, message_type, message):
        if page not in self.messages:
            self.messages[page] = {"system": None, "greeting": None, "history": []}
        if message_type in ["system", "greeting"]:
            self.messages[page][message_type] = message
        elif message_type == "history":
            self.messages[page]["history"].append(message)

    def get_message(self, page, message_type):
        return self.messages.get(page, {}).get(message_type, "")

    def get_history(self, page):
        return self.messages.get(page, {}).get("history", [])

    def set_history(self, page, history):
        if page not in self.messages:
            self.messages[page] = {"system": None, "greeting": None, "history": []}
        self.messages[page]["history"] = history