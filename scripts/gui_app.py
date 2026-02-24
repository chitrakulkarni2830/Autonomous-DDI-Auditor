import tkinter as tk
import customtkinter as ctk
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import threading

# Set appearance and theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class DDIAuditorGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("🏥 Autonomous DDI Auditor - Premium Dashboard")
        self.geometry("1200x850")

        # Configuration & State
        self.df = pd.DataFrame()
        self.filtered_df = pd.DataFrame()
        
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.db_path = os.path.join(BASE_DIR, "outputs", "audit_results.db")

        # Layout Configuration
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Setup Components
        self.setup_sidebar()
        self.setup_main_area()
        
        # Initial Load
        self.load_full_data()

    def setup_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        # Brand
        self.logo = ctk.CTkLabel(self.sidebar, text="🏥 DDI AUDITOR", font=ctk.CTkFont(size=22, weight="bold"))
        self.logo.pack(pady=30, padx=20)

        # Filters Label
        ctk.CTkLabel(self.sidebar, text="FILTERS", font=ctk.CTkFont(size=12, weight="bold"), text_color="gray").pack(anchor="w", padx=30, pady=(10, 5))

        # Department Filter
        ctk.CTkLabel(self.sidebar, text="Department", font=ctk.CTkFont(size=11)).pack(anchor="w", padx=30)
        self.dept_selector = ctk.CTkOptionMenu(self.sidebar, values=["All Departments"], command=self.apply_filters)
        self.dept_selector.pack(pady=(0, 15), padx=20, fill="x")

        # Patient Selection
        ctk.CTkLabel(self.sidebar, text="Select Patient", font=ctk.CTkFont(size=11)).pack(anchor="w", padx=30)
        self.patient_selector = ctk.CTkOptionMenu(self.sidebar, values=["All Patients"], command=self.apply_filters)
        self.patient_selector.pack(pady=(0, 15), padx=20, fill="x")

        # Drug Filter
        ctk.CTkLabel(self.sidebar, text="Filter by Drug", font=ctk.CTkFont(size=11)).pack(anchor="w", padx=30)
        self.drug_search = ctk.CTkEntry(self.sidebar, placeholder_text="e.g. Insulin")
        self.drug_search.pack(pady=(0, 15), padx=20, fill="x")
        self.drug_search.bind("<KeyRelease>", lambda e: self.apply_filters())

        # Risk Filter
        self.risk_only_var = tk.BooleanVar(value=False)
        self.risk_checkbox = ctk.CTkCheckBox(self.sidebar, text="Show High Risk Only", variable=self.risk_only_var, command=self.apply_filters)
        self.risk_checkbox.pack(pady=20, padx=30, anchor="w")

        # Footer Actions
        self.refresh_btn = ctk.CTkButton(self.sidebar, text="🔄 Reload Database", fg_color="transparent", border_width=1, command=self.load_full_data)
        self.refresh_btn.pack(side="bottom", pady=20, padx=20, fill="x")

    def setup_main_area(self):
        self.scrollable_container = ctk.CTkScrollableFrame(self, corner_radius=0, fg_color="transparent")
        self.scrollable_container.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        
        # --- HEADER SECTION ---
        self.header = ctk.CTkFrame(self.scrollable_container, fg_color="transparent")
        self.header.pack(fill="x", padx=30, pady=(30, 10))
        
        self.title_lbl = ctk.CTkLabel(self.header, text="Safety Dashboard", font=ctk.CTkFont(size=28, weight="bold"))
        self.title_lbl.pack(side="left")

        # --- METRICS SECTION ---
        self.metrics_row = ctk.CTkFrame(self.scrollable_container, fg_color="transparent")
        self.metrics_row.pack(fill="x", padx=20, pady=20)
        
        self.metric_widgets = {}
        for m in ["Patients", "Audits", "Risk Alerts", "At Risk %"]:
            card = ctk.CTkFrame(self.metrics_row, height=120, corner_radius=15, border_width=1, border_color="#333")
            card.pack(side="left", expand=True, padx=10, fill="both")
            card.pack_propagate(False)
            
            ctk.CTkLabel(card, text=m.upper(), font=ctk.CTkFont(size=11, weight="bold"), text_color="gray").pack(pady=(20, 5))
            val = ctk.CTkLabel(card, text="--", font=ctk.CTkFont(size=32, weight="bold"))
            val.pack()
            self.metric_widgets[m] = val

        # --- CHARTS SECTION (DEPARTMENT) ---
        self.dept_chart_row = ctk.CTkFrame(self.scrollable_container, fg_color="transparent")
        self.dept_chart_row.pack(fill="x", padx=20, pady=(10, 5))
        
        self.dept_chart_frame = ctk.CTkFrame(self.dept_chart_row, height=350, corner_radius=15)
        self.dept_chart_frame.pack(fill="both", expand=True, padx=10)
        
        # --- DEDICATED TOP CONTRIBUTORS SECTION ---
        ctk.CTkLabel(self.scrollable_container, text="TOP DRUG CONTRIBUTORS", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=30, pady=(20, 0))
        
        self.drug_chart_row = ctk.CTkFrame(self.scrollable_container, fg_color="transparent")
        self.drug_chart_row.pack(fill="x", padx=20, pady=(5, 10))

        self.drug_chart_frame = ctk.CTkFrame(self.drug_chart_row, height=350, corner_radius=15)
        self.drug_chart_frame.pack(fill="both", expand=True, padx=10)

        # --- LOGS SECTION ---
        ctk.CTkLabel(self.scrollable_container, text="DETAILED AUDIT LOGS", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=30, pady=(30, 10))
        
        self.logs_table_frame = ctk.CTkFrame(self.scrollable_container, corner_radius=15)
        self.logs_table_frame.pack(fill="x", padx=30, pady=(0, 50))
        
        # Table Header
        header_f = ctk.CTkFrame(self.logs_table_frame, fg_color="#222", height=40)
        header_f.pack(fill="x", padx=5, pady=5)
        cols = [("Patient", 200), ("Interaction", 250), ("Lit. Risk", 300), ("Biochem", 200)]
        for text, width in cols:
            lbl = ctk.CTkLabel(header_f, text=text, font=ctk.CTkFont(weight="bold"), width=width, anchor="w")
            lbl.pack(side="left", padx=10)

        self.rows_container = ctk.CTkFrame(self.logs_table_frame, fg_color="transparent")
        self.rows_container.pack(fill="x")

    def load_full_data(self):
        if not os.path.exists(self.db_path):
            self.title_lbl.configure(text="Database Not Found - Please Run main.py")
            return

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall() if row[0] != "sqlite_sequence"]
            
            df_list = []
            for table in tables:
                df_temp = pd.read_sql_query(f"SELECT * FROM {table}", conn)
                df_temp['Department'] = table.replace("_", " ")
                df_list.append(df_temp)
            
            conn.close()
            
            if df_list:
                self.df = pd.concat(df_list, ignore_index=True)
                self.df['Is_High_Risk'] = self.df['literature_risk'].str.contains('KNOWN RISK', na=False) | \
                                         self.df['biochem_risk'].str.contains('HIGH STRUCTURAL SIMILARITY', na=False)
                
                # Update Selectors
                depts = ["All Departments"] + sorted(self.df['Department'].unique().tolist())
                self.dept_selector.configure(values=depts)

                patients = ["All Patients"] + sorted(self.df['patient_name'].unique().tolist())
                self.patient_selector.configure(values=patients)
                
                self.apply_filters()
        except Exception as e:
            print(f"Error loading data: {e}")

    def apply_filters(self, *args):
        if self.df.empty: return
        
        filtered = self.df.copy()
        
        # Dept Filter
        dept = self.dept_selector.get()
        if dept != "All Departments":
            filtered = filtered[filtered['Department'] == dept]
            
        # Patient Filter
        patient = self.patient_selector.get()
        if patient != "All Patients":
            filtered = filtered[filtered['patient_name'] == patient]
            
        # Drug Filter
        d_search = self.drug_search.get().lower()
        if d_search:
            filtered = filtered[
                (filtered['drug_1'].str.lower().contains(d_search, na=False)) | 
                (filtered['drug_2'].str.lower().contains(d_search, na=False))
            ]
            
        # Risk Filter
        if self.risk_only_var.get():
            filtered = filtered[filtered['Is_High_Risk'] == True]
            
        self.filtered_df = filtered
        self.update_ui()

    def update_ui(self):
        # Update Metrics
        total_p = self.filtered_df['patient_name'].nunique()
        total_a = len(self.filtered_df)
        risks = self.filtered_df['Is_High_Risk'].sum()
        risk_pct = (risks / total_a * 100) if total_a > 0 else 0
        
        self.metric_widgets["Patients"].configure(text=str(total_p))
        self.metric_widgets["Audits"].configure(text=str(total_a))
        self.metric_widgets["Risk Alerts"].configure(text=str(risks), text_color="#ff4d4d" if risks > 0 else "white")
        self.metric_widgets["At Risk %"].configure(text=f"{risk_pct:.1f}%")

        # Update Charts (Non-blocking)
        self.render_charts()
        
        # Update Table Rows
        self.render_table()

    def render_table(self):
        for child in self.rows_container.winfo_children():
            child.destroy()
            
        # Remove hard display limit so all filtered patients are visible
        display_df = self.filtered_df
        
        for i, row in display_df.iterrows():
            f = ctk.CTkFrame(self.rows_container, fg_color="transparent" if i%2 == 0 else "#1a1a1a")
            f.pack(fill="x", padx=5, pady=1)
            
            risk_color = "#ff4d4d" if row['Is_High_Risk'] else "gray"
            
            ctk.CTkLabel(f, text=row['patient_name'], width=200, anchor="w", font=ctk.CTkFont(size=12)).pack(side="left", padx=10)
            ctk.CTkLabel(f, text=f"{row['drug_1']} + {row['drug_2']}", width=250, anchor="w", text_color="#3b8ed0").pack(side="left", padx=10)
            
            lit_text = row['literature_risk'].split('-')[0] if '-' in row['literature_risk'] else row['literature_risk']
            ctk.CTkLabel(f, text=lit_text, width=300, anchor="w", text_color=risk_color).pack(side="left", padx=10)
            
            chem_text = row['biochem_risk'].split('(')[0] if '(' in row['biochem_risk'] else row['biochem_risk']
            ctk.CTkLabel(f, text=chem_text, width=200, anchor="w", text_color=risk_color).pack(side="left", padx=10)



    def render_charts(self):
        # Dept Chart
        for w in self.dept_chart_frame.winfo_children(): w.destroy()
        # Increased width to match new full-width layout
        fig1, ax1 = plt.subplots(figsize=(10, 3.5), dpi=100)
        plt.style.use('dark_background')
        
        risk_df = self.filtered_df[self.filtered_df['Is_High_Risk']]
        if not risk_df.empty:
            risk_df.groupby("Department").size().sort_values(ascending=True).plot(kind="barh", color="#1f538d", ax=ax1)
            
            # Make the department names smaller so they fit
            ax1.tick_params(axis='y', labelsize=6)
            ax1.set_title("High Risks by Department", fontsize=12, pad=10)
            ax1.set_xlabel("Count", fontsize=10)
            ax1.set_ylabel("")
            
            # Use tight layout with a pad to ensure labels aren't cut off
            plt.tight_layout(pad=1.5)
            # Force extra left margin in case tight_layout fails to account for very long names
            fig1.subplots_adjust(left=0.25)
            
            canvas1 = FigureCanvasTkAgg(fig1, master=self.dept_chart_frame)
            canvas1.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
            canvas1.draw()
        else:
            ctk.CTkLabel(self.dept_chart_frame, text="No Risk Data for Charts").pack(pady=100)

        # Drug Chart (Dedicated Section)
        for w in self.drug_chart_frame.winfo_children(): w.destroy()
        # Full width figure, slightly taller to accommodate labels comfortably
        fig2, ax2 = plt.subplots(figsize=(10, 4), dpi=100)
        if not risk_df.empty:
            drugs = pd.concat([risk_df['drug_1'], risk_df['drug_2']]).value_counts().head(5)
            # Use horizontal bar chart instead of pie for better visibility
            drugs.sort_values(ascending=True).plot(kind="barh", color="#e74c3c", ax=ax2)
            
            # Make the drug names smaller so they fit
            ax2.tick_params(axis='y', labelsize=6)
            ax2.set_xlabel("Involvement Count", fontsize=10)
            ax2.set_ylabel("")
            # Title is now handled by the UI label, so removing it from the plot to save space
            ax2.set_title("")
            
            # Add value labels to the bars
            for container in ax2.containers:
                ax2.bar_label(container, padding=5, color='white', fontsize=9, weight='bold')

            # Use tight layout with a pad to ensure labels aren't cut off
            plt.tight_layout(pad=1.5)
            # Force extra left margin in case tight_layout fails to account for very long names
            fig2.subplots_adjust(left=0.25)
            canvas2 = FigureCanvasTkAgg(fig2, master=self.drug_chart_frame)
            canvas2.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
            canvas2.draw()
        else:
            ctk.CTkLabel(self.drug_chart_frame, text="All Clear! No High Risk Drugs Found.").pack(pady=100)

if __name__ == "__main__":
    app = DDIAuditorGUI()
    app.mainloop()
