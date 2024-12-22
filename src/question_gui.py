import json
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

class QuestionManagerGUI:
    def __init__(self, questions_file):
        with open(questions_file, 'r') as f:
            self.questions_data = json.load(f)
        self.user_responses = {}
        self.selected_stages = []
        self.current_section_index = 0
        self.current_question_index = 0

        self.root = tk.Tk()
        self.root.title("DevSecOps Tool Selector")
        self.root.geometry("950x750")  # Increased window size

        self.frame = tk.Frame(self.root, padx=30, pady=30)  # Added padding to frame
        self.frame.pack(padx=20, pady=20)

        self.question_label = tk.Label(self.frame, text="", wraplength=700, justify=tk.LEFT)
        self.question_label.pack()

        self.response_entry = tk.Entry(self.frame)
        self.response_entry.pack()

        self.response_listbox = tk.Listbox(self.frame, selectmode=tk.SINGLE)
        self.response_listbox.pack()

        self.next_button = tk.Button(self.frame, text="Next", command=self.next_question)
        self.next_button.pack()

        self.prev_button = tk.Button(self.frame, text="Previous", command=self.previous_question)
        self.prev_button.pack()

        self.load_section()

    def get_section(self, section_name):
        for section in self.questions_data['sections']:
            if section['name'] == section_name:
                return section
        return None

    def get_question(self, question_id):
        for section in self.questions_data['sections']:
            for question in section['questions']:
                if question['question_id'] == question_id:
                    return question
        return None

    def load_section(self):
        self.current_question_index = 0
        self.load_question()

    def load_question(self):
        self.clear_response_widgets()
        question = self.get_current_question()

        if not question or not self.should_ask_question(question):
            self.next_section()
            return

        self.question_label.config(text=question['text'])

        if question['type'] == 'text':
            self.response_entry.pack()
        elif question['type'] == 'boolean':
            self.response_listbox.pack()
            self.response_listbox.insert(tk.END, "Yes")
            self.response_listbox.insert(tk.END, "No")
        elif question['type'] == 'multiple_choice':
            self.response_listbox.pack()
            if question.get('allows_multiple', False):
                self.response_listbox.config(selectmode=tk.MULTIPLE)
            else:
                self.response_listbox.config(selectmode=tk.SINGLE)
            for option in question['options']:
                self.response_listbox.insert(tk.END, option['label'])

    def clear_response_widgets(self):
        self.response_entry.pack_forget()
        self.response_listbox.pack_forget()
        self.response_entry.delete(0, tk.END)
        self.response_listbox.delete(0, tk.END)

    def next_question(self):
        question = self.get_current_question()
        self.save_response()

        if question['question_id'] == "stages_implemented":
            self.selected_stages = self.user_responses["stages_implemented"]

        self.current_question_index += 1
        if self.current_question_index >= len(self.questions_data['sections'][self.current_section_index]['questions']):
            self.next_section()
        else:
            self.load_question()

    def previous_question(self):
        self.current_question_index -= 1
        if self.current_question_index < 0:
            self.previous_section()
        else:
            self.load_question()

    def next_section(self):
        while True:
            self.current_section_index += 1
            if self.current_section_index >= len(self.questions_data['sections']):
                self.show_summary()
                return

            next_section_name = self.questions_data['sections'][self.current_section_index]['name']

            if next_section_name == "Introduction" or next_section_name == "Stage Selection":
                self.load_section()
                return

            if 'stage_id' in self.questions_data['sections'][self.current_section_index]:
                stage_id = self.questions_data['sections'][self.current_section_index]['stage_id']
                if stage_id in self.selected_stages:
                    self.load_section()
                    return
            else:
                self.load_section()
                return

    def previous_section(self):
        self.current_question_index = -1  # Reset question index for previous section
        self.current_section_index -= 1
        if self.current_section_index < 0:
            self.current_section_index = 0
        else:
            section_name = self.questions_data['sections'][self.current_section_index]['name']
            if section_name == "Stage Selection":
                self.selected_stages = []
            self.load_section()

    def get_current_question(self):
        if 0 <= self.current_section_index < len(self.questions_data['sections']):
            section = self.questions_data['sections'][self.current_section_index]
            if 0 <= self.current_question_index < len(section['questions']):
                return section['questions'][self.current_question_index]
        return None

    def save_response(self):
        question = self.get_current_question()
        if not question:
            return

        question_id = question['question_id']
        if question['type'] == 'text':
            response = self.response_entry.get()
        elif question['type'] == 'boolean':
            selection = self.response_listbox.curselection()
            if selection:
                response = self.response_listbox.get(selection[0]).lower() == 'yes'
            else:
                response = None
        elif question['type'] == 'multiple_choice':
            selections = self.response_listbox.curselection()
            if selections:
                if question.get('allows_multiple', False):
                    response = [question['options'][i]['value'] for i in selections]
                else:
                    response = question['options'][selections[0]]['value']
            else:
                response = None
        else:
            response = None

        self.user_responses[question_id] = response

    def should_ask_question(self, question):
        depends_on = question.get('depends_on')
        if not depends_on:
            return True

        if depends_on['question_id'] == "stages_implemented":
            return depends_on['value'] in self.user_responses.get("stages_implemented", [])

        if depends_on['question_id'] not in self.user_responses:
            return False  # Dependency question hasn't been answered yet

        dependency_value = self.user_responses[depends_on['question_id']]

        if isinstance(dependency_value, list):
            return depends_on['value'] in dependency_value
        else:
            return dependency_value == depends_on['value']

    def show_summary(self):
        self.frame.destroy()

        # Create a canvas and a scrollbar
        canvas = tk.Canvas(self.root)
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        # Configure the canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind the scrollable frame to the canvas
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        tk.Label(scrollable_frame, text="Summary of Your Responses", font=("Arial", 14)).pack()

        for question_id, response in self.user_responses.items():
            question = self.get_question(question_id)
            if question:
                tk.Label(scrollable_frame, text=question['text'], font=("Arial", 12), wraplength=700, justify=tk.LEFT).pack(anchor="w")
                if question['type'] == 'multiple_choice':
                    if not response:
                        tk.Label(scrollable_frame, text="None", font=("Arial", 10), fg="gray").pack(anchor="w")
                    else:
                        for option in question['options']:
                            if option['value'] in response:
                                tk.Label(scrollable_frame, text=f"- {option['label']}", font=("Arial", 10)).pack(anchor="w")
                elif question['type'] == 'boolean':
                    tk.Label(scrollable_frame, text=f"Answer: {'Yes' if response else 'No'}", font=("Arial", 10)).pack(anchor="w")
                else:
                    tk.Label(scrollable_frame, text=f"Answer: {response}", font=("Arial", 10)).pack(anchor="w")

        save_button = tk.Button(scrollable_frame, text="Save Responses", command=self.save_responses)
        save_button.pack(pady=10)

    def save_responses(self, filename="data/user_responses.json"):
        with open(filename, 'w') as f:
            json.dump(self.user_responses, f, indent=4)
        messagebox.showinfo("Saved", f"Responses saved to {filename}")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    question_manager = QuestionManagerGUI("data/questions.json")
    question_manager.run()