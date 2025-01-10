import json
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext


class QuestionManagerGUI:
    def __init__(self, questions_file):
        self.questions_data = self.load_questions(questions_file)
        self.user_responses = {}
        self.selected_stages = []
        self.current_section_index = 0
        self.current_question_index = 0

        self.setup_gui()

        self.load_section()

    def load_questions(self, questions_file):
        try:
            with open(questions_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            messagebox.showerror("Error", f"Questions file not found: {questions_file}")
            exit()
        except json.JSONDecodeError:
            messagebox.showerror("Error", f"Invalid JSON in questions file: {questions_file}")
            exit()

    def setup_gui(self):
        """Setup the main GUI components."""
        self.root = tk.Tk()
        self.root.title("DevSecOps Tool Selector")
        self.root.geometry("950x750")

        self.frame = tk.Frame(self.root, padx=30, pady=30)
        self.frame.pack(padx=20, pady=20)

        self.question_label = tk.Label(self.frame, text="", wraplength=700, justify=tk.LEFT, font=("Arial", 12))
        self.question_label.pack(pady=(0, 10))

        self.response_entry = tk.Entry(self.frame)
        self.response_listbox = tk.Listbox(self.frame, selectmode=tk.SINGLE)

        self.navigation_frame = tk.Frame(self.frame)
        self.navigation_frame.pack(pady=20)

        self.prev_button = tk.Button(self.navigation_frame, text="Previous", command=self.previous_question)
        self.prev_button.grid(row=0, column=0, padx=5)

        self.next_button = tk.Button(self.navigation_frame, text="Next", command=self.next_question)
        self.next_button.grid(row=0, column=1, padx=5)

    def load_section(self):
        """Load the first question of the current section."""
        self.current_question_index = 0
        self.load_question()

    def load_question(self):
        """Load the current question."""
        self.clear_response_widgets()
        question = self.get_current_question()

        if not question:
            self.next_section()
            return

        self.question_label.config(text=question['text'])

        if question['type'] == 'text':
            self.response_entry.pack()
        elif question['type'] == 'boolean':
            self.populate_listbox(["Yes", "No"])
        elif question['type'] == 'multiple_choice':
            options = [opt['label'] for opt in question['options']]
            self.populate_listbox(options, question.get('allows_multiple', False))

    def populate_listbox(self, options, allows_multiple=False):
        """Populate the listbox with provided options."""
        self.response_listbox.config(selectmode=tk.MULTIPLE if allows_multiple else tk.SINGLE)
        self.response_listbox.pack()
        self.response_listbox.delete(0, tk.END)
        for option in options:
            self.response_listbox.insert(tk.END, option)

    def clear_response_widgets(self):
        """Clear all response widgets."""
        self.response_entry.pack_forget()
        self.response_listbox.pack_forget()
        self.response_entry.delete(0, tk.END)
        self.response_listbox.delete(0, tk.END)

    def save_response(self):
        """Save the user's response for the current question."""
        question = self.get_current_question()
        if not question:
            return

        question_id = question['question_id']
        if question['type'] == 'text':
            response = self.response_entry.get()
        elif question['type'] == 'boolean':
            selection = self.response_listbox.curselection()
            response = self.response_listbox.get(selection[0]) if selection else None
        elif question['type'] == 'multiple_choice':
            response = [self.response_listbox.get(i) for i in self.response_listbox.curselection()]
        else:
            response = None

        self.user_responses[question_id] = response

    def next_question(self):
        """Navigate to the next question."""
        self.save_response()
        self.current_question_index += 1
        if self.current_question_index >= len(self.questions_data['sections'][self.current_section_index]['questions']):
            self.next_section()
        else:
            self.load_question()

    def previous_question(self):
        """Navigate to the previous question."""
        self.current_question_index -= 1
        if self.current_question_index < 0:
            self.previous_section()
        else:
            self.load_question()

    def next_section(self):
        """Navigate to the next section."""
        self.current_section_index += 1
        if self.current_section_index >= len(self.questions_data['sections']):
            self.show_summary()
        else:
            self.load_section()

    def previous_section(self):
        """Navigate to the previous section."""
        self.current_section_index -= 1
        if self.current_section_index < 0:
            self.current_section_index = 0
        self.load_section()

    def get_current_question(self):
        """Get the current question based on section and index."""
        try:
            section = self.questions_data['sections'][self.current_section_index]
            return section['questions'][self.current_question_index]
        except (IndexError, KeyError):
            return None

    def show_summary(self):
        """Display a summary of user responses."""
        self.frame.destroy()
        summary_frame = tk.Frame(self.root)
        summary_frame.pack(pady=20)

        tk.Label(summary_frame, text="Summary of Your Responses", font=("Arial", 14)).pack()

        for question_id, response in self.user_responses.items():
            tk.Label(summary_frame, text=f"{question_id}: {response}", wraplength=700, justify=tk.LEFT).pack()

        save_button = tk.Button(summary_frame, text="Save Responses", command=self.save_responses)
        save_button.pack(pady=10)

    def save_responses(self, filename="user_responses.json"):
        """Save user responses to a JSON file."""
        with open(filename, 'w') as f:
            json.dump(self.user_responses, f, indent=4)
        messagebox.showinfo("Saved", f"Responses saved to {filename}")

    def run(self):
        """Run the GUI application."""
        self.root.mainloop()


if __name__ == "__main__":
    question_manager = QuestionManagerGUI("data/questions.json")
    question_manager.run()
