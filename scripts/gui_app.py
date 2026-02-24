import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os

# Set appearance and theme to match Streamlit light mode
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class DDIAuditorGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("🏥 Autonomous DDI Auditor - Safety Dashboard")
        self.geometry("1400x900")

        # Configuration & State
        self.df = pd.DataFrame()
        self.filtered_df = pd.DataFrame()
        
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.db_path = os.path.join(BASE_DIR, "outputs", "audit_results.db")

        # Layout Configuration - Single Scrollable Main Area
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Setup Scrollable Main Area
        self.main_container = ctk.CTkScrollableFrame(self, fg_color="white", corner_radius=0)
        self.main_container.grid(row=0, column=0, sticky="nsew")

        # UI Construction
        self.setup_header()
        self.setup_metrics()
        self.setup_charts_area()
        self.setup_table_area()

        # Build style for Treeview
        self.setup_treeview_style()

        # Initial Load
        self.load_full_data()

    def setup_treeview_style(self):
        style = ttk.Style()
        style.theme_use("default")
        
        style.configure("Treeview", 
                        background="#ffffff",
                        foreground="#000000",
                        rowheight=35,
                        fieldbackground="#ffffff",
                        bordercolor="#e0e0e0",
                        borderwidth=1,
                        font=("Helvetica", 11))
                        
        style.map('Treeview', background=[('selected', '#e6f2ff')])
        
        style.configure("Treeview.Heading", 
                        background="#f9f9f9",
                        foreground="#555555",
                        font=("Helvetica", 10, "bold"),
                        bordercolor="#e0e0e0",
                        borderwidth=1)
                        
        # Striped rows setup is handled in render_table

    def setup_header(self):
        # Top Title
        title_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        title_frame.pack(fill="x", padx=40, pady=(40, 20))
        
        ctk.CTkLabel(title_frame, text="🏥 Autonomous DDI Auditor - Safety Dashboard", 
                     font=ctk.CTkFont(family="Helvetica", size=36, weight="bold"), 
                     text_color="#31333f").pack(anchor="w")
                     
        # Horizontal Rule
        ctk.CTkFrame(self.main_container, height=2, fg_color="#e6e6e8").pack(fill="x", padx=40, pady=(0, 20))

    def setup_metrics(self):
        # Section Title
        ctk.CTkLabel(self.main_container, text="📊 Executive Summary", 
                     font=ctk.CTkFont(family="Helvetica", size=24, weight="bold"), 
                     text_color="#31333f").pack(anchor="w", padx=40, pady=(20, 10))
        
        metrics_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        metrics_frame.pack(fill="x", padx=40, pady=(10, 30))
        
        self.metric_widgets = {}
        metrics = ["Total Patients Audited", "Drug Pairs Checked", "High-Risk Interactions", "Patients at Risk"]
        
        for m in metrics:
            card = ctk.CTkFrame(metrics_frame, fg_color="transparent")
            card.pack(side="left", expand=True, fill="x")
            
            # Small label on top
            ctk.CTkLabel(card, text=m, font=ctk.CTkFont(family="Helvetica", size=14), text_color="#555867").pack(anchor="w")
            # Large number on bottom
            val = ctk.CTkLabel(card, text="--", font=ctk.CTkFont(family="Helvetica", size=42, weight="normal"), text_color="#31333f")
            val.pack(anchor="w", pady=(5, 0))
            self.metric_widgets[m] = val

        # Horizontal Rule
        ctk.CTkFrame(self.main_container, height=2, fg_color="#e6e6e8").pack(fill="x", padx=40, pady=20)

    def setup_charts_area(self):
        # --- CHARTS SECTION (DEPARTMENT) ---
        self.dept_chart_row = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.dept_chart_row.pack(fill="x", padx=40, pady=(10, 5))
        
        ctk.CTkLabel(self.dept_chart_row, text="📈 High-Risk Interactions by Department", 
                     font=ctk.CTkFont(family="Helvetica", size=20, weight="bold"), 
                     text_color="#31333f").pack(anchor="w", pady=(0, 20))
                     
        self.dept_chart_frame = ctk.CTkFrame(self.dept_chart_row, fg_color="white", height=400)
        self.dept_chart_frame.pack(fill="both", expand=True)
        
        # --- DEDICATED TOP CONTRIBUTORS SECTION ---
        self.drug_chart_row = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.drug_chart_row.pack(fill="x", padx=40, pady=(30, 10))

        ctk.CTkLabel(self.drug_chart_row, text="💊 Most Common Interacting Drugs", 
                     font=ctk.CTkFont(family="Helvetica", size=20, weight="bold"), 
                     text_color="#31333f").pack(anchor="w", pady=(0, 20))

        self.drug_chart_frame = ctk.CTkFrame(self.drug_chart_row, fg_color="white", height=400)
        self.drug_chart_frame.pack(fill="both", expand=True)
        
        # Horizontal Rule
        ctk.CTkFrame(self.main_container, height=2, fg_color="#e6e6e8").pack(fill="x", padx=40, pady=40)

    def setup_table_area(self):
        # Section Title
        ctk.CTkLabel(self.main_container, text="📋 Detailed Safety Audit Log", 
                     font=ctk.CTkFont(family="Helvetica", size=24, weight="bold"), 
                     text_color="#31333f").pack(anchor="w", padx=40, pady=(10, 10))
                     
        # Filter Dropdown (Match Streamlit selectbox)
        filter_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        filter_frame.pack(fill="x", padx=40, pady=(10, 20))
        
        ctk.CTkLabel(filter_frame, text="Filter by Department:", font=ctk.CTkFont(family="Helvetica", size=14), text_color="#555867").pack(side="left", padx=(0, 10))
        
        self.dept_selector = ctk.CTkOptionMenu(filter_frame, values=["All"], command=self.apply_filters, fg_color="#f0f2f6", text_color="#31333f", button_color="#f0f2f6", button_hover_color="#e0e2e6", font=ctk.CTkFont(family="Helvetica", size=14))
        self.dept_selector.pack(side="left", fill="x", expand=True)

        self.high_risk_var = tk.BooleanVar(value=False)
        self.high_risk_checkbox = ctk.CTkCheckBox(filter_frame, text="Show High Risk Only", variable=self.high_risk_var, command=self.apply_filters, text_color="#31333f", font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"), fg_color="#ff4d4d", hover_color="#cc0000")
        self.high_risk_checkbox.pack(side="right", padx=(20, 0))

        # Treeview Table Container
        table_container = ctk.CTkFrame(self.main_container, fg_color="transparent")
        table_container.pack(fill="x", padx=40, pady=(0, 50))
        
        # Define Columns
        columns = ('patient_name', 'age', 'Department', 'diagnosis', 'drug_1', 'drug_2', 'literature_risk', 'biochem_risk')
        self.tree = ttk.Treeview(table_container, columns=columns, show='headings', height=15)
        
        # Define Headings and Column widths
        for col in columns:
            self.tree.heading(col, text=col)
            # Adjust column widths based on content type
            if col == 'age':
                self.tree.column(col, width=50, anchor="e")
            elif col in ['patient_name', 'Department', 'drug_1', 'drug_2']:
                self.tree.column(col, width=150, anchor="w")
            elif col == 'diagnosis':
                self.tree.column(col, width=180, anchor="w")
            elif col == 'literature_risk':
                self.tree.column(col, width=350, anchor="w")
            elif col == 'biochem_risk':
                self.tree.column(col, width=250, anchor="w")
        
        # Striped Row Tags
        self.tree.tag_configure('oddrow', background='white')
        self.tree.tag_configure('evenrow', background='#f9f9f9')
        
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(table_container, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

    def load_full_data(self):
        if not os.path.exists(self.db_path):
            self.metric_widgets["Total Patients Audited"].configure(text="Err: DB DB Not Found")
            return

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall() if row[0] != "sqlite_sequence"]
            
            df_list = []
            for table in tables:
                df_temp = pd.read_sql_query(f"SELECT *, '{table.replace('_', ' ')}' as Department FROM {table}", conn)
                df_list.append(df_temp)
            
            conn.close()
            
            if df_list:
                self.df = pd.concat(df_list, ignore_index=True)
                # Calculate high risk Boolean
                self.df['Is_High_Risk'] = self.df['literature_risk'].str.contains('KNOWN RISK', na=False) | \
                                         self.df['biochem_risk'].str.contains('HIGH STRUCTURAL SIMILARITY', na=False)
                
                # Update Filter Dropdown
                depts = ["All"] + sorted(self.df['Department'].unique().tolist())
                self.dept_selector.configure(values=depts)
                
                self.apply_filters()
        except Exception as e:
            print(f"Error loading data: {e}")

    def apply_filters(self, *args):
        if self.df.empty: return
        
        filtered = self.df.copy()
        
        # Dept Filter
        dept = self.dept_selector.get()
        if dept != "All":
            filtered = filtered[filtered['Department'] == dept]
            
        # High Risk Filter
        if self.high_risk_var.get():
            filtered = filtered[filtered['Is_High_Risk'] == True]
            
        self.filtered_df = filtered
        self.update_ui()

    def update_ui(self):
        # 1. Update Executive Summary Metrics
        total_p = self.filtered_df['patient_name'].nunique()
        total_a = len(self.filtered_df)
        risks = self.filtered_df['Is_High_Risk'].sum()
        risk_patients = self.filtered_df[self.filtered_df['Is_High_Risk']]['patient_name'].nunique()
        
        self.metric_widgets["Total Patients Audited"].configure(text=str(total_p))
        self.metric_widgets["Drug Pairs Checked"].configure(text=str(total_a))
        self.metric_widgets["High-Risk Interactions"].configure(text=str(risks))
        self.metric_widgets["Patients at Risk"].configure(text=str(risk_patients))

        # 2. Update Charts
        self.render_charts()
        
        # 3. Update Audit Log Table
        self.render_table()

    def render_table(self):
        # Clear existing rows
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Display rows matching Streamlit format
        columns_to_show = ['patient_name', 'age', 'Department', 'diagnosis', 'drug_1', 'drug_2', 'literature_risk', 'biochem_risk']
        
        for i, row in self.filtered_df.iterrows():
            values = []
            for col in columns_to_show:
                val = str(row[col])
                # Emulate Streamlit's visual flags for identical representation if possible, otherwise use text
                if col == 'literature_risk' and 'KNOWN RISK' in val:
                    val = f"⚠️ {val}"
                elif col == 'literature_risk' and 'No obvious flag' in val:
                    val = f"✅ {val}"
                elif col == 'biochem_risk' and 'HIGH STRUCTURAL SIMILARITY' in val:
                    val = f"⚠️ {val}"
                elif col == 'biochem_risk' and 'Low structural risk' in val:
                    val = f"✅ {val}"
                    
                values.append(val)
                
            tags = ('evenrow',) if i % 2 == 0 else ('oddrow',)
            self.tree.insert('', tk.END, values=values, tags=tags)

    def render_charts(self):
        # Get risk dataframe
        df_risk = self.filtered_df[self.filtered_df['Is_High_Risk']]
        
        # Dept Chart (Vertical Bar) - Match Streamlit style
        for w in self.dept_chart_frame.winfo_children(): w.destroy()
        # Increased width to match new full-width layout
        fig1, ax1 = plt.subplots(figsize=(10, 4), dpi=100)
        # Use a white background
        fig1.patch.set_facecolor('white')
        ax1.set_facecolor('white')
        
        if not df_risk.empty:
            dept_counts = df_risk.groupby("Department").size()
            # Plotly styling: vertical bars, multi-colored
            colors = ['#1f77b4', '#99ccff', '#ff3333', '#ff9999', '#2ca02c', '#98df8a', '#d62728']
            colors = colors * (len(dept_counts) // len(colors) + 1) # Repeat if necessary
            
            bars = ax1.bar(dept_counts.index, dept_counts.values, color=colors[:len(dept_counts)])
            
            # Matplotlib styling to match Plotly clean look
            ax1.set_title("Count of Critical Drug-Drug Interactions", loc='left', fontsize=12, pad=15, weight='bold')
            ax1.set_ylabel("Count", fontsize=10, color="#555555")
            ax1.set_xlabel("Department", fontsize=10, color="#555555")
            
            # Hide top and right spines, make bottom/left light grey
            ax1.spines['top'].set_visible(False)
            ax1.spines['right'].set_visible(False)
            ax1.spines['bottom'].set_color('#e0e0e0')
            ax1.spines['left'].set_color('#e0e0e0')
            ax1.tick_params(colors='#555555')
            
            # Add light grey horizontal gridlines
            ax1.yaxis.grid(True, linestyle='-', which='major', color='#f0f0f0', alpha=0.8)
            ax1.set_axisbelow(True) # Put grid behind bars
            
            # Rotate x labels for better fit
            plt.setp(ax1.xaxis.get_majorticklabels(), rotation=-30, ha="left", rotation_mode="anchor", fontsize=9)
            
            plt.tight_layout()
            canvas1 = FigureCanvasTkAgg(fig1, master=self.dept_chart_frame)
            canvas1.get_tk_widget().pack(fill="both", expand=True)
            canvas1.draw()
        else:
            ctk.CTkLabel(self.dept_chart_frame, text="No High-Risk Data Available", text_color="grey").pack(pady=100)

        # Drug Chart (Pie with Legend) - Dedicated Section
        for w in self.drug_chart_frame.winfo_children(): w.destroy()
        # Full width figure, significantly wider to comfortably fit the pie and the legend side-by-side
        fig2, ax2 = plt.subplots(figsize=(10, 5), dpi=100)
        fig2.patch.set_facecolor('white')
        ax2.set_facecolor('white')
        
        if not df_risk.empty:
            drugs = pd.concat([df_risk['drug_1'], df_risk['drug_2']])
            top_drugs = drugs.value_counts().head(10)
            
            # Title removed from map frame since UI provides it
            # Plotly default colors
            pie_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
            
            wedges, texts, autotexts = ax2.pie(
                top_drugs.values, 
                autopct='%1.1f%%', 
                colors=pie_colors[:len(top_drugs)],
                pctdistance=0.75,
                textprops={'color': "white", 'fontsize': 10}
            )
            
            # Add legend to the right, much larger text and well spaced
            ax2.legend(wedges, top_drugs.index,
                      title="Drug Name",
                      loc="center left",
                      bbox_to_anchor=(1.1, 0.5), # Push legend completely to the right of the pie
                      fontsize=11,
                      title_fontsize=12,
                      frameon=False)
            
            plt.setp(autotexts, size=10, weight="bold")

            # Expand the layout so the legend is not cut off
            plt.tight_layout()
            # Increase right margin explicitly
            fig2.subplots_adjust(right=0.75)
            
            canvas2 = FigureCanvasTkAgg(fig2, master=self.drug_chart_frame)
            canvas2.get_tk_widget().pack(fill="both", expand=True)
            canvas2.draw()
        else:
            ctk.CTkLabel(self.drug_chart_frame, text="No High-Risk Data Available", text_color="grey").pack(pady=100)

if __name__ == "__main__":
    app = DDIAuditorGUI()
    app.mainloop()
