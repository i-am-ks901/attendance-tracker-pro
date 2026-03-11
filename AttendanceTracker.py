import customtkinter as ctk
from tkinter import ttk, messagebox
import json
import os
import math
import sys
from datetime import datetime

# Determine path for executable storage reliability
def get_data_dir():
    """Returns a consistent data directory cross-platform for storing user data."""
    home_dir = os.path.expanduser("~")
    app_data_dir = os.path.join(home_dir, ".AttendanceTrackerPro")
    
    if not os.path.exists(app_data_dir):
        os.makedirs(app_data_dir)
        
    return app_data_dir

DATA_FILE = os.path.join(get_data_dir(), "attendance_data.json")

# Set Appearance
ctk.set_appearance_mode("System")  
ctk.set_default_color_theme("blue")

class AddSubjectDialog(ctk.CTkToplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.title("Add/Edit Subject")
        self.geometry("420x550")
        self.minsize(350, 500)
        self.callback = callback
        
        self.transient(parent)
        self.grab_set()
        
        self.title_label = ctk.CTkLabel(self, text="📚 Add New Subject", font=ctk.CTkFont(size=22, weight="bold"))
        self.title_label.pack(pady=(20, 10))

        form_frame = ctk.CTkFrame(self, fg_color="transparent")
        form_frame.pack(fill=ctk.BOTH, expand=True, padx=30, pady=10)
        
        ctk.CTkLabel(form_frame, text="Subject Name:", font=ctk.CTkFont(weight="bold"), anchor="w").pack(fill=ctk.X, pady=(0, 2))
        self.name_var = ctk.StringVar()
        self.name_entry = ctk.CTkEntry(form_frame, textvariable=self.name_var, placeholder_text="e.g. Mathematics", height=35)
        self.name_entry.pack(fill=ctk.X, pady=(0, 15))
        
        ctk.CTkLabel(form_frame, text="Total Classes Held (so far):", font=ctk.CTkFont(weight="bold"), anchor="w").pack(fill=ctk.X, pady=(0, 2))
        self.total_var = ctk.StringVar(value="0")
        self.total_entry = ctk.CTkEntry(form_frame, textvariable=self.total_var, height=35)
        self.total_entry.pack(fill=ctk.X, pady=(0, 15))
        
        ctk.CTkLabel(form_frame, text="Attended Classes (so far):", font=ctk.CTkFont(weight="bold"), anchor="w").pack(fill=ctk.X, pady=(0, 2))
        self.attended_var = ctk.StringVar(value="0")
        self.attended_entry = ctk.CTkEntry(form_frame, textvariable=self.attended_var, height=35)
        self.attended_entry.pack(fill=ctk.X, pady=(0, 15))
        
        ctk.CTkLabel(form_frame, text="Target Percentage (%):", font=ctk.CTkFont(weight="bold"), anchor="w").pack(fill=ctk.X, pady=(0, 2))
        self.target_var = ctk.StringVar(value="75")
        self.target_entry = ctk.CTkEntry(form_frame, textvariable=self.target_var, height=35)
        self.target_entry.pack(fill=ctk.X, pady=(0, 15))
        
        # Dynamic calculation label
        self.dynamic_stats_frame = ctk.CTkFrame(form_frame, corner_radius=8, fg_color=("#e5e7eb", "#2a2d2e"))
        self.dynamic_stats_frame.pack(fill=ctk.X, pady=(5, 20))
        
        self.dynamic_stats_label = ctk.CTkLabel(self.dynamic_stats_frame, text="Enter details to see percentage...", font=ctk.CTkFont(size=13), text_color="gray", wraplength=320)
        self.dynamic_stats_label.pack(padx=10, pady=10)
        
        # Trace inputs to update stats dynamically
        self.total_var.trace_add("write", self.update_dynamic_stats)
        self.attended_var.trace_add("write", self.update_dynamic_stats)
        self.target_var.trace_add("write", self.update_dynamic_stats)
        
        self.update_dynamic_stats() # initialize trigger
        
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(fill=ctk.X)
        self.cancel_btn = ctk.CTkButton(btn_frame, text="Cancel", command=self.destroy, fg_color="transparent", border_width=1, text_color=("gray10", "gray90"), height=40)
        self.cancel_btn.pack(side=ctk.LEFT, expand=True, padx=(0, 5))
        self.save_btn = ctk.CTkButton(btn_frame, text="Save Tracker", command=self.save, height=40)
        self.save_btn.pack(side=ctk.LEFT, expand=True, padx=(5, 0))

    def update_dynamic_stats(self, *args):
        try:
            total_str = self.total_var.get().strip()
            attended_str = self.attended_var.get().strip()
            target_str = self.target_var.get().strip()
            
            if not total_str or not attended_str or not target_str:
                self.dynamic_stats_label.configure(text="Awaiting complete input...", text_color="gray")
                return
                
            total = int(total_str)
            attended = int(attended_str)
            target = float(target_str)
            
            if total < 0 or attended < 0 or target < 0 or target > 100:
                self.dynamic_stats_label.configure(text="⚠️ Invalid range. Percentages must be 0-100.", text_color="#ef4444")
                return
            if attended > total:
                self.dynamic_stats_label.configure(text="⚠️ Attended cannot be greater than Total classes.", text_color="#ef4444")
                return
                
            percentage = (attended / total * 100) if total > 0 else 0.0
            
            # Predict the status
            if total == 0:
                msg = f"Current: 0.0%  |  Target: {target}%\nClasses haven't started yet."
                color = ("black", "white")
            elif percentage >= target:
                if target > 0:
                    can_miss = math.floor((attended - (target/100.0) * total) / (target/100.0))
                    msg = f"Current: {percentage:.1f}%\nYou are SAFE! You can safely miss {can_miss} class(es)." if can_miss > 0 else f"Current: {percentage:.1f}%\nYou are exactly on track. Do not miss the next class!"
                else:
                    msg = f"Current: {percentage:.1f}%\nTarget is 0%, you are safe."
                color = "#10b981" # Green
            else:
                if target < 100:
                    must_attend = math.ceil(((target/100.0) * total - attended) / (1.0 - (target/100.0)))
                    msg = f"Current: {percentage:.1f}%\nYou are SHORT! Must attend {must_attend} class(es) to reach target."
                else:
                    msg = f"Current: {percentage:.1f}%\nTarget is 100%, impossible to reach."
                color = "#ef4444" # Red
                
            self.dynamic_stats_label.configure(text=msg, text_color=color)

        except ValueError:
             self.dynamic_stats_label.configure(text="⚠️ Please enter valid integers.", text_color="#ef4444")

        
    def save(self):
        name = self.name_var.get().strip()
        try:
            total = int(self.total_var.get())
            attended = int(self.attended_var.get())
            target = float(self.target_var.get())
            
            if not name:
                messagebox.showerror("Error", "Subject name cannot be empty.", parent=self)
                return
            if total < 0 or attended < 0 or target < 0 or target > 100:
                messagebox.showerror("Error", "Numbers should be within valid ranges (Target 0-100).", parent=self)
                return
            if attended > total:
                messagebox.showerror("Error", "Attended classes cannot be greater than total classes.", parent=self)
                return
                
            self.callback(name, total, attended, target)
            self.destroy()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values.", parent=self)


class EditHistoryDialog(ctk.CTkToplevel):
    def __init__(self, parent, subject_name, data, save_callback, refresh_callback):
        super().__init__(parent)
        self.title(f"Edit History - {subject_name}")
        self.geometry("550x450")
        self.minsize(450, 350)
        self.subject_name = subject_name
        self.data = data
        self.save_callback = save_callback
        self.refresh_callback = refresh_callback
        
        self.transient(parent)
        self.grab_set()

        self.title_label = ctk.CTkLabel(self, text=f"Attendance Record: {subject_name}", font=ctk.CTkFont(size=18, weight="bold"))
        self.title_label.pack(pady=(15, 10))
        
        # Treeview inside customTkinter
        tree_frame = ctk.CTkFrame(self)
        tree_frame.pack(fill=ctk.BOTH, expand=True, padx=20, pady=(0, 15))
        
        style = ttk.Style()
        style.theme_use("default")
        bg_col = "#2b2b2b" if ctk.get_appearance_mode() == "Dark" else "#f2f2f2"
        fg_col = "white" if ctk.get_appearance_mode() == "Dark" else "black"
        head_bg = "#1f1f1f" if ctk.get_appearance_mode() == "Dark" else "#e5e5e5"
        sel_bg = "#1f538d" if ctk.get_appearance_mode() == "Dark" else "#3a7ebf"

        style.configure("History.Treeview.Heading", font=('Segoe UI', 10, 'bold'), background=head_bg, foreground=fg_col, borderwidth=0)
        style.configure("History.Treeview", font=('Segoe UI', 10), rowheight=25, background=bg_col, fieldbackground=bg_col, foreground=fg_col, borderwidth=0)
        style.map('History.Treeview', background=[('selected', sel_bg)])
        
        columns = ("Date", "Status")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", style="History.Treeview")
        self.tree.heading("Date", text="Date & Time")
        self.tree.heading("Status", text="Status")
        
        self.tree.column("Date", width=300, anchor=ctk.CENTER)
        self.tree.column("Status", width=150, anchor=ctk.CENTER)
        
        self.scrollbar = ctk.CTkScrollbar(tree_frame, command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        
        self.tree.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)
        self.scrollbar.pack(side=ctk.RIGHT, fill=ctk.Y)
        
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill=ctk.X, padx=20, pady=(0, 15))
        
        self.toggle_btn = ctk.CTkButton(btn_frame, text="🔁 Toggle Status", command=self.toggle_status, width=150)
        self.toggle_btn.pack(side=ctk.LEFT, padx=(0, 5))
        
        self.delete_btn = ctk.CTkButton(btn_frame, text="🗑️ Delete Log", command=self.delete_record, fg_color="#ef4444", hover_color="#dc2626", width=120)
        self.delete_btn.pack(side=ctk.LEFT, padx=5)
        
        self.close_btn = ctk.CTkButton(btn_frame, text="Close", command=self.destroy, fg_color="transparent", border_width=1, text_color=("gray10", "gray90"), width=100)
        self.close_btn.pack(side=ctk.RIGHT)
        
        self.populate()
        
    def populate(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        history = self.data[self.subject_name].get("history", [])
        for i, record in enumerate(history):
            self.tree.insert("", ctk.END, iid=str(i), values=(record["date"], record["status"]))
            
    def toggle_status(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a record to edit.", parent=self)
            return
            
        idx = int(selected[0])
        subject = self.data[self.subject_name]
        record = subject["history"][idx]
        
        if record["status"] == "Present":
            record["status"] = "Absent"
            subject["attended"] -= 1
        elif record["status"] == "Absent":
            record["status"] = "Present"
            subject["attended"] += 1
            
        self.save_callback()
        self.refresh_callback()
        self.populate()

    def delete_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a record to delete.", parent=self)
            return
            
        if messagebox.askyesno("Confirm", "Delete this record? This modifies the total and attended counts.", parent=self):
            idx = int(selected[0])
            subject = self.data[self.subject_name]
            record = subject["history"].pop(idx)
            
            subject["total"] -= 1
            if record["status"] == "Present":
                subject["attended"] -= 1
                
            self.save_callback()
            self.refresh_callback()
            self.populate()


class AttendanceTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Attendance Tracker Pro")
        self.root.geometry("1000x750")
        self.root.minsize(600, 500)  # Allow it to squish a bit more reasonably
        
        self.data = self.load_data()
        self.setup_ui()
        self.refresh_cards()
        
    def load_data(self):
        if os.path.exists(DATA_FILE):
             try:
                 with open(DATA_FILE, 'r') as f:
                     data = json.load(f)
                     for k, v in data.items():
                         if "target" not in v:
                             v["target"] = 75.0
                     return data
             except json.JSONDecodeError:
                 return {}
        return {}

    def save_data(self):
        with open(DATA_FILE, 'w') as f:
            json.dump(self.data, f, indent=4)

    def setup_ui(self):
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        # HEADER
        header_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=30, pady=(30, 10))
        # Important: column configuration to make the title squish and buttons stay flush right.
        header_frame.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(header_frame, text="🎓 Tracker Pro", font=ctk.CTkFont(size=28, weight="bold"))
        title_label.grid(row=0, column=0, sticky="w")

        controls_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        controls_frame.grid(row=0, column=1, sticky="e")

        self.btn_add = ctk.CTkButton(controls_frame, text="➕ Add Subject", command=self.add_subject, width=130, height=35)
        self.btn_add.pack(side=ctk.LEFT, padx=(0, 15))

        self.theme_switch = ctk.CTkSwitch(controls_frame, text="Dark Mode", font=ctk.CTkFont(weight="bold"), command=self.toggle_theme)
        self.theme_switch.pack(side=ctk.LEFT)
        self.theme_switch.select()
        ctk.set_appearance_mode("Dark")

        # SCROLLABLE CONTENT AREA (CARDS)
        self.scrollable_frame = ctk.CTkScrollableFrame(self.root, corner_radius=15, fg_color="transparent")
        self.scrollable_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(10, 20))
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

    def toggle_theme(self):
        if self.theme_switch.get() == 1:
            ctk.set_appearance_mode("Dark")
        else:
            ctk.set_appearance_mode("Light")
        self.refresh_cards() 

    def refresh_cards(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if not self.data:
            empty_lbl = ctk.CTkLabel(self.scrollable_frame, text="No subjects created yet.\nClick 'Add Subject' to begin tracking!", font=ctk.CTkFont(size=18), text_color="gray")
            empty_lbl.pack(pady=100)
            return

        for idx, (subject_name, details) in enumerate(self.data.items()):
            self.create_subject_card(idx, subject_name, details)

    def create_subject_card(self, row_idx, subject_name, details):
        total = details["total"]
        attended = details["attended"]
        target = details.get("target", 75.0)
        
        percentage = (attended / total * 100) if total > 0 else 0.0

        safe_color = "#10b981" # Green
        short_color = "#f43f5e" # Soft Red/Pink instead of harsh red
        
        # Subtle floating card background
        card_bg = ("#ffffff", "#212121")

        if total == 0:
            status_text = "No Classes Yet"
            primary_color = "#94a3b8" # Slate gray
            main_action_text = "Waiting for classes to start..."
        elif percentage >= target:
            status_text = "SAFE"
            primary_color = safe_color
            if target > 0:
                 can_miss = math.floor((attended - (target/100.0) * total) / (target/100.0))
                 main_action_text = f"You can safely miss {can_miss} class(es)" if can_miss > 0 else "You are exactly on track."
            else:
                 main_action_text = "Safe (Target is 0%)"
        else:
            status_text = "SHORT"
            primary_color = short_color
            if target < 100:
                 must_attend = math.ceil(((target/100.0) * total - attended) / (1.0 - (target/100.0)))
                 main_action_text = f"Must attend {must_attend} class(es) to reach target"
            else:
                 main_action_text = "Impossible to reach 100%"

        # Main Card Frame - more rounded, subtle borders
        card = ctk.CTkFrame(self.scrollable_frame, corner_radius=20, fg_color=card_bg, border_width=1, border_color=("#e2e8f0", "#333333"))
        card.grid(row=row_idx, column=0, sticky="ew", padx=15, pady=12)
        
        # We'll use a 3-column grid for the card that gracefully handles squishing.
        card.grid_columnconfigure(0, weight=1, minsize=180) # Left side (Titles)
        card.grid_columnconfigure(1, weight=3, minsize=200) # Center side (Progress Bar)
        card.grid_columnconfigure(2, weight=1, minsize=150) # Right side (Buttons)

        # Card Left: Info Text
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.grid(row=0, column=0, padx=25, pady=25, sticky="we")
        
        title_lbl = ctk.CTkLabel(info_frame, text=subject_name, font=ctk.CTkFont(size=22, weight="bold"), justify="left")
        title_lbl.pack(anchor="w", pady=(0, 2), fill=ctk.X, expand=True)
        
        # Dynamically wrap subject title based on the width of info_frame
        def resize_title(event, lbl=title_lbl):
            lbl.configure(wraplength=event.width - 10)
        info_frame.bind("<Configure>", resize_title)
        
        stats_lbl = ctk.CTkLabel(info_frame, text=f"Attended: {attended}/{total}  •  Target: {target}%", font=ctk.CTkFont(size=14, weight="bold"), text_color="gray")
        stats_lbl.pack(anchor="w")

        # Card Center: Progress Area
        prog_frame = ctk.CTkFrame(card, fg_color="transparent")
        prog_frame.grid(row=0, column=1, padx=20, pady=25, sticky="nsew")

        bar_val = percentage / 100.0
        bar_color = primary_color if percentage > 0 else "gray"

        # Explicitly prioritizing the "Must attend X lectures" message!
        action_lbl = ctk.CTkLabel(prog_frame, text=main_action_text, font=ctk.CTkFont(size=16, weight="bold"), text_color=bar_color, justify="center")
        action_lbl.pack(anchor="center", fill=ctk.X, expand=True)
        
        # Dynamically wrap action text based on the width of prog_frame
        def resize_action(event, lbl=action_lbl):
            lbl.configure(wraplength=event.width - 20)
        prog_frame.bind("<Configure>", resize_action)

        prog_bar = ctk.CTkProgressBar(prog_frame, height=14, progress_color=bar_color)
        prog_bar.pack(fill=ctk.X, pady=(8, 8))
        prog_bar.set(bar_val)

        percent_lbl = ctk.CTkLabel(prog_frame, text=f"Current Status: {percentage:.1f}% ({status_text})", font=ctk.CTkFont(size=13), text_color="gray")
        percent_lbl.pack(anchor="center")

        # Card Right: Action Buttons - Softer, more modern pills
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.grid(row=0, column=2, padx=20, pady=25, sticky="e")
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        # Using modern pill-shaped buttons with softer shadow colors
        present_btn = ctk.CTkButton(btn_frame, text="✅ Present", height=40, corner_radius=20, fg_color="#10b981", hover_color="#059669", text_color="white", font=ctk.CTkFont(size=14, weight="bold"), command=lambda s=subject_name: self.mark_attendance(s, "Present"))
        present_btn.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="ew")
        
        absent_btn = ctk.CTkButton(btn_frame, text="❌ Absent", height=40, corner_radius=20, fg_color="#f43f5e", hover_color="#e11d48", text_color="white", font=ctk.CTkFont(size=14, weight="bold"), command=lambda s=subject_name: self.mark_attendance(s, "Absent"))
        absent_btn.grid(row=0, column=1, pady=5, sticky="ew")

        manage_btn = ctk.CTkButton(btn_frame, text="⚙️ Manage Subject", height=36, corner_radius=18, fg_color=("gray90", "gray20"), hover_color=("gray85", "gray25"), text_color=("gray10", "gray90"), border_width=0, command=lambda s=subject_name: self.open_manage_window(s))
        manage_btn.grid(row=1, column=0, columnspan=2, pady=(12, 0), sticky="ew")

    def mark_attendance(self, subject_name, status):
        subject = self.data[subject_name]
        subject["total"] += 1
        if status == "Present":
            subject["attended"] += 1
            
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        subject.setdefault("history", []).append({"date": timestamp, "status": status})
        
        self.save_data()
        self.refresh_cards()

    def open_manage_window(self, subject_name):
        manage_win = ctk.CTkToplevel(self.root)
        manage_win.title(f"Manage: {subject_name}")
        manage_win.geometry("320x280")
        manage_win.minsize(320, 280)
        manage_win.transient(self.root)
        manage_win.grab_set()

        ctk.CTkLabel(manage_win, text=f"⚙️ {subject_name}", font=ctk.CTkFont(size=20, weight="bold"), wraplength=280).pack(pady=(25, 15))

        ctk.CTkButton(manage_win, text="✏️ Edit History", height=35, command=lambda: [manage_win.destroy(), self.edit_history(subject_name)]).pack(fill=ctk.X, padx=40, pady=6)
        ctk.CTkButton(manage_win, text="🎯 Set Target %", height=35, command=lambda: [manage_win.destroy(), self.change_target(subject_name)]).pack(fill=ctk.X, padx=40, pady=6)
        
        ctk.CTkButton(manage_win, text="🗑️ Delete Subject", height=35, fg_color="transparent", border_width=1, border_color="#ef4444", text_color="#ef4444", hover_color="rgba(239, 68, 68, 0.1)", command=lambda: [manage_win.destroy(), self.delete_subject(subject_name)]).pack(fill=ctk.X, padx=40, pady=(20, 5))

    def add_subject(self):
        def save_new_subject(name, total, attended, target):
            if name in self.data:
                messagebox.showerror("Error", f"Subject '{name}' already exists.")
                return
            self.data[name] = {
                "name": name,
                "total": total,
                "attended": attended,
                "target": target,
                "history": []
            }
            self.save_data()
            self.refresh_cards()
        AddSubjectDialog(self.root, save_new_subject)

    def edit_history(self, subject_name):
        EditHistoryDialog(self.root, subject_name, self.data, self.save_data, self.refresh_cards)

    def change_target(self, subject_name):
        dialog = ctk.CTkInputDialog(text=f"Enter target percentage for '{subject_name}' (0-100):", title="Change Target")
        val = dialog.get_input()
        
        if val is not None:
            try:
                new_target = float(val)
                if 0 <= new_target <= 100:
                    self.data[subject_name]["target"] = new_target
                    self.save_data()
                    self.refresh_cards()
                else:
                    messagebox.showerror("Error", "Target must be between 0 and 100.")
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number.")
            
    def delete_subject(self, subject_name):
        if messagebox.askyesno("Confirm Deletion", f"Permanently delete tracker data for '{subject_name}'?"):
            del self.data[subject_name]
            self.save_data()
            self.refresh_cards()

if __name__ == "__main__":
    app = ctk.CTk()
    app_controller = AttendanceTrackerApp(app)
    app.mainloop()