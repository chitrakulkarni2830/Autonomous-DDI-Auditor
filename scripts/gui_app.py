import tkinter as tk
import customtkinter as ctk
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os

# Set appearance and theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class DDIAuditorGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("🏥 Autonomous DDI Auditor - Desktop Dashboard")
        self.geometry("1100x700")

        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Path Setup
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.db_path = os.path.join(BASE_DIR, "outputs", "audit_results.db")

        # Initialize UI Components
        self.setup_sidebar()
        self.setup_main_frame()
        
        # Load Initial Data
        self.refresh_data()

    def setup_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="DDI AUDITOR", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.pack(pady=20, padx=20)

        self.summary_btn = ctk.CTkButton(self.sidebar_frame, text="Executive Summary", command=lambda: self.show_page("summary"))
        self.summary_btn.pack(pady=10, padx=20)

        self.logs_btn = ctk.CTkButton(self.sidebar_frame, text="Audit Logs", command=lambda: self.show_page("logs"))
        self.logs_btn.pack(pady=10, padx=20)

        self.refresh_btn = ctk.CTkButton(self.sidebar_frame, text="🔄 Refresh Data", fg_color="transparent", border_width=1, command=self.refresh_data)
        self.refresh_btn.pack(side="bottom", pady=20, padx=20)

    def setup_main_frame(self):
        self.main_container = ctk.CTkFrame(self, corner_radius=10)
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(1, weight=1)

        # Header
        self.header_label = ctk.CTkLabel(self.main_container, text="Executive Summary", font=ctk.CTkFont(size=24, weight="bold"))
        self.header_label.grid(row=0, column=0, sticky="w", padx=20, pady=20)

        # Content Frame
        self.content_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=0)
        
        self.pages = {}
        self.setup_summary_page()
        self.setup_logs_page()
        
        self.show_page("summary")

    def setup_summary_page(self):
        page = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.pages["summary"] = page
        
        # Metrics Row
        self.metrics_frame = ctk.CTkFrame(page, fg_color="transparent")
        self.metrics_frame.pack(fill="x", pady=10)
        
        self.metric_labels = {}
        metrics = ["Total Patients", "Pairs Checked", "High-Risk Alerts", "Patients at Risk"]
        for i, m in enumerate(metrics):
            f = ctk.CTkFrame(self.metrics_frame, width=200, height=100)
            f.pack(side="left", expand=True, padx=10)
            f.pack_propagate(False)
            
            ctk.CTkLabel(f, text=m, font=ctk.CTkFont(size=12)).pack(pady=(15,0))
            lbl = ctk.CTkLabel(f, text="--", font=ctk.CTkFont(size=24, weight="bold"))
            lbl.pack()
            self.metric_labels[m] = lbl

        # Charts Row
        self.charts_frame = ctk.CTkFrame(page, fg_color="transparent")
        self.charts_frame.pack(fill="both", expand=True, pady=20)
        
    def setup_logs_page(self):
        page = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.pages["logs"] = page
        
        # Simple Listbox for logs (in a real app, use a proper ScrollableFrame or Table)
        self.log_scrollable = ctk.CTkScrollableFrame(page, label_text="Safety Audit Log")
        self.log_scrollable.pack(fill="both", expand=True, padx=10, pady=10)

    def show_page(self, page_name):
        for p in self.pages.values():
            p.pack_forget()
        self.pages[page_name].pack(fill="both", expand=True)
        self.header_label.configure(text="Executive Summary" if page_name=="summary" else "Detailed Safety Logs")

    def refresh_data(self):
        if not os.path.exists(self.db_path):
            self.header_label.configure(text="Waiting for Database...")
            return

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall() if row[0] != "sqlite_sequence"]
            
            df_list = []
            for table in tables:
                df_temp = pd.read_sql_query(f"SELECT * FROM {table}", conn)
                df_temp['Department'] = table
                df_list.append(df_temp)
            
            if not df_list:
                return
                
            df = pd.concat(df_list, ignore_index=True)
            conn.close()

            # Update Metrics
            total_patients = df['patient_name'].nunique()
            total_checks = len(df)
            df['Is_High_Risk'] = df['literature_risk'].str.contains('KNOWN RISK', na=False) | \
                                df['biochem_risk'].str.contains('HIGH STRUCTURAL SIMILARITY', na=False)
            high_risk_count = df['Is_High_Risk'].sum()
            patients_at_risk = df[df['Is_High_Risk']]['patient_name'].nunique()

            self.metric_labels["Total Patients"].configure(text=str(total_patients))
            self.metric_labels["Pairs Checked"].configure(text=str(total_checks))
            self.metric_labels["High-Risk Alerts"].configure(text=str(high_risk_count))
            self.metric_labels["Patients at Risk"].configure(text=str(patients_at_risk))

            # Update Logs
            for child in self.log_scrollable.winfo_children():
                child.destroy()
            
            for _, row in df.head(100).iterrows():
                color = "#ff4d4d" if row['Is_High_Risk'] else "#4CAF50"
                txt = f"{row['patient_name']} | {row['drug_1']} + {row['drug_2']} | {row['literature_risk']} | {row['biochem_risk']}"
                lbl = ctk.CTkLabel(self.log_scrollable, text=txt, text_color=color, anchor="w", justify="left")
                lbl.pack(fill="x", padx=10, pady=2)

            self.update_charts(df)

        except Exception as e:
            print(f"Error refreshing data: {e}")

    def update_charts(self, df):
        # Clear existing charts
        for widget in self.charts_frame.winfo_children():
            widget.destroy()

        if df.empty:
            return

        # 1. Department Risk Chart
        fig1, ax1 = plt.subplots(figsize=(5, 4), dpi=100)
        plt.style.use('dark_background')
        
        df_risk = df[df['Is_High_Risk']]
        if not df_risk.empty:
            risk_counts = df_risk.groupby("Department").size()
            risk_counts.plot(kind='bar', color='#1f538d', ax=ax1)
            ax1.set_title("High-Risk Alerts by Department", fontsize=10, pad=10)
            ax1.tick_params(axis='x', rotation=45, labelsize=8)
            ax1.spines['top'].set_visible(False)
            ax1.spines['right'].set_visible(False)
            plt.tight_layout()
            
            canvas1 = FigureCanvasTkAgg(fig1, master=self.charts_frame)
            canvas1.draw()
            canvas1.get_tk_widget().pack(side="left", fill="both", expand=True, padx=10)

        # 2. Top Interacting Drugs Chart (Pie)
        if not df_risk.empty:
            fig2, ax2 = plt.subplots(figsize=(5, 4), dpi=100)
            plt.style.use('dark_background')
            
            drugs = pd.concat([df_risk['drug_1'], df_risk['drug_2']])
            top_drugs = drugs.value_counts().head(5)
            
            colors = ['#1f538d', '#2874a6', '#2e86c1', '#3498db', '#5dade2']
            ax2.pie(top_drugs, labels=top_drugs.index, autopct='%1.1f%%', colors=colors, textprops={'fontsize': 8})
            ax2.set_title("Top 5 Drugs Involved in Risks", fontsize=10, pad=10)
            plt.tight_layout()

            canvas2 = FigureCanvasTkAgg(fig2, master=self.charts_frame)
            canvas2.draw()
            canvas2.get_tk_widget().pack(side="left", fill="both", expand=True, padx=10)
        else:
            lbl = ctk.CTkLabel(self.charts_frame, text="No risk data available for charts.", font=ctk.CTkFont(slant="italic"))
            lbl.pack(pady=50)

if __name__ == "__main__":
    app = DDIAuditorGUI()
    app.mainloop()
