# 🎓 Attendance Tracker Pro

[🚀 Download Latest Version for Windows](https://github.com/i-am-ks901/attendance-tracker-pro/releases/latest)

A modern, high-performance desktop application built with Python and CustomTkinter. This tool helps students manage university attendance, track history, and calculate exactly how many classes they need to attend to meet their target percentage.

## 🚀 Key Features
* **Smart Attendance Logic**: Real-time calculation of "Safe" or "Short" status.
* **Predictive Analysis**: Tells you exactly how many lectures you can safely miss or must attend to reach your goal (e.g., 75%).
* **Modern UI/UX**: Built with a sleek, responsive dark-mode interface using `CustomTkinter`.
* **Persistent History**: Automatically logs every attendance mark with a timestamp in a local JSON database.
* **History Management**: Ability to toggle attendance status or delete specific logs.

## 🛠️ Tech Stack
* **Language**: Python 3.11
* **GUI**: CustomTkinter / Tkinter (ttk)
* **Data**: JSON (Local Persistence)
* **Logic**: Math-based prediction algorithms

## 📦 Installation & Usage
1. **Clone the repository:**
   ```bash
   git clone https://github.com/i-am-ks901/attendance-tracker-pro.git
   ```
   
2. **Install dependencies:**
   ```bash
   pip install customtkinter
   ```

3. **Run the application:**
   ```bash
   python AttendanceTracker.py
   ```

## 📸 Preview
<img width="1089" height="806" alt="image" src="https://github.com/user-attachments/assets/fd77bf0f-58df-465a-803a-3992f79a7ae1" />



## 🗺️ v2.0 Roadmap (Coming Soon)
I am currently working on the next major update to transition this from a simple tracker to a full analytics suite.

[x] Global Dashboard: Added a pinned summary card showing total attendance and safe/short counts.

[x] Performance Optimization: Implemented an update-based rendering engine to handle multiple subjects without lag.

[X] Visual Analytics: Integrated bar charts using matplotlib to compare attendance vs. targets across all subjects.

[X] Data Portability: CSV export functionality for external backup and reporting.

[X] Search & Sort: Real-time filtering and sorting (by name or attendance level) for students with many subjects.

[ ] Critical Alerts: Visual pulsing warnings for subjects that fall significantly below the target threshold.

[ ] Enhanced Logging: Ability to add custom notes (e.g., "Medical Leave") to individual attendance records.


## Note for Windows Users: 
Since this application is not digitally signed, Windows might show a "SmartScreen" warning. To run the app, click "More info" and then "Run anyway".
