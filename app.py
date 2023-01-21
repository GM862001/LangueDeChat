from PIL import ImageTk, Image
from itertools import chain
import tkinter as tk
import tkmacosx
import logging

from lib import DialogueManager
from lib import USR_REQ_KEYS, USR_INF_KEYS, OWT, INF, REQ, THX, RJCT

logging.basicConfig(
    filename="log/app.log",
    filemode="w",
    level=logging.INFO,
    format="%(message)s"
)


class ChatApplication:


    def __init__(self, rule_based=True):

        self.window = tk.Tk()
        self.dialogue_manager = DialogueManager(
            kb_filepath="data/knowledge_base.json",
        )
        self.rule_based = rule_based
        if not rule_based:
            self.dialogue_manager.load("models/Trained")
        self._setup_window()
        self._round = 0


    def run(self):

        self.window.mainloop()


    def _add_image(self, x, y, size, filepath):

        image = Image.open(filepath)
        image = image.resize(size, Image.Resampling.LANCZOS)
        image = ImageTk.PhotoImage(image)
        label = tk.Label(image=image, borderwidth=0)
        label.image = image
        label.place(x=x, y=y)


    def _add_header(self):

        tk.Label(
            self.window,
            bg="white",
            fg="black",
            text="Langue de Chat",
            font="Helvetica 50"
        ).place(relwidth=1, y=10)
        tk.Label(
            self.window,
            bg="white",
            fg="#83A1AB",
            text="«Ne donne pas ta langue au chat»",
            font="Helvetica 20 italic"
        ).place(relwidth=1, y=80)
        tk.Label(
            self.window,
            bg="white",
            fg="Black",
            text="«Don't give up on finding the solution»",
            font="Helvetica 20 italic"
        ).place(relwidth=1, y=110)
        self._add_image(x=20, y=25, size=(140, 100), filepath="img/chatting_cat.png")
        self._add_image(x=540, y=75, size=(150, 50), filepath="img/trois_chats.png")


    def _add_text(self):

        self.text = tk.Text(
            self.window,
            padx=5,
            pady=5,
            font="Helvetica 18",
            wrap=tk.WORD
        )
        self.text.place(relheight=0.6, relwidth=1, y=150)
        self.text.configure(cursor="arrow", state=tk.DISABLED)


    def _add_entry(self, label, xlabel, xentry, y):

        tk.Label(
            self.window,
            text=label,
            font="Helvetica 20",
            background="white"
        ).place(x=xlabel, y=y)
        entry = tk.Entry(
            self.window,
            background="white",
            font="Helvetica 15"
        )
        entry.place(relwidth=0.5, x=xentry, y=y)
        entry.focus()
        return entry


    def _add_button(self, text, command, x, y, height=30):

        tkmacosx.Button(
            self.window,
            text=text,
            font="Helvetica 20 bold",
            bg="#83A1AB",
            fg="black",
            borderless=1,
            command=command,
            activebackground="#83A1AB"
        ).place(x=x, y=y, height=height)


    def _setup_window(self):
        
        self.window.title("Langue De Chat")
        self.window.geometry("700x750")
        self.window.resizable(width=False, height=False)
        self.window.configure(bg="white")
        self._add_header()
        self._add_text()
        self.inform_entry = self._add_entry(label="Inform", xlabel=60, xentry=165, y=615)
        self.request_entry = self._add_entry(label="Request", xlabel=50, xentry=165, y=655)
        self._add_button(text="THANKS", command=lambda: self._send("Thanks", THX), x=190, y=700)
        self._add_button(text="REJECT", command=lambda: self._send("Reject", RJCT), x=375, y=700)
        self._add_button(text="EXIT", command=self.window.destroy, x=545, y=700)
        self._add_button(text="HELP", command=self._on_help_pressed, x=35, y=700)
        self._add_button(text="SEND", command=self._on_send_pressed, x=545, y=615, height=70)
        self.window.bind('<Return>', self._on_send_pressed)


    def _parse_inform(self, inform_str):

        informs = {}
        if inform_str:
            inform_pairs = inform_str.split(";")
            for inform in inform_pairs:
                inform = inform.strip()
                key, value = inform.split(":")
                key = key.lower().strip()
                value = value.lower().strip()
                if key not in USR_INF_KEYS:
                    raise ValueError
                owt_values = ["anything", "any", "owt"]
                if key == "open_access" and value not in ["yes", "no"] + owt_values:
                    raise ValueError
                if key == "content_type" and value not in ["books", "journals", "conferences"] + owt_values:
                    raise ValueError
                if value in owt_values:
                    value = OWT
                informs[key] = value
        return informs


    def _parse_request(self, request_str):

        requests = []
        if request_str:
            for request in request_str.split(";"):
                request = request.strip()
                if request not in USR_REQ_KEYS:
                    raise ValueError
                requests.append(request)
        return requests


    def _on_send_pressed(self, event=None):

        inform_string = self.inform_entry.get()
        request_string = self.request_entry.get()
        if inform_string or request_string:
            self.inform_entry.delete(0, tk.END)
            self.request_entry.delete(0, tk.END)
            try:
                user_action = {
                    INF: self._parse_inform(inform_string),
                    REQ: self._parse_request(request_string)
                }
            except:
                self._submission_error()
            else:
                msg = inform_string
                if request_string:
                    if inform_string:
                        msg += "\n"
                    msg += request_string + "?"
                self._send(msg, user_action)


    def _send(self, user_message, user_action):

        agent_message = self.get_response(user_action)
        self._insert(user_message, agent_message)


    def _submission_error(self):
        
        error_window = tk.Toplevel(self.window)
        error_window.title("Error")
        error_window.geometry("400x110")
        error_window.resizable(width=False, height=False)
        error_window.configure(bg="white")
        error_text = tk.Text(error_window, padx=5, pady=20, width=500, height=600, bg="white", fg="black", font="Helvetica 14", wrap=tk.WORD, highlightthickness=0)
        error_text.pack()
        error_text.insert(
            tk.END,
            "Invalid input!\n\n"
            "Please enter valid inform and request values. Look at the help menu for further information."
        )
        error_text.tag_config("heading", font=("Helvetica", 20, "bold"), justify="center")
        error_text.tag_config("body", font=("Helvetica", 14, "italic"), justify="center")
        error_text.tag_add("heading", "1.0", "1.end")
        error_text.tag_add("body", "3.0", "3.end")


    def _on_help_pressed(self):

        help_window = tk.Toplevel(self.window)
        help_window.title("Help")
        help_window.geometry("500x600")
        help_window.resizable(width=False, height=False)
        help_window.configure(bg="white")
        help_text = tk.Text(help_window, padx=5, pady=5, width=500, height=600, bg="white", fg="black", font="Helvetica 14", wrap=tk.WORD, highlightthickness=0)
        help_text.pack()
        help_text.tag_config("title", font=("Helvetica", 20, "bold"), justify="center")
        help_text.tag_config("subtitle", font=("Helvetica", 16, "bold"))
        help_text.tag_config("key", font=("Helvetica", 14, "italic"))

        help_text.insert(
            tk.END,
            "WELCOME TO LANGUE DE CHAT\n\n" \
            "Langue de Chat is a chatbot that helps you browse your favourite scientific documents.\n" \
            "You can interact with the agent by typing in the \"Inform\" and \"Request\" entries, or by pressing the \"Thanks\" and \"Reject\" buttons.\n" \
            "Read the help information below to learn the details!\n\n"
            "INFORM ENTRY\n\n" \
            "Type here your constraints and preferences to inform the agent about them.\n"
            "For each attribute that you want to inform about, " \
            "type the attribute name followed by a colon and its value. " \
            "For example, to inform the agent that you are interested in artificial intelligence documents, " \
            "type \"keywords: Artificial intelligence\".\n" \
            "To inform the agent about multiple attributes, " \
            "separate each attribute with a semicolon. " \
            "For example, to inform the agent that you are interested in journals only, " \
            "type \"keywords: Artificial intelligence; content_type: journals\".\n" \
            "If the value of an attribute is irrelevant to you, " \
            "type \"anything\", \"any\" or \"owt\".\n\n" \
            "You can inform the agent about the following attributes:\n" \
            "keywords: keywords to search for;\n" \
            "content_type: type of publication (journals, books, or conferences);\n" \
            "authors: authors of the document;\n" \
            "document_title: title of the document;\n" \
            "publication_title: title of the publication;\n" \
            "open_access: whether you want an open access resource or not (Yes or No);\n" \
            "publisher: the publisher of the document;\n" \
            "min_num_citations: minimum number of citations;\n" \
            "publication_year: year of publication;\n" \
            "min_publication_year: minimum year of publication;\n" \
            "max_publication_year: maximum year of publication.\n\n"
            "REQUEST ENTRY\n\n" \
            "Type here the attributes that you want to be suggested or informed about to make the agent specify them.\n" \
            "To request an attribute to the agent, type the attribute name. " \
            "For example, to request authors, type: \"authors\".\n" \
            "To request multiple attributes, separate each attribute with a semicolon. " \
            "For example, to request authors and document title, type: \"authors; document_title\".\n\n" \
            "You can request the following attributes:\n" \
            "authors: authors of the document;\n" \
            "document_title: title of the document;\n" \
            "publication_title: title of the publication;\n" \
            "open_access: whether the resource is open access or not;\n" \
            "publisher: the publisher of the document;\n" \
            "num_citations: number of citations;\n" \
            "publication_year: year of publication;\n" \
            "content_type: type of publication;\n" \
            "doi: document identifier;\n" \
            "abstract: abstract of the document.\n\n"
            "THANKS AND REJECT BUTTONS\n\n" \
            "Press the \"Thanks\" button if you want to let the agent know that you are satisfied with the suggested proposal.\n" \
            "Instead, press the \"Reject\" button if you want the agent to propose something different.\n"
        )

        help_text.tag_add("title", "1.0", "1.end")
        help_text.tag_add("subtitle", "7.0", "7.end")
        help_text.tag_add("subtitle", "27.0", "27.end")
        help_text.tag_add("subtitle", "45.0", "45.end")
        for line in chain(range(15, 26), range(34, 44)):
            key = help_text.get(f"{line}.0", f"{line}.end").split(":")[0]
            help_text.tag_add("key", f"{line}.0", f"{line}.{len(key)}")


    def _insert(self, user_msg, agent_msg):

        msg = f"YOU\n{user_msg}\n\nLANGUE DE CHAT\n{agent_msg}\n\n"
        self.text.configure(state=tk.NORMAL)
        self.text.insert(tk.END, msg)
        self.text.configure(state=tk.DISABLED)
        self.text.see(tk.END) # Scroll to the bottom


    def get_response(self, user_action):
        
        self._round += 1
        _, _, agent_action, _ = self.dialogue_manager.step(user_action, warmup=self.rule_based)
        logging.info(
            f"ROUND {self._round}\n"
            f"User action: {user_action}\n"
            f"Agent action: {agent_action}\n"
            f"State Tracker current user informs: "
            f"{self.dialogue_manager._state_tracker._curr_usr_inf}\n"
            f"State Tracker current user requests: "
            f"{self.dialogue_manager._state_tracker._curr_usr_req}\n"
            f"State Tracker current agent informs: "
            f"{self.dialogue_manager._state_tracker._curr_agt_inf}\n"
        )
        if agent_action[0] == INF:
            key, value = agent_action[1:]
            if key in ["abstract", "publication_title", "document_title"]:
                return f"{key}: \"{value}\""
            else:
                return f"{key}: {value}"
        elif agent_action[0] == REQ:
            return f"{agent_action[1]}?"
        else:
            return agent_action


if __name__ == "__main__":

    app = ChatApplication(rule_based=True)
    app.run()

