import tkinter as tk
from tkinter import ttk, StringVar, Text, messagebox
import networkx as nx
import matplotlib.pyplot as plt
import sqlite3
import math


class Task:
    def __init__(self, name, duration):
        self.name = name
        self.duration = duration

class Activity(Task):
    def __init__(self, name, duration):
        super().__init__(name, duration)
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
        

        self.activities = []
        self.critical_path = []
        self.cpm_time = 0
        self.graph = nx.DiGraph()

        self.cpmconn = sqlite3.connect("cpm_activities.db")
        self.cursor = self.cpmconn.cursor()
        self.create_table()

        self.create_input_panel()
        self.create_output_panel()
        self.load_activities()

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS activities (
                id INTEGER PRIMARY KEY,
                name TEXT,
                duration INTEGER,
                dependency TEXT
            )
        """)
        self.cpmconn.commit()

    def load_activities(self):
        self.cursor.execute("SELECT * FROM activities")
        rows = self.cursor.fetchall()
        for row in rows:
            name, duration, dependency = row[1], row[2], row[3]
            activity = Activity(name, duration)
            dependencies = dependency.split(",") if dependency else []
            for dep_name in dependencies:
                dep_activity = next((act for act in self.activities if act.name == dep_name), None)
                if dep_activity:
                    activity.add_dependency(dep_activity)
                    self.graph.add_edge(dep_activity.name, name)
            self.activities.append(activity)

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

        # Insert activity into the database
        self.cursor.execute("INSERT INTO activities (name, duration, dependency) VALUES (?, ?, ?)",
                            (name, duration, ",".join(dependencies)))
        self.cpmconn.commit()

        self.activity_name_var.set("")
        self.duration_var.set("")
        self.dependencies_var.set("")

    def delete_activity(self):
        name = self.activity_name_delete_var.get()

        if not name:
            messagebox.showerror("Error", "Please enter the name of the activity to delete.")
            return

        confirmation = messagebox.askokcancel("Confirm Deletion", f"Are you sure you want to delete activity '{name}'?")
        if not confirmation:
            return

        self.cursor.execute("DELETE FROM activities WHERE name=?", (name,))
        self.cpmconn.commit()

        self.activities = [activity for activity in self.activities if activity.name != name]

        self.graph.remove_node(name)

        self.load_activity_listbox()

    def view_activities(self):
        self.cursor.execute("SELECT * FROM activities")
        activities = self.cursor.fetchall()
        for activity in activities:
            print(activity)  

    def load_activity_listbox(self):
        self.activity_listbox.delete(0, tk.END)
        for activity in self.activities:
            self.activity_listbox.insert(tk.END, activity.name)

    def create_input_panel(self):
        input_panel = ttk.LabelFrame(self.root, text="Activity Information", padding=(10, 5), relief="groove")
        input_panel.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        ttk.Label(input_panel, text="Activity Name:").grid(row=0, column=0, sticky="e")
        ttk.Label(input_panel, text="Duration:").grid(row=1, column=0, sticky="e")
        ttk.Label(input_panel, text="Dependencies (comma-separated):").grid(row=2, column=0, sticky="e")

        self.activity_name_var = StringVar()
        self.duration_var = StringVar()
        self.dependencies_var = StringVar()
        self.activity_name_delete_var = StringVar()

        entry_name = ttk.Entry(input_panel, textvariable=self.activity_name_var)
        entry_duration = ttk.Entry(input_panel, textvariable=self.duration_var)
        entry_dependencies = ttk.Entry(input_panel, textvariable=self.dependencies_var)
        entry_name_delete = ttk.Entry(input_panel, textvariable=self.activity_name_delete_var)

        entry_name.grid(row=0, column=1, padx=5, pady=5)
        entry_duration.grid(row=1, column=1, padx=5, pady=5)
        entry_dependencies.grid(row=2, column=1, padx=5, pady=5)
        entry_name_delete.grid(row=3, column=1, padx=5, pady=5)

        ttk.Button(input_panel, text="Add Activity", command=self.add_activity).grid(row=4, column=0, columnspan=2, pady=10)
        ttk.Button(input_panel, text="Delete Activity", command=self.delete_activity).grid(row=5, column=0, columnspan=2, pady=10)
        ttk.Button(input_panel, text="Calculate CPM", command=self.calculate_cpm).grid(row=6, column=0, columnspan=2, pady=10)
        ttk.Button(input_panel, text="View Activities", command=self.view_activities).grid(row=7, column=0, columnspan=2, pady=10)

        self.activity_listbox = tk.Listbox(input_panel, selectmode=tk.SINGLE)
        self.activity_listbox.grid(row=8, column=0, columnspan=2, pady=10)

    def create_output_panel(self):
        output_panel = ttk.Frame(self.root)
        output_panel.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.result_text = Text(output_panel, height=10, width=40)
        self.result_text.config(state=tk.DISABLED)
        self.result_text.grid(row=0, column=0)

    def calculate_cpm(self):
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)

        try:
            self.calculate_cpm_core()

            self.result_text.insert(tk.END, "\nCritical Path:\n")
            for activity in reversed(self.critical_path):
                self.result_text.insert(tk.END, activity.name + "\n")

            self.result_text.insert(tk.END, "\nCPM Time: " + str(self.cpm_time))
        except Exception as e:
            messagebox.showerror("Error", f"Error in calculating CPM: {str(e)}")

        self.result_text.config(state=tk.DISABLED)

        self.display_graph()

    def calculate_cpm_core(self):
        if len(self.activities) == 0:
            messagebox.showwarning("Warning", "Please add activities before calculating CPM.")
            return

        start_activity = self.activities[0]
        start_activity.earliest_start = 0
        start_activity.earliest_finish = start_activity.duration

        for current_activity in self.activities[1:]:
            max_earliest_finish = 0
            for dependency in current_activity.dependencies:
                if dependency.earliest_finish > max_earliest_finish:
                    max_earliest_finish = dependency.earliest_finish
            current_activity.earliest_start = max_earliest_finish
            current_activity.earliest_finish = current_activity.earliest_start + current_activity.duration

        end_activity = self.activities[-1]
        end_activity.latest_finish = end_activity.earliest_finish
        end_activity.latest_start = end_activity.latest_finish - end_activity.duration

        self.critical_path.append(end_activity)

        for current_activity in reversed(self.activities[:-1]):
            min_latest_start = float('inf')
            for dependent_activity in self.activities:
                if current_activity in dependent_activity.dependencies:
                    latest_start = dependent_activity.latest_start - current_activity.duration
                    min_latest_start = min(min_latest_start, latest_start)

            current_activity.latest_start = min_latest_start
            current_activity.latest_finish = current_activity.latest_start + current_activity.duration

            current_activity.slack = current_activity.latest_start - current_activity.earliest_start

            if current_activity.slack == 0 or current_activity == end_activity:
                current_activity.set_critical_path(True)
                self.critical_path.append(current_activity)

        self.cpm_time = end_activity.earliest_finish

    def display_graph(self):
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
    def __init__(self, root):
        self.root = root
        self.tasks = []
        self.load_tasks_from_db()

        self.create_widgets()

    def create_widgets(self):
        input_frame = ttk.LabelFrame(self.root, text="Task Information", padding=(10, 5), relief="groove")
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        output_frame = ttk.Frame(self.root)
        output_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        ttk.Label(input_frame, text="Task Name", font=("Helvetica", 12)).grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(input_frame, text="Optimistic Duration", font=("Helvetica", 12)).grid(row=1, column=0, padx=5, pady=5)
        ttk.Label(input_frame, text="Most Likely Duration", font=("Helvetica", 12)).grid(row=2, column=0, padx=5, pady=5)
        ttk.Label(input_frame, text="Pessimistic Duration", font=("Helvetica", 12)).grid(row=3, column=0, padx=5, pady=5)

        style = ttk.Style()
        style.configure("TEntry", padding=5, font=("Helvetica", 12), background="#EFEFEF")

        self.name_entry = ttk.Entry(input_frame, style="TEntry")
        self.optimistic_entry = ttk.Entry(input_frame, style="TEntry")
        self.most_likely_entry = ttk.Entry(input_frame, style="TEntry")
        self.pessimistic_entry = ttk.Entry(input_frame, style="TEntry")

        self.name_entry.grid(row=0, column=1, padx=5, pady=5)
        self.optimistic_entry.grid(row=1, column=1, padx=5, pady=5)
        self.most_likely_entry.grid(row=2, column=1, padx=5, pady=5)
        self.pessimistic_entry.grid(row=3, column=1, padx=5, pady=5)

        style.configure("TButton", padding=5, font=("Helvetica", 12), background="#4CAF50", foreground="#000000")

        ttk.Button(input_frame, text="Add Task", command=self.add_task, style="TButton").grid(row=4, column=0, columnspan=2, pady=(10, 0))
        ttk.Button(input_frame, text="Calculate PERT", command=self.calculate_pert, style="TButton").grid(row=5, column=0, columnspan=2, pady=(10, 0))
        ttk.Button(input_frame, text="View Tasks", command=self.view_tasks, style="TButton").grid(row=6, column=0, columnspan=2, pady=(10, 0))
        ttk.Button(input_frame, text="Delete Task", command=self.delete_task, style="TButton").grid(row=7, column=0, columnspan=2, pady=(10, 0))

        self.output_text = Text(output_frame, height=10, width=30, font=("Helvetica", 12))
        self.output_text.config(state="disabled", wrap="word")
        self.output_text.grid(row=0, column=0)

    def add_task(self):
        name = self.name_entry.get()
        optimistic = int(self.optimistic_entry.get())
        most_likely = int(self.most_likely_entry.get())
        pessimistic = int(self.pessimistic_entry.get())

        task = PERTTask(name, optimistic, most_likely, pessimistic)
        self.tasks.append(task)
        self.save_task_to_db(task)

        self.name_entry.delete(0, tk.END)
        self.optimistic_entry.delete(0, tk.END)
        self.most_likely_entry.delete(0, tk.END)
        self.pessimistic_entry.delete(0, tk.END)

    def save_task_to_db(self, task):
        conn = sqlite3.connect('pert_tasks.db')
        c = conn.cursor()
        c.execute("INSERT INTO tasks VALUES (?, ?, ?, ?, ?)", (task.name, task.optimistic, task.most_likely, task.pessimistic, task.expected))
        conn.commit()
        conn.close()

    def load_tasks_from_db(self):
        conn = sqlite3.connect('pert_tasks.db')
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS tasks (name TEXT, optimistic INTEGER, most_likely INTEGER, pessimistic INTEGER, expected REAL)")
        conn.commit()

        c.execute("SELECT * FROM tasks")
        rows = c.fetchall()
        for row in rows:
            task = PERTTask(row[0], row[1], row[2], row[3])
            self.tasks.append(task)
        conn.close()

    def view_tasks(self):
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", tk.END)

        for task in self.tasks:
            self.output_text.insert(tk.END, f"{task.name}\n")

        self.output_text.config(state="disabled")

    def delete_task(self):
        task_name = self.name_entry.get()

        if not task_name:
            messagebox.showerror("Error", "Please enter a task name to delete.")
            return

        conn = sqlite3.connect('pert_tasks.db')
        c = conn.cursor()

        c.execute("DELETE FROM tasks WHERE name=?", (task_name,))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", f"Task '{task_name}' deleted successfully.")
        self.name_entry.delete(0, tk.END)

    def calculate_pert(self):
        if not self.tasks:
            messagebox.showerror("Error", "Please add tasks before calculating PERT.")
            return

        total_expected = 0.0
        total_variance = 0.0

        for task in self.tasks:
            task_expected = task.expected
            task_variance = task.variance

            total_expected += task_expected
            total_variance += task_variance

        project_time = total_expected
        project_variance = total_variance
        project_standard_deviation = math.sqrt(total_variance)

        self.output_text.config(state="normal")
        self.output_text.delete("1.0", tk.END)

        self.output_text.insert(tk.END, f"Expected Project Duration: {project_time} units\n")
        self.output_text.insert(tk.END, f"Project Variance: {project_variance} units^2\n")
        self.output_text.insert(tk.END, f"Project Standard Deviation: {project_standard_deviation} units\n")

        self.output_text.config(state="disabled")


def main():
    root = tk.Tk()
    root.geometry("800x600")

    notebook = ttk.Notebook(root)
    notebook.pack(fill='both', expand=True)

    cpm_tab = ttk.Frame(notebook)
    pert_tab = ttk.Frame(notebook)

    notebook.add(cpm_tab, text="CPM Calculator")
    notebook.add(pert_tab, text="PERT Calculator")

    CPMCalculatorGUI(cpm_tab)
    PERTCalculatorGUI(pert_tab)

    root.mainloop()

if __name__ == "__main__":
    main()
