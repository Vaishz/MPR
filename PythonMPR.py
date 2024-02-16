import tkinter as tk
from tkinter import ttk, StringVar, Entry, Label, Button, Text, messagebox
import networkx as nx
import matplotlib.pyplot as plt
import math


class Activity:
    def __init__(self, name, duration):
        self.name = name
        self.duration = duration
        self.dependencies = []
        self.earliest_start = 0
        self.earliest_finish = 0
        self.latest_start = 0
        self.latest_finish = 0
        self.slack = 0
        self.critical_path = False

    def add_dependency(self, activity):
        self.dependencies.append(activity)

    def is_critical_path(self):
        return self.critical_path

    def set_critical_path(self, is_critical):
        self.critical_path = is_critical


class CPMCalculatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CPM Calculator")

        self.activities = []
        self.critical_path = []
        self.cpm_time = 0
        self.graph = nx.DiGraph()

        self.create_input_panel()
        self.create_output_panel()

    def create_input_panel(self):
        input_panel = ttk.LabelFrame(self.root, text="Activity Information", padding=(10, 5), relief="groove")
        input_panel.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        ttk.Label(input_panel, text="Activity Name:").grid(row=0, column=0, sticky="e")
        ttk.Label(input_panel, text="Duration:").grid(row=1, column=0, sticky="e")
        ttk.Label(input_panel, text="Dependencies (comma-separated):").grid(row=2, column=0, sticky="e")

        self.activity_name_var = StringVar()
        self.duration_var = StringVar()
        self.dependencies_var = StringVar()

        entry_name = ttk.Entry(input_panel, textvariable=self.activity_name_var)
        entry_duration = ttk.Entry(input_panel, textvariable=self.duration_var)
        entry_dependencies = ttk.Entry(input_panel, textvariable=self.dependencies_var)

        entry_name.grid(row=0, column=1, padx=5, pady=5)
        entry_duration.grid(row=1, column=1, padx=5, pady=5)
        entry_dependencies.grid(row=2, column=1, padx=5, pady=5)

        ttk.Button(input_panel, text="Add Activity", command=self.add_activity).grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Button(input_panel, text="Calculate CPM", command=self.calculate_cpm).grid(row=4, column=0, columnspan=2, pady=10)

    def create_output_panel(self):
        output_panel = ttk.Frame(self.root)
        output_panel.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.result_text = Text(output_panel, height=10, width=40)
        self.result_text.config(state=tk.DISABLED)
        self.result_text.grid(row=0, column=0)

    def add_activity(self):
        name = self.activity_name_var.get()
        duration_text = self.duration_var.get()
        dependencies_text = self.dependencies_var.get()

        if not name or not duration_text:
            messagebox.showerror("Error", "Please fill in both activity name and duration.")
            return

        try:
            duration = int(duration_text)
            if duration <= 0:
                raise ValueError("Duration must be greater than zero.")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input for duration: {str(e)}")
            return

        dependencies = [dep.strip() for dep in dependencies_text.split(',')]

        activity = Activity(name, duration)

        for dependency in dependencies:
            dependency_activity = next((a for a in self.activities if a.name == dependency), None)
            if dependency_activity:
                activity.add_dependency(dependency_activity)
                self.graph.add_edge(dependency_activity.name, name)

        self.activities.append(activity)

        self.activity_name_var.set("")
        self.duration_var.set("")
        self.dependencies_var.set("")

    def calculate_cpm(self):
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)

        # Calculate CPM and display result
        try:
            self.calculate_cpm_core()

            # Display result in the GUI
            self.result_text.insert(tk.END, "\nCritical Path:\n")
            for activity in reversed(self.critical_path):
                self.result_text.insert(tk.END, activity.name + "\n")

            self.result_text.insert(tk.END, "\nCPM Time: " + str(self.cpm_time))
        except Exception as e:
            messagebox.showerror("Error", f"Error in calculating CPM: {str(e)}")

        self.result_text.config(state=tk.DISABLED)

        # Visualize the graph
        self.display_graph()

    def calculate_cpm_core(self):
        if len(self.activities) == 0:
            messagebox.showwarning("Warning", "Please add activities before calculating CPM.")
            return

        start_activity = self.activities[0]
        start_activity.earliest_start = 0
        start_activity.earliest_finish = start_activity.duration

        # Perform forward pass
        for current_activity in self.activities[1:]:
            max_earliest_finish = 0
            for dependency in current_activity.dependencies:
                if dependency.earliest_finish > max_earliest_finish:
                    max_earliest_finish = dependency.earliest_finish
            current_activity.earliest_start = max_earliest_finish
            current_activity.earliest_finish = current_activity.earliest_start + current_activity.duration

        # Calculate latest start and finish times for the last activity
        end_activity = self.activities[-1]
        end_activity.latest_finish = end_activity.earliest_finish
        end_activity.latest_start = end_activity.latest_finish - end_activity.duration

        self.critical_path.append(end_activity)

        # Perform backward pass
        for current_activity in reversed(self.activities[:-1]):
            min_latest_start = float('inf')
            for dependent_activity in self.activities:
                if current_activity in dependent_activity.dependencies:
                    latest_start = dependent_activity.latest_start - current_activity.duration
                    min_latest_start = min(min_latest_start, latest_start)

            current_activity.latest_start = min_latest_start
            current_activity.latest_finish = current_activity.latest_start + current_activity.duration

            # Calculate slack for current_activity
            current_activity.slack = current_activity.latest_start - current_activity.earliest_start

            # Check if current_activity is on the critical path
            if current_activity.slack == 0 or current_activity == end_activity:
                current_activity.set_critical_path(True)
                self.critical_path.append(current_activity)

        # Calculate the CPM time
        self.cpm_time = end_activity.earliest_finish

    def display_graph(self):
        # Visualize the graph
        pos = nx.spring_layout(self.graph)
        nx.draw(self.graph, pos, with_labels=True, font_weight='bold', node_color='blue', font_color='white')
        nx.draw_networkx_nodes(self.graph, pos, nodelist=[activity.name for activity in self.critical_path], node_color='red')
        plt.title("Activity Graph")
        plt.show()


class PERTTask:
    def __init__(self, name, optimistic, most_likely, pessimistic):
        self.name = name
        self.optimistic = optimistic
        self.most_likely = most_likely
        self.pessimistic = pessimistic
        self.expected = self.calculate_expected()
        self.variance = self.calculate_variance()

    def calculate_expected(self):
        return (self.optimistic + 4 * self.most_likely + self.pessimistic) / 6

    def calculate_variance(self):
        return ((self.pessimistic - self.optimistic) / 6) ** 2


class PERTCalculatorGUI:
    def __init__(self):
        self.tasks = []
        self.project_time = 0.0
        self.project_variance = 0.0
        self.project_standard_deviation = 0.0

        self.root = tk.Tk()
        self.root.title("PERT Calculator")

        self.create_widgets()

    def create_widgets(self):
        input_frame = ttk.LabelFrame(self.root, text="Task Information", padding=(10, 5), relief="groove")
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        output_frame = ttk.Frame(self.root)
        output_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        ttk.Label(input_frame, text="Task Name", font=("Helvetica", 12)).grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(input_frame, text="Optimistic Duration", font=("Helvetica", 12)).grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(input_frame, text="Most Likely Duration", font=("Helvetica", 12)).grid(row=0, column=2, padx=5, pady=5)
        ttk.Label(input_frame, text="Pessimistic Duration", font=("Helvetica", 12)).grid(row=0, column=3, padx=5, pady=5)

        style = ttk.Style()

        style.configure("TEntry", padding=5, font=("Helvetica", 12), background="#EFEFEF")  # Light gray background

        self.name_entry = ttk.Entry(input_frame, style="TEntry")
        self.optimistic_entry = ttk.Entry(input_frame, style="TEntry")
        self.most_likely_entry = ttk.Entry(input_frame, style="TEntry")
        self.pessimistic_entry = ttk.Entry(input_frame, style="TEntry")

        self.name_entry.grid(row=1, column=0, padx=5, pady=5)
        self.optimistic_entry.grid(row=1, column=1, padx=5, pady=5)
        self.most_likely_entry.grid(row=1, column=2, padx=5, pady=5)
        self.pessimistic_entry.grid(row=1, column=3, padx=5, pady=5)

        style.configure("TButton", padding=5, font=("Helvetica", 12), background="#4CAF50", foreground="#000000")  # Green background, black text

        ttk.Button(input_frame, text="Calculate PERT", command=self.calculate_pert, style="TButton").grid(row=2, column=0, columnspan=4, pady=(10, 0))
        ttk.Button(input_frame, text="Clear Screen", command=self.clear_screen, style="TButton").grid(row=3, column=0, columnspan=4, pady=(10, 0))

        self.output_text = Text(output_frame, height=10, width=30, font=("Helvetica", 12))
        self.output_text.config(state="disabled", wrap="word")
        self.output_text.grid(row=0, column=0)

    def calculate_pert(self):
        try:
            name = self.name_entry.get()
            optimistic_text = self.optimistic_entry.get()
            most_likely_text = self.most_likely_entry.get()
            pessimistic_text = self.pessimistic_entry.get()

            if not name or not optimistic_text or not most_likely_text or not pessimistic_text:
                messagebox.showerror("Error", "Please fill in all fields.")
                return

            optimistic = int(optimistic_text)
            most_likely = int(most_likely_text)
            pessimistic = int(pessimistic_text)

            if optimistic < 0 or most_likely < 0 or pessimistic < 0:
                raise ValueError("Time estimates cannot be negative.")

            task = PERTTask(name, optimistic, most_likely, pessimistic)
            self.tasks.append(task)

            self.calculate_pert_values()
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")

    def calculate_pert_values(self):
        total_expected = 0.0
        total_variance = 0.0

        for task in self.tasks:
            task_expected = task.expected
            task_variance = task.variance

            total_expected += task_expected
            total_variance += task_variance

        self.project_time = total_expected
        self.project_variance = total_variance
        self.project_standard_deviation = math.sqrt(total_variance)

        self.display_pert_results()

    def display_pert_results(self):
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", tk.END)

        self.output_text.insert(tk.END, f"PERT Project Time: {self.project_time:.2f}\n")
        self.output_text.insert(tk.END, f"Variance of Total Project: {self.project_variance:.2f}\n")
        self.output_text.insert(tk.END, f"Standard Deviation: {self.project_standard_deviation:.2f}\n")
        self.output_text.insert(tk.END, "Probability of Completion:\n")

        for task in self.tasks:
            probability = self.calculate_probability(task.expected, task.variance)
            self.output_text.insert(tk.END, f"{task.name}: {probability:.2f}\n")

        self.output_text.config(state="disabled")

    def calculate_probability(self, expected, variance):
        z = (self.project_time - expected) / self.project_standard_deviation
        return 1 - self.cumulative_distribution(z)

    def cumulative_distribution(self, z):
        t = 1 / (1 + 0.2316419 * abs(z))
        y = (((((1.330274429 * t - 1.821255978) * t + 1.781477937) * t - 0.356563782) * t + 0.319381530) * t) / (2 * math.pi) + 0.5

        if z > 0:
            return 1 - y
        else:
            return y

    def clear_screen(self):
        self.tasks.clear()
        self.project_time = 0.0
        self.project_variance = 0.0
        self.project_standard_deviation = 0.0
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", tk.END)
        self.output_text.config(state="disabled")
        self.name_entry.delete(0, tk.END)
        self.optimistic_entry.delete(0, tk.END)
        self.most_likely_entry.delete(0, tk.END)
        self.pessimistic_entry.delete(0, tk.END)

    def run(self):
        self.root.mainloop()


class CalculatorMenu:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PERT and CPM Calculator")

        self.create_menu()

    def create_menu(self):
        menu_frame = ttk.Frame(self.root, padding=(10, 5), relief="groove")
        menu_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        ttk.Button(menu_frame, text="PERT Calculator", command=self.run_pert_calculator).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(menu_frame, text="CPM Calculator", command=self.run_cpm_calculator).grid(row=0, column=1, padx=5, pady=5)

    def run_pert_calculator(self):
        pert_calculator = PERTCalculatorGUI()
        pert_calculator.run()

    def run_cpm_calculator(self):
        cpm_calculator = CPMCalculatorGUI(self.root)
        self.root.mainloop()


if __name__ == "__main__":
    calculator_menu = CalculatorMenu()
    calculator_menu.root.mainloop()
