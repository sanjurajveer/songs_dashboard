import pandas as pd
import tkinter as tk
import numpy as np
from tkinter import ttk,filedialog, messagebox
from tkcalendar import DateEntry
from datetime import datetime
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image
import tempfile
import os
import warnings
from tkinter import filedialog, messagebox
#Setup
warnings.filterwarnings("ignore")


class UploadInputFiles:
    def __init__(self, root):
        self.root = root
        self.root.title("Upload Data Input Files")

        # Store selected file paths
        self.file_paths = []
        self.required_files = ["tabdb.csv", "playdb.csv", "requestdb.csv"]

        self.title_label = tk.Label(root, text="Welcome to Ukulele Interface !!!", font=("Arial", 15, "bold"),)
        self.title_label.pack(padx=30,pady=40)

        # Label to prompt the user
        self.label = tk.Label(root, text="Please upload the data files:")
        self.label.pack(pady=10)

        # Button to select files
        self.select_button = tk.Button(root, text="Upload Data Files", command=self.handle_file_selection_and_missing_column)
        self.select_button.pack(pady=5)

        # Button to quit the application
        self.quit_button = tk.Button(root, text="Quit", command=root.quit)
        self.quit_button.pack(pady=25)

    #function to select file from user 
    def get_file_path(self, prompt):
        file_path = filedialog.askopenfilename(title=prompt, filetypes=[("CSV files", "*.csv")])
        return file_path

    def validate_file(self, file_path, required_file):
        # Check if the file exists and is the required file
        if not os.path.isfile(file_path):
            return False, "File does not exist."
        #check if the file selected is same as aksed
        file_name = os.path.basename(file_path)
        if file_name != required_file:
            return False, f"Uploaded file is not the {required_file} file mentioned to upload."
        
        return True, ""

    

    def handle_file_selection_and_missing_column(self):
        # Initialize user_tabdb to None to handle the case when tabdb.csv is missing
        user_tabdb = None

        # Allow the user to select files
        for required_file in self.required_files:
            file_path = self.get_file_path(f"Please upload the file: {required_file}")
            is_valid, message = self.validate_file(file_path, required_file)
            
            if is_valid == False:
                # Show error message
                messagebox.showerror("Error", message) 

            else:
                self.file_paths.append(file_path)
                

        # Check if all required files have been selected
        if len(self.file_paths) == len(self.required_files):
            # Iterate over the file paths and find "tabdb.csv"
            for file_path in self.file_paths:
                file_name = os.path.basename(file_path)

                if file_name == "tabdb.csv":
                    user_tabdb = file_path

            # If tabdb.csv is found, proceed with column validation
            
            if user_tabdb:
                try:
                    # Read the user-uploaded tabdb.csv and the required tabdb.csv
                    file_df = pd.read_csv(user_tabdb, encoding='latin1')
                    
                    
                    # Identify missing columns in the user-uploaded file
                    req_columns = ['song','artist','year','type','gender','duration','language','tabber','source','date','difficulty','specialbooks']
                    missing_columns = [col for col in req_columns if col not in file_df.columns]
                    
                    if missing_columns:
                        
                        column_label = "Column" if len(missing_columns) == 1 else "Columns"
                        verb = "is" if len(missing_columns) == 1 else "are"
                        missing_columns_message = ', '.join(missing_columns)
                        
                        # Message box indicating which columns are missing
                        messagebox.showwarning(f"{column_label} Missing:", f"{missing_columns_message} {column_label.lower()} {verb} missing.")
                        self.root.destroy()
                    else:
                        
                        messagebox.showinfo("Success", "All required columns are present.")

                        # Proceed with loading data
                        final_table, unique_data = self.load_data_input(self.file_paths)

                        # An instance of the filterable table
                        self.filterable_app = FilterTable(tk.Toplevel(self.root), final_table, unique_data)

                        # Display the FilterTable UI
                        self.filterable_app.show()
                #Error message display
                except FileNotFoundError:
                    messagebox.showerror("Error", "The 'tabdb.csv' file could not be found.")
                    self.root.destroy()
                except pd.errors.ParserError:
                    messagebox.showerror("Error", "Error reading the CSV file. Please ensure the file is correctly formatted.")
                    self.root.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"An unexpected error occurred: {e}")
                    self.root.destroy()

            else:
                messagebox.showwarning("Warning", "'tabdb.csv' is missing. Please upload it.")
                self.root.destroy()
        else:
            messagebox.showwarning("Warning", "Please upload all required files.")
            self.root.destroy()
    #saving files in memory and formatting data
    def load_data_input(self,file_paths):
        request = pd.read_csv(file_paths[2], encoding="latin1")
        play = pd.read_csv(file_paths[1], encoding="latin1")
        tab = pd.read_csv(file_paths[0], encoding="latin1")
         #converting column dates to row dates of play and request data
        play_up = (
            play.melt(id_vars=["song", "artist"], var_name="date_val", value_name="Play_count")
            .sort_values(by=["date_val"])
            .reset_index(drop=True)
        )
        request_up = (
            request.melt(id_vars=["song", "artist"], var_name="date_val", value_name="req_type")
            .sort_values(by=["date_val"])
            .reset_index(drop=True)
        )
        #merging the play data and request data and formatting date to date time
        merged_data = play_up.merge(request_up, on=["song", "artist", "date_val"], how="outer")
        merged_data["date_val"] = pd.to_datetime(
            merged_data["date_val"], format="%Y%m%d", errors="coerce"
        ).dt.strftime("%Y/%m/%d")

        #merging tab data with above merged data to create final data frmae and changing column names
        final_table = pd.merge(merged_data, tab, how="left", on=['song', 'artist'])
        final_table = final_table.rename(columns={"date_val": "Date Requested"})
        final_table["Play_count"] = (
            pd.to_numeric(final_table["Play_count"], errors="coerce").fillna(0).astype(int)
        )
        final_table["Date Requested"] = pd.to_datetime(
            final_table["Date Requested"], errors="coerce"
        )
        final_table["date"] = pd.to_datetime(
            final_table["date"], format="%Y%m%d", errors="coerce"
        ).dt.strftime("%d/%m/%Y")
        final_table.loc[final_table["Play_count"] >= 1, "Play_count"] = 1

        # Prepare unique data without duplicates
        unique_data = final_table.drop(
            columns=["Play_count", "req_type", "tabber"]
        )

        # Additional processing for unique_data
        unique_data['difficulty_level'] = pd.cut(unique_data['difficulty'], 
            bins=[0.0, 1.5, 2.5, 3.5, 4.5, 5.5],  
            labels=['0.0 - 1.5', '1.5 - 2.5', '2.5 - 3.5', '3.5 - 4.5', '4.5 - 5.5'],  
            include_lowest=True,  
            right=False
        )

        

        unique_data['duration_seconds'] = pd.to_timedelta(unique_data['duration']).dt.total_seconds()
        unique_data['duration_minutes'] = unique_data['duration_seconds'] / 60
        unique_data['duration_period'] = pd.cut(unique_data['duration_minutes'], 
            bins=[0, 1, 2, 3, 4, 5, 6, 7],  
            labels=['0 - 1', '1 - 2', '2 - 3', '3 - 4', '4 - 5', '5 - 6', '6 - 7'],  
            include_lowest=True,  
            right=False
        )

        
        unique_data['language'] = unique_data['language'].fillna('Unknown')
        unique_data['language'] = unique_data['language'].str.split(',')
        unique_data = unique_data.explode('language', ignore_index=True)
        unique_data['language'] = unique_data['language'].fillna('Unknown')

        unique_data['specialbooks'] = unique_data['specialbooks'].fillna('Unknown')
        unique_data['specialbooks'] = unique_data['specialbooks'].str.split(',')
        unique_data = unique_data.explode('specialbooks', ignore_index=True)
        unique_data['specialbooks'] = unique_data['specialbooks'].fillna('Unknown')

        unique_data['year'] = pd.to_numeric(unique_data['year'], errors='coerce')
        unique_data.dropna(subset=['year'], inplace=True)
        unique_data['year'] = unique_data['year'].astype(int)

        unique_data['gender'] = unique_data['gender'].str.lower()
        unique_data['decade'] = (unique_data['year'] // 10) * 10
        unique_data['decade'] = unique_data['decade'].astype(int)

        unique_data['year'] = unique_data['year'].apply(lambda x: f"{x:04}")
        unique_data['decade'] = unique_data['decade'].apply(lambda x: f"{x:04}")

        return final_table , unique_data


class FilterTable:
    def __init__(self, root, final_table,unique_data):
        self.root = root
        self.root.title("Ukulele Interface")

        # Store original data
        self.original_df = final_table.copy()
        self.unique_df = unique_data.copy()
        

        # Exclude columns for checkboxes
        self.excluded_columns = [
            "Date Requested", "req_type", "tabber", "total_play_count","song","duration_seconds","duration_minutes"
        ]

        # Columns to exclude specifically from checkboxes
        self.checkbox_excluded_columns = self.excluded_columns

        # Define display columns
        self.display_columns = [
            col for col in self.unique_df.columns if col not in self.excluded_columns
        ]


        self.checkbox_columns = [
            'artist', 'year', 'type', 'gender', 'duration', 'language', 'source', 'difficulty', 'specialbooks'
        ]
        
        min_date = unique_data["Date Requested"].min().date().strftime("%d/%m/%Y")
        max_date = unique_data["Date Requested"].max().date().strftime("%d/%m/%Y")

        date_title_frame = tk.Frame(root)
        date_title_frame.pack(fill="x", padx=10, anchor="center")

        # Date Title Label
        date_title_label = tk.Label(date_title_frame, text=f"Data Available from {min_date} to {max_date}", font=("Arial", 15, "bold"), anchor="center")
        date_title_label.pack(side="left", padx=5, pady=5, anchor="center")

        # Date Filter Frame
        filter_frame = tk.Frame(root)
        filter_frame.pack(fill="x", padx=10,pady=10, anchor="center")

        # From Date Filter
        self.from_date_var = tk.BooleanVar()
        tk.Checkbutton(filter_frame, text="From Date:", variable=self.from_date_var).pack(side="left", padx=5)
        self.from_date_entry = DateEntry(filter_frame, width=10, background="darkblue",
                                         foreground="white", borderwidth=2, date_pattern="dd/mm/yyyy")
        self.from_date_entry._set_text(min_date)
        self.from_date_entry.pack(side="left", padx=5)

        # To Date Filter
        self.to_date_var = tk.BooleanVar()
        tk.Checkbutton(filter_frame, text="To Date:", variable=self.to_date_var).pack(side="left", padx=5)
        self.to_date_entry = DateEntry(filter_frame, width=10, background="darkblue",
                                       foreground="white", borderwidth=2, date_pattern="dd/mm/yyyy")
        self.to_date_entry._set_text(max_date)
        self.to_date_entry.pack(side="left", padx=5)

        title_frame = tk.Frame(root)
        title_frame.pack(fill="x", padx=10, anchor="center")

        # Title Label
        title_label = tk.Label(title_frame, text="Select Columns to display", font=("Arial", 15, "bold"), anchor="center")
        title_label.pack(side="left", padx=5, pady=5, anchor="center")

        # Checkbox Frame
        checkbox_frame = tk.Frame(root)
        checkbox_frame.pack(fill="both", padx=5, pady=10, anchor="center")
        self.column_vars = {}
        # Checkboxes for each column except excluded ones
        for col in self.checkbox_columns:
            var = tk.BooleanVar(value=False)
            cb = tk.Checkbutton(
                checkbox_frame, text=col, variable=var, command=self.update_columns
            )
            cb.pack(side="left", padx=5, anchor="center")
            self.column_vars[col] = var

        # Frame for Dropdown Filters
        dropdown_frame = tk.Frame(root)
        dropdown_frame.pack(fill="both", padx=10, pady=5, anchor="center")

        # Dropdowns for type, gender, year, language
        self.dropdown_filters = {}
        for filter_name in ["type", "gender", "year", "language","source","difficulty_level", "duration_period","decade", "specialbooks"]:
            tk.Label(dropdown_frame, text=f"{filter_name}:").pack(
                side="left", padx=2, anchor="center"
            )
            values = list(self.unique_df[filter_name].dropna().unique())
            values.sort()
            
            values = ["All"] + values  # Add "All" option
            var = tk.StringVar(value="All")  # Default to "All"
            
            dropdown = ttk.Combobox(
                dropdown_frame, textvariable=var, values=values, width=6 
            )
            dropdown.pack(side="left", padx=2, anchor="center")
            dropdown.config(state="readonly")
            self.dropdown_filters[filter_name] = (var, dropdown)

        # Filter button
        filter_button = tk.Button(
            filter_frame, text="Filter Results", command=self.apply_filters
        )
        filter_button.pack(side="left", padx=5, anchor="center")

        # Sorting Result
        self.sort_by_var = tk.StringVar(value="song")  # Default sorting column
        self.sort_order_var = tk.StringVar(value="ascending")  # Default sorting order

        sort_label = tk.Label(filter_frame, text="Order")
        sort_label.pack(side="left", padx=5)

        sort_by_menu = ttk.Combobox(
            filter_frame, textvariable=self.sort_by_var, values=["song", "total_play_count", "artist", "year", "duration", "difficulty", "type", "source", "language", "specialbooks"], state="readonly"
        )
        sort_by_menu.pack(side="left", padx=5)

        sort_label = tk.Label(filter_frame, text="By")
        sort_label.pack(side="left", padx=5)

        sort_order_menu = ttk.Combobox(
            filter_frame, textvariable=self.sort_order_var, values=["ascending", "descending"], state="readonly"
        )
        sort_order_menu.pack(side="left", padx=5)

        sort_button = tk.Button(filter_frame, text="Sort Result", command=self.apply_filters)
        sort_button.pack(side="left", padx=5)


        # Error message label
        self.error_label = tk.Label(filter_frame, text="", fg="red")
        self.error_label.pack(side="left", padx=5, anchor="center")

        # Table Frame
        table_frame = tk.Frame(root)
        table_frame.pack(fill="both", expand=True, padx=5, pady=5, anchor="center")

        # Treeview for displaying table
        self.tree = ttk.Treeview(table_frame, show="headings")
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=vsb.set)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        hsb.pack(side="bottom", fill="x")
        self.tree.configure(xscrollcommand=hsb.set)
        self.tree.pack(fill="both", expand=True)

        # Load initial data
        self.load_data(self.unique_df)

        # Chart Options Frame
        chart_frame = tk.Frame(root)
        chart_frame.pack(anchor="center", fill="x", padx=10, pady=5)

        # Chart By
        self.chart_by = tk.StringVar(value="Select Column")
        
        
        self.by_options = [
            "difficulty_level", "duration_period", "language", "source", "decade", "gender", "song"
        ]
        tk.Label(chart_frame, text="Generate Plot By").pack(
            side="left", padx=5, anchor="center"
        )
        ttk.Combobox(
            chart_frame, textvariable=self.chart_by, values=self.by_options, width=20
        ).pack(side="left", padx=5, anchor="center")
        

        # Chart date filters
        
        self.error_message = tk.Label(chart_frame, text="", fg="red")
        self.error_message.pack(side="left", padx=5, anchor="center")
        tk.Button(chart_frame, text="Generate Plot", command=self.generate_graph).pack(
            side="left", padx=5, anchor="center"
        )
        reset_chart_button = tk.Button(
            chart_frame, text="Reset Plot", command=self.reset_chart
        )

        reset_chart_button.pack(side="left", padx=5, anchor="center")

        save_button = tk.Button(
            chart_frame, text="Save Plots", command=self.save_charts_as_pdf
        )

        save_button.pack(side="left", padx=5, anchor="center")

        # Graph Display Canvas
        self.figure = plt.Figure()
        self.canvas = FigureCanvasTkAgg(self.figure, root)
        self.image_files = []
    
    def show(self):
        self.root.deiconify()
        
  ########################################################################################################################################

    def calculate_total_play_count(self, song, start_date=None, end_date=None):
        df = self.original_df[self.original_df["song"] == song]
        if start_date:
            start_date = np.datetime64(start_date)
            df = df[df["Date Requested"] >= start_date]
        if end_date:
            end_date = np.datetime64(end_date)
            df = df[df["Date Requested"] <= end_date]
        return df["Play_count"].sum()

    def load_data(self, data):
        self.tree.delete(*self.tree.get_children())
        
        # Ensuring 'song' and 'total_play_count' columns are always included
        selected_columns = ["song", "total_play_count"] + [col for col, var in self.column_vars.items() if var.get()]
        if "duration" in selected_columns:
            index = selected_columns.index("duration")
    
            # Add new data beside the specified data (after it)
            selected_columns.insert(index + 1, "duration_period")

        if "difficulty" in selected_columns:
            index = selected_columns.index("difficulty")
    
            # Add new data beside the specified data (after it)
            selected_columns.insert(index + 1, "difficulty_level")

        if "year" in selected_columns:
            index = selected_columns.index("year")
    
            # Add new data beside the specified data (after it)
            selected_columns.insert(index + 1, "decade")

        self.tree["columns"] = selected_columns
        for col in selected_columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=100)

        start_date = self.from_date_entry.get_date() if self.from_date_var.get() else None
        end_date = self.to_date_entry.get_date() if self.to_date_var.get() else None

        

        # Calculate total play counts for all songs at once
        total_play_counts = data.groupby("song").apply(lambda x: self.calculate_total_play_count(x["song"].iloc[0], start_date, end_date)).reset_index()
        total_play_counts.rename(columns={0: 'total_play_count'}, inplace=True)
        
        # Merge total play counts back to the original data
        data = data.merge(total_play_counts, on="song", how="left")
        # Apply sorting based on user input
        sort_by = self.sort_by_var.get()
        sort_order = self.sort_order_var.get()
        ascending = True if sort_order == "ascending" else False

        if sort_by in data.columns:
            data = data.sort_values(by=sort_by, ascending=ascending)

        if "difficulty" in selected_columns:
            data["difficulty"] = data["difficulty"].fillna("nan")

        

        # Prepare values for batch insertion
        values_to_insert = [tuple(row) for row in data[selected_columns].itertuples(index=False, name=None)]
        # Insert all values at once
        seen = set()
        for value in values_to_insert:
            if value not in seen:
                seen.add(value)
                self.tree.insert("", "end", values=value)


    def update_columns(self):
        self.load_data(self.unique_df)


    def apply_filters(self):
       
       filtered_df = self.unique_df.copy()

       if self.from_date_var.get():
           from_date = np.datetime64(self.from_date_entry.get_date())
           filtered_df = filtered_df[filtered_df["Date Requested"] >= from_date]
       if self.to_date_var.get():
           to_date = np.datetime64(self.to_date_entry.get_date())
           filtered_df = filtered_df[filtered_df["Date Requested"] <= to_date]

       for filter_name, (var, dropdown) in self.dropdown_filters.items():
           filter_value = var.get()
           if filter_value!='All':
               filtered_df = filtered_df[filtered_df[filter_name] == filter_value]

       # Save the filtered data
       self.filtered_data = filtered_df

       # Apply sorting
       sort_by = self.sort_by_var.get()
       sort_order = self.sort_order_var.get()
       ascending = True if sort_order == "ascending" else False

       if sort_by in self.filtered_data.columns:
          self.filtered_data = self.filtered_data.sort_values(by=sort_by, ascending=ascending)

       # Load the filtered and sorted data into the Treeview
       self.load_data(self.filtered_data)
 
       self.error_label.config(text="") 


    def save_charts_as_pdf(self):
        if not self.image_files:
            self.error_message.config(text="No graphs available to save.")
            return

        # Open the images and save to a single PDF file
        images = [Image.open(img) for img in self.image_files]
        
        pdf_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])

        # Convert to RGB if necessary and save as a PDF
        images[0].save(pdf_path, save_all=True, append_images=images[1:], format="PDF")
        
        # Clear the list and delete the temp files after saving
        for img in self.image_files:
            os.remove(img)  # Deletes the temporary image file
        self.image_files.clear()
        
        self.error_message.config(text=f"All plots saved to {pdf_path}.")


    def generate_graph(self):
    
        by_field = self.chart_by.get()
        
        if by_field not in self.by_options:
            self.error_message.config(text="Invalid plot by option selected.")
            return
            

        selected_columns = [col for col, var in self.column_vars.items() if var.get()]
        
        if "difficulty" in selected_columns:
            selected_columns.append("difficulty_level")

        if "duration" in selected_columns:
            selected_columns.append("duration_period")

        if "year" in selected_columns:
            selected_columns.append("decade")


        if by_field not in selected_columns and by_field != "song":
            if by_field == "difficulty_level":
                show_field = "difficulty"
            elif by_field == "duration_period":
                show_field = "duration"
            elif by_field == "decade":
                show_field = "year"
            else:
                show_field= by_field

            self.error_message.config(text=f"Please select the '{show_field}' column in the table above.")
            return
            

        self.error_message.config(text="")

        

        # Retrieve table data directly for chart generation
        table_data = []
        for item in self.tree.get_children():
            table_data.append(self.tree.item(item)['values'])

            chart_df = pd.DataFrame(table_data, columns=self.tree['columns'])
            chart_df['total_play_count'] = pd.to_numeric(chart_df['total_play_count'], errors='coerce')

            chart_df = chart_df[chart_df['total_play_count'] > 0]
            
            if by_field != "song":
                grouped_data = chart_df.groupby(by_field)["song"].nunique().reset_index(name="song")
                grouped_data.rename(columns={"song": "Number of Songs"}, inplace=True)
            else:
                grouped_data = chart_df
                    
        if 'chart_df' not in locals():
            self.error_message.config(text="No data available for the plot.")
            return
        
        else:


            from_date_str = self.from_date_entry.get_date().strftime("%d/%m/%Y") if self.from_date_var.get() else ""
            to_date_str = self.to_date_entry.get_date().strftime("%d/%m/%Y") if self.to_date_var.get() else ""

            if from_date_str == "" and to_date_str == "":
                date_range_title = " "
            elif from_date_str == "":
                date_range_title = f" Till: {to_date_str}"
            elif to_date_str == "":
                date_range_title = f" From: {from_date_str}"
            else:
                date_range_title = f" (From: {from_date_str} To: {to_date_str})"

            # Prepare the figure and axis for the plot
            self.figure.clear()
            ax = self.figure.add_subplot(111)

            # Create the appropriate chart based on selected column

            
            if by_field == "decade":
                decade_count = chart_df['decade'].value_counts().sort_index().reset_index()
                decade_count['decade'] = decade_count['decade'].astype(str)
                ax.bar(decade_count['decade'], decade_count['count'], color="skyblue", edgecolor="black")
                ax.set_title(f"Bar Chart of Songs by {by_field}{date_range_title}")
                ax.set_xlabel(by_field)
                ax.set_ylabel("No. of Songs Played")

            elif by_field == "source" or by_field == "language":
                if by_field == "source":
                    bar_color = "purple"
                else:
                    bar_color = "orange"

                grouped_data = chart_df.groupby(by_field)['song'].nunique().reset_index()
                grouped_data.rename(columns={"song": "Number of Songs"}, inplace=True)
                ax.bar(grouped_data[by_field], grouped_data["Number of Songs"], color = bar_color)
                ax.set_title(f"Bar Chart of Songs by {by_field}{date_range_title}")
                ax.set_xlabel(by_field)
                ax.set_ylabel("No. of Songs Played")


            elif by_field == "gender":
                grouped_data = chart_df.groupby(by_field)["song"].nunique().reset_index()
                grouped_data.rename(columns={"song": "Number of Songs"}, inplace=True)
                # Calculate total number of songs for percentage calculation
                total_songs = grouped_data["Number of Songs"].sum()

                # Calculate percentage for each category
                grouped_data['percentage'] = grouped_data["Number of Songs"] / total_songs * 100

                # Format the legend labels to include percentages
                legend_labels = [f"{category} ({percentage:.1f}%)" for category, percentage in zip(grouped_data[by_field], grouped_data['percentage'])]
                ax.pie(grouped_data["Number of Songs"], startangle=90)
                ax.axis('equal')
                ax.set_title(f"Pie Chart of Songs by {by_field} {date_range_title}")
                ax.legend(legend_labels, title=by_field, loc='upper right', bbox_to_anchor=(1.1, 1))


            elif by_field in ["difficulty_level", "duration_period"]:
                val_list = chart_df[by_field].unique().tolist()
                if by_field == "difficulty_level":
                    group = "difficulty"
                    hist_color = "red"
                else:
                    group = "duration"
                    hist_color = "green"
                
                
                if len(val_list) != 1:
                    grouped_data = chart_df.groupby(by_field)['song'].nunique().reset_index()
                    grouped_data.rename(columns={"song": "Number of Songs"}, inplace=True)
                    
                    ax.hist(grouped_data[by_field],weights=grouped_data["Number of Songs"], bins=len(grouped_data), edgecolor="black", align="mid", color=hist_color)  
                    ax.set_title(f"Histogram of Songs by {by_field}{date_range_title}")
                    ax.set_xlabel(by_field)
                    ax.set_ylabel("No. of Songs")


                else:

                    if group == "difficulty":

                        # Define the minimum and maximum difficulty values in the data
                        diff_range = val_list[0]
                        min_value = float(diff_range[0:3])  
                        max_value = float(diff_range[6:])  
                        
                        # Define the width of each bin
                        bin_width = 0.25

                        # Generate bin edges
                        bin_edges = list(np.arange(min_value, max_value + bin_width, bin_width))
                        
                        
                        chart_df['difficulty'] = chart_df['difficulty'].replace('nan', None)
                        chart_df['difficulty'] = chart_df['difficulty'].astype(float)
                        
                        blabels = [f"{bin_edges[i]} - {bin_edges[i+1]}" for i in range(len(bin_edges) - 1)]
                        chart_df['difficulty_bin'] = pd.cut(chart_df['difficulty'], bins=bin_edges, labels= blabels, include_lowest=True, right=False)

                        # Group data by the bins and count unique songs
                        grouped_data = chart_df.groupby('difficulty_bin')['song'].nunique().reset_index()
                        grouped_data.rename(columns={"song": "Number of Songs"}, inplace=True)

                        # Plot the histogram
                        ax.hist(grouped_data['difficulty_bin'],weights=grouped_data["Number of Songs"], bins=len(grouped_data), edgecolor="black", align="mid", color="red")  
                        # Set plot titles and labels
                        ax.set_title(f"Histogram of Songs by {by_field}{date_range_title}")
                        ax.set_xlabel(by_field)
                        ax.set_ylabel("No. of Songs")
                        

                    else:

                        chart_df['duration_timedelta'] = pd.to_timedelta(chart_df['duration'])
                        chart_df['duration_seconds'] = chart_df['duration_timedelta'].dt.total_seconds()
                        diff_range = val_list[0]
                        min_value = chart_df['duration_seconds'].min() # Adjust based on your data
                        max_value = chart_df['duration_seconds'].max()  # Adjust based on your data
                        
                        # Define the width of each bin
                        bin_width = 10

                        # Generate bin edges
                        bin_edges = list(np.arange(min_value, max_value + bin_width, bin_width))
                    
                        chart_df['duration'] = chart_df['duration'].replace('nan', None)
                    
                        def seconds_to_min_sec(seconds):
                            minutes = seconds // 60
                            remaining_seconds = seconds % 60
                            return f"{int(minutes):02}:{int(remaining_seconds):02}"

                        
                        blabels = [f"{seconds_to_min_sec(bin_edges[i])} - {seconds_to_min_sec(bin_edges[i+1])}" for i in range(len(bin_edges) - 1)]
                
                        chart_df['duration_bin'] = pd.cut(chart_df['duration_seconds'], bins=bin_edges, labels= blabels, include_lowest=True, right=False)
                        
                        # Group data by the bins and count unique songs
                        grouped_data = chart_df.groupby('duration_bin')['song'].nunique().reset_index()
                        grouped_data.rename(columns={"song": "Number of Songs"}, inplace=True)

                        # Plot the histogram
                        ax.hist(grouped_data['duration_bin'],weights=grouped_data["Number of Songs"], bins=len(grouped_data), edgecolor="black", align="mid", color="green")  
                        # Set plot titles and labels
                        ax.set_title(f"Histogram of Songs by {by_field}{date_range_title}")
                        ax.set_xlabel(by_field)
                        ax.set_ylabel("No. of Songs")
                    

            elif by_field == "song":
                # Filter original_df based on selected dates
                filtered_original_df = self.original_df.copy()

                if self.from_date_var.get():
                    try:
                        from_date = datetime.strptime(self.from_date_entry.get(), "%d/%m/%Y").date()
                        filtered_original_df = filtered_original_df[filtered_original_df["Date Requested"] >= pd.Timestamp(from_date)]
                    except ValueError:
                        self.error_message.config(text="Invalid From Date format (dd/mm/yyyy)")
                        return

                if self.to_date_var.get():
                    try:
                        to_date = datetime.strptime(self.to_date_entry.get(), "%d/%m/%Y").date()
                        filtered_original_df = filtered_original_df[filtered_original_df["Date Requested"] <= pd.Timestamp(to_date)]
                    except ValueError:
                        self.error_message.config(text="Invalid To Date format (dd/mm/yyyy)")
                        return

                # Calculate cumulative songs played
                filtered_original_df["Date Requested"] = pd.to_datetime(filtered_original_df["Date Requested"], format="%d/%m/%Y", errors="coerce")
                filtered_original_df.sort_values(by=["Date Requested"], inplace=True)
                filtered_original_df['Play_count'] = pd.to_numeric(filtered_original_df['Play_count'], errors='coerce')
                cumulative_songs = filtered_original_df.groupby("Date Requested")["Play_count"].sum().reset_index()
                
                cumulative_songs['Cumulative_Play_Count'] = cumulative_songs['Play_count'].cumsum()
                
                ax.plot(cumulative_songs['Date Requested'], cumulative_songs['Cumulative_Play_Count'], color='b')
                ax.set_title(f"Cumulative Number of Songs Played {date_range_title}")
                ax.set_xlabel("Date")
                ax.set_ylabel("Cumulative Songs Played")
                
            else:
                self.error_message.config(text="Invalid chart or by option selected.")
                return

            # Draw the updated canvas with the new plot
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Save the figure to a temporary image file
        temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        self.figure.savefig(temp_file.name, format="png") 
        self.image_files.append(temp_file.name) 

    def reset_chart(self):
        self.chart_by.set("Select Column")
        self.figure.clear()
        self.canvas.draw()
        self.canvas.get_tk_widget().pack_forget()
        self.error_message.config(text="")


if __name__ == "__main__":
    
    root = tk.Tk()
    root.geometry(f"+{(root.winfo_screenwidth() - root.winfo_width()) // 2}+{(root.winfo_screenheight() - root.winfo_height()) // 2}")
    app = UploadInputFiles(root)
    root.mainloop()
