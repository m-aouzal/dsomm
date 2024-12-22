import json

class QuestionManager:
    def __init__(self, questions_file):
        with open(questions_file, 'r') as f:
            self.questions_data = json.load(f)
        self.user_responses = {}
        self.selected_stages = []

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

    def ask_question(self, question):
        print(question['text'])
        if question['type'] == 'text':
            response = input("Your answer: ")
            self.user_responses[question['question_id']] = response
        elif question['type'] == 'boolean':
            while True:
                response = input("Your answer (yes/no): ").lower()
                if response in ['yes', 'no']:
                    self.user_responses[question['question_id']] = response == 'yes'
                    break
                else:
                    print("Invalid input. Please enter 'yes' or 'no'.")
        elif question['type'] == 'multiple_choice':
            for i, option in enumerate(question['options']):
                print(f"{i + 1}. {option['label']}")
            if question.get('allows_multiple', False):
                print("Enter numbers of your choices separated by commas (e.g., 1,3,4) or 'none' for no selection:")
            else:
                print("Enter the number of your choice or 'none' for no selection:")

            while True:
                response = input("Your answer: ").lower()
                if response == 'none' or response == '':
                    self.user_responses[question['question_id']] = [] if question.get('allows_multiple', False) else None
                    break

                try:
                    if question.get('allows_multiple', False):
                        selected_indices = [int(x.strip()) - 1 for x in response.split(',')]
                    else:
                        selected_indices = [int(response.strip()) - 1]

                    selected_options = []
                    invalid_input = False
                    for index in selected_indices:
                        if 0 <= index < len(question['options']):
                            selected_options.append(question['options'][index]['value'])
                        else:
                            print("Invalid choice. Please enter valid number(s).")
                            invalid_input = True
                            break

                    if not invalid_input:
                        self.user_responses[question['question_id']] = selected_options
                        break
                except ValueError:
                    print("Invalid input. Please enter valid number(s) or 'none'.")

    def process_section(self, section_name):
        section = self.get_section(section_name)
        if not section:
            print(f"Section '{section_name}' not found.")
            return

        for question in section['questions']:
            if self.should_ask_question(question):
                self.ask_question(question)
                if section_name == "Stage Selection" and question["question_id"] == "stages_implemented":
                    self.selected_stages = self.user_responses["stages_implemented"]

    
    def should_ask_question(self, question):
        depends_on = question.get('depends_on')
        if not depends_on:
            return True

        if depends_on['question_id'] == "stages_implemented":
            return depends_on['value'] in self.user_responses.get("stages_implemented", [])

        if depends_on['question_id'] not in self.user_responses:
            return False  # Dependency question hasn't been asked yet

        dependency_value = self.user_responses[depends_on['question_id']]

        if isinstance(dependency_value, list):
            return depends_on['value'] in dependency_value
        else:
            return dependency_value == depends_on['value']

    def run(self):
        self.process_section("Introduction")
        self.process_section("Stage Selection")

        for stage in self.selected_stages:
            section_name = next((s['name'] for s in self.questions_data['sections'] if s.get('stage_id') == stage), None)
            if section_name:
                self.process_section(section_name)

        print("\nThank you for answering the questions!")
        print("Here's a summary of your responses:")
        for question_id, response in self.user_responses.items():
            question = self.get_question(question_id)
            if question:
                print(f"\n{question['text']}")
                if question['type'] == 'multiple_choice':
                    if not response:
                        print("None")
                    else:
                         for option in question['options']:
                            if option['value'] in response:
                                print(f"- {option['label']}")
                else:
                     print(f"Answer: {response}")

    def save_responses(self, filename="user_responses.json"):
        with open(filename, 'w') as f:
            json.dump(self.user_responses, f, indent=4)

if __name__ == "__main__":
    question_manager = QuestionManager("data/questions.json")
    question_manager.run()
    question_manager.save_responses()