import json
import tkinter as tk
from tkinter import ttk, messagebox

class QuestionManagerGUI:
    def __init__(self, questions_file, pipeline_file):
        with open(questions_file, 'r') as f:
            self.questions_data = json.load(f)

        with open(pipeline_file, 'r') as f:
            self.pipeline_data = json.load(f)

        self.user_responses = {}
        self.selected_stages = []
        self.current_section_index = 0
        self.current_question_index = 0

        self.root = tk.Tk()
        self.root.title("DevSecOps Tool Selector")
        self.root.geometry("950x750")

        self.frame = tk.Frame(self.root, padx=20, pady=20)
        self.frame.pack(fill="both", expand=True)

        self.question_label = tk.Label(self.frame, text="", wraplength=800, justify=tk.LEFT)
        self.question_label.pack()

        self.response_entry = tk.Entry(self.frame)
        self.response_entry.pack()

        self.response_listbox = tk.Listbox(self.frame, selectmode=tk.SINGLE)
        self.response_listbox.pack()

        self.next_button = tk.Button(self.frame, text="Next", command=self.next_question)
        self.next_button.pack(side="right", padx=10)

        self.prev_button = tk.Button(self.frame, text="Previous", command=self.previous_question)
        self.prev_button.pack(side="left", padx=10)

        self.load_section()

    def load_section(self):
        """Load the current section and its questions."""
        while True:
            if isinstance(self.questions_data, list):
                if self.current_section_index >= len(self.questions_data):
                    self.show_summary()
                    return
                current_stage = self.questions_data[self.current_section_index]
            else:
                if self.current_section_index >= len(self.questions_data.get('sections', [])):
                    self.show_summary()
                    return
                current_stage = self.questions_data['sections'][self.current_section_index]

            if current_stage.get('questions'):
                self.current_question_index = 0
                self.load_question()
                break
            else:
                self.current_section_index += 1

    def load_question(self):
        """Load the current question based on section and question index."""
        self.clear_response_widgets()
        question = self.get_current_question()

        if not question or not self.should_ask_question(question):
            self.next_section()
            return

        self.question_label.config(text=question['text'])

        if question['type'] == 'text':
            self.response_entry.pack()
        elif question['type'] in ['boolean', 'multiple_choice']:
            self.response_listbox.pack()
            self.response_listbox.delete(0, tk.END)
            if question['type'] == 'boolean':
                self.response_listbox.insert(tk.END, "Yes")
                self.response_listbox.insert(tk.END, "No")
            elif question['type'] == 'multiple_choice':
                allows_multiple = question.get('allows_multiple', False)
                self.response_listbox.config(selectmode=tk.MULTIPLE if allows_multiple else tk.SINGLE)
                for option in question['options']:
                    self.response_listbox.insert(tk.END, option['label'])

    def clear_response_widgets(self):
        """Clear input fields."""
        self.response_entry.pack_forget()
        self.response_listbox.pack_forget()
        self.response_entry.delete(0, tk.END)
        self.response_listbox.delete(0, tk.END)

    def get_current_question(self):
        """Get the current question."""
        if isinstance(self.questions_data, list):
            if 0 <= self.current_section_index < len(self.questions_data):
                section = self.questions_data[self.current_section_index]
                if 0 <= self.current_question_index < len(section.get('questions', [])):
                    return section['questions'][self.current_question_index]
        elif isinstance(self.questions_data, dict):
            if 0 <= self.current_section_index < len(self.questions_data.get('sections', [])):
                section = self.questions_data['sections'][self.current_section_index]
                if 0 <= self.current_question_index < len(section.get('questions', [])):
                    return section['questions'][self.current_question_index]
        return None

    def preprocess_response(self, response, question_type):
        """Preprocess the user response based on question type."""
        if question_type == 'text':
            return response.strip()
        elif question_type == 'boolean':
            return response.lower() == 'yes'
        elif question_type == 'multiple_choice':
            return [option.strip() for option in response] if isinstance(response, list) else []
        return response

    def save_response(self):
        """Save the response to the current question."""
        question = self.get_current_question()
        if not question:
            return

        question_id = question['question_id']
        if question['type'] == 'text':
            raw_response = self.response_entry.get()
            response = self.preprocess_response(raw_response, 'text')
        elif question['type'] == 'boolean':
            selection = self.response_listbox.curselection()
            raw_response = self.response_listbox.get(selection[0]) if selection else ""
            response = self.preprocess_response(raw_response, 'boolean')
        elif question['type'] == 'multiple_choice':
            selections = self.response_listbox.curselection()
            raw_response = [self.response_listbox.get(i) for i in selections]
            response = self.preprocess_response(raw_response, 'multiple_choice')
        else:
            response = None

        self.user_responses[question_id] = response

    def next_question(self):
        """Navigate to the next question."""
        self.save_response()
        self.current_question_index += 1
        if isinstance(self.questions_data, list):
            section_questions = self.questions_data[self.current_section_index].get('questions', [])
        else:
            section_questions = self.questions_data['sections'][self.current_section_index].get('questions', [])

        if self.current_question_index >= len(section_questions):
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
        if isinstance(self.questions_data, list):
            sections_length = len(self.questions_data)
        else:
            sections_length = len(self.questions_data.get('sections', []))

        if self.current_section_index >= sections_length:
            self.show_summary()
        else:
            self.load_section()

    def previous_section(self):
        """Navigate to the previous section."""
        self.current_section_index -= 1
        if self.current_section_index < 0:
            self.current_section_index = 0
        self.load_section()

    def should_ask_question(self, question):
        """Determine whether to ask the question based on dependencies."""
        depends_on = question.get('depends_on')
        if not depends_on:
            return True

        dependency_value = self.user_responses.get(depends_on['question_id'])
        return dependency_value == depends_on['value']

    def show_summary(self):
        """Display a summary of user responses."""
        self.frame.destroy()

        summary_frame = tk.Frame(self.root, padx=20, pady=20)
        summary_frame.pack(fill="both", expand=True)

        tk.Label(summary_frame, text="Summary of Responses", font=("Arial", 14)).pack(pady=10)

        for question_id, response in self.user_responses.items():
            question = self.get_current_question()
            if question:
                tk.Label(summary_frame, text=f"{question['text']}").pack(anchor="w")
                tk.Label(summary_frame, text=f"Answer: {response}").pack(anchor="w")

        save_button = tk.Button(summary_frame, text="Save Responses", command=self.save_responses)
        save_button.pack(pady=20)

    def save_responses(self, filename="../data/user_responses.json"):
        """Save user responses to a file."""
        with open(filename, 'w') as f:
            json.dump(self.user_responses, f, indent=4)
        messagebox.showinfo("Saved", f"Responses saved to {filename}")

    def run(self):
        """Run the GUI."""
        self.root.mainloop()

if __name__ == "__main__":
    question_manager = QuestionManagerGUI("../data/generated_questions.json", "../data/updated_pipeline_order.json")
    question_manager.run()
