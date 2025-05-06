import customtkinter as ctk
from customtkinter import CTk, CTkLabel, CTkButton, CTkEntry, CTkFrame, CTkToplevel
from customtkinter import *
import psycopg2
from tkinter import messagebox, END
from tkinter.ttk import Treeview, Scrollbar, Combobox
import re
from customtkinter import CTkToplevel, CTkLabel, CTkButton, CTkEntry, CTkFrame 
import ctypes
import random
ctypes.CDLL('/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation')
from tkinter import ttk

# === PostgreSQL CONFIG ===
DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "medease",
    "user": "postgres",
    "password": "himanshu"
}

# === Database Connection Function ===
def check_admin_credentials(admin_id, password):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        query = f"SELECT * FROM Admin WHERE Admin_id = '{admin_id}' AND Password_ = '{password}'"
        cursor.execute(query, (admin_id, password))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result is not None
    except Exception as e:
        messagebox.showerror("Database Error", str(e))
        return False

# === CustomTkinter GUI ===
set_appearance_mode("light")
set_default_color_theme("blue")

root = CTk()
root.geometry("1000x800")
root.title("Pharmacy Management System")

main_frame = CTkFrame(root)
main_frame.pack(expand=True, fill="both")


# === DYNAMIC PAGE LOADER ===
def load_page(title_text):
    for widget in main_frame.winfo_children():
        widget.destroy()

    top_bar = CTkFrame(main_frame)
    top_bar.pack(fill="x", pady=(10, 20))

    back_btn = CTkButton(top_bar, text="←", width=40, height=30, command=show_admin_dashboard)
    back_btn.pack(side="left", padx=10)

    title = CTkLabel(top_bar, text=title_text, font=("Arial", 22, "bold"))
    title.pack(side="left", padx=20)

    placeholder = CTkLabel(main_frame, text=f"This is the '{title_text}' page.", font=("Arial", 16))
    placeholder.pack(pady=50)

def manage_customers():
    for widget in main_frame.winfo_children():
        widget.destroy()

    # === Top bar with back ===
    top_frame = CTkFrame(main_frame)
    top_frame.pack(fill="x", pady=(10, 10))

    back_btn = CTkButton(top_frame, text="←", width=40, height=30, command=show_admin_dashboard)
    back_btn.pack(side="left", padx=10)

    heading = CTkLabel(top_frame, text="Manage Customers", font=("Arial", 22, "bold"))
    heading.pack(side="left", padx=20)

    # Search Section
    search_frame = CTkFrame(main_frame)
    search_frame.pack(pady=10)

    # Attribute Dropdown
    search_attribute = StringVar(value="Customer_Name")
    attribute_options = ["Customer_ID", "Customer_Name", "Age", "Phone_no", "Gender"]
    attribute_menu = CTkOptionMenu(search_frame, variable=search_attribute, values=attribute_options, width=150)
    attribute_menu.grid(row=0, column=0, padx=10)

    # Search Entry
    search_var = StringVar()
    # search_entry = CTkEntry(search_frame, textvariable=search_var, placeholder_text="Search...")
    # search_entry.grid(row=0, column=1, padx=10)

    # Search Button
    def search_customers():
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        attr = search_attribute.get()
        # print(search_attribute.value())
        print(attr)
        term = search_var.get()
        if not term:
            messagebox.showerror("Error", "Enter a value to search")
            return
        try:
            cursor.execute(
                f"SELECT * FROM Customer WHERE CAST({attr} AS TEXT) ILIKE %s",
                (f"%{term}%",)
            )
            
            tree.delete(*tree.get_children())
            for row in cursor.fetchall():
                tree.insert("", "end", values=row)
            
        except Exception as e:
            messagebox.showerror("Error", str(e))

    search_btn = CTkButton(search_frame, text="Search", command=search_customers)
    search_btn.grid(row=0, column=2, padx=10)

    # === Search Entry ===
    search_var = StringVar()

    search_entry = CTkEntry(main_frame, placeholder_text="Search by ID, Name, Age, Phone, Gender", textvariable=search_var, width=400)
    search_entry.pack(pady=10)

    # === Treeview Table ===
    tree_frame = CTkFrame(main_frame)
    tree_frame.pack(padx=10, pady=10, expand=True, fill="both")

    columns = ("ID", "Name", "Email", "Phone", "Age", "Gender", "Address")
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings")

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center")

    vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)

    tree.pack(side="left", fill="both", expand=True)
    vsb.pack(side="right", fill="y")

    # === Load Customer Data ===
    def load_customers(filter_text=""):
        tree.delete(*tree.get_children())
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()

            if filter_text:
                query = f"SELECT * FROM CUSTOMER WHERE CAST({search_attribute.get()} AS TEXT) = '{filter_text}' ORDER BY Gender, Age ;"
                # values = tuple([f"%{filter_text}%"] * 1)
                cursor.execute(query)
            else:
                cursor.execute("SELECT * FROM Customer")

            for row in cursor.fetchall():
                tree.insert("", "end", values=row)

            cursor.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    load_customers()

    # === Search Update ===
    def on_search(a, b, c):
        s = search_var.get() 
        print(f"I have to search {s}")
        load_customers(s)

    search_var.trace_add("write", on_search)

    # === Delete Customer ===
    def delete_customer():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Select a customer to delete.")
            return

        customer_id = tree.item(selected[0])["values"][0]
        confirm = messagebox.askyesno("Confirm", f"Delete customer ID {customer_id}?")

        if confirm:
            try:
                conn = psycopg2.connect(**DB_CONFIG)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM Customer WHERE Customer_ID = %s", (customer_id,))
                conn.commit()
                cursor.close()
                conn.close()
                load_customers()
                messagebox.showinfo("Success", "Customer deleted.")
            except Exception as e:
                messagebox.showerror("Database Error", str(e))

    # === Modify Customer ===
    def modify_customer():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Select a customer to modify.")
            return

        customer_data = tree.item(selected[0])["values"]
        customer_id = customer_data[0]

        # Popup to choose field and new value
        popup = CTkToplevel(root)
        popup.geometry("400x250")
        popup.title("Modify Customer")
        popup.grab_set()

        CTkLabel(popup, text=f"Customer ID: {customer_id}", font=("Arial", 14)).pack(pady=10)

        field_var = StringVar(value="Customer_Name")
        CTkLabel(popup, text="Select Field:").pack()
        fields = ["Customer_Name", "Email_ID", "Phone_no", "Age", "Gender", "Addr"]
        field_menu = CTkOptionMenu(popup, variable=field_var, values=fields)
        field_menu.pack(pady=5)

        value_entry = CTkEntry(popup, placeholder_text="New Value", width=200)
        value_entry.pack(pady=10)

        def apply_change():
            field = field_var.get()
            new_value = value_entry.get()
            try:
                conn = psycopg2.connect(**DB_CONFIG)
                cursor = conn.cursor()
                query = f"UPDATE Customer SET {field} = %s WHERE Customer_ID = %s"
                cursor.execute(query, (new_value, customer_id))
                conn.commit()
                cursor.close()
                conn.close()
                popup.destroy()
                load_customers()
                messagebox.showinfo("Success", "Customer updated.")
            except Exception as e:
                messagebox.showerror("Database Error", str(e))

        CTkButton(popup, text="Update", command=apply_change).pack(pady=10)

    # === Action Buttons ===
    btn_frame = CTkFrame(main_frame)
    btn_frame.pack(pady=10)

    del_btn = CTkButton(btn_frame, text="Delete Customer", command=delete_customer, width=150)
    del_btn.pack(side="left", padx=10)

    mod_btn = CTkButton(btn_frame, text="Modify Customer", command=modify_customer, width=150)
    mod_btn.pack(side="left", padx=10)

# === Admin Dashboard Screen ===
def show_admin_dashboard():
    for widget in main_frame.winfo_children():
        widget.destroy()

    heading = CTkLabel(main_frame, text="Admin Dashboard", font=("Arial", 22, "bold"))
    heading.pack(pady=30)

    logout_btn = CTkButton(main_frame, text="Logout", width=100, height=30, command=show_admin_login)
    logout_btn.pack(pady=10, anchor="ne", padx=20)

    button_texts = [
        "View and Manage Inventory",
        "Manage Customers",
        "Manage Delivery Partners",
        "Manage Supply",
        "Manage Orders",
        "Order Analysis"
    ]

    for text in button_texts:
        if text == "Manage Customers":
            btn = CTkButton(main_frame, text=text, width=250, height=40, command=manage_customers, font=("Arial", 14))
        elif text == "Manage Delivery Partners":
            btn = CTkButton(main_frame, text=text, width=250, height=40, command=manage_delivery_partners, font=("Arial", 14))
        elif text == "Order Analysis":
            btn = CTkButton(main_frame, text=text, width=250, height=40, command=show_order_analytics, font=("Arial", 14))  
        elif text == "View and Manage Inventory":
            btn = CTkButton(main_frame, text=text, width=250, height=40, command=view_manage_inventory, font=("Arial", 14))  
        elif text == "Manage Supply":
            btn = CTkButton(main_frame, text=text, width=250, height=40, command=load_supply_orders, font=("Arial", 14))  
        elif text == "Manage Orders" :
            btn = CTkButton(main_frame, text=text, width=250, height=40, command=view_customer_orders_admin, font=("Arial", 14))  
        else:
            btn = CTkButton(main_frame, text=text, width=250, height=40, font=("Arial", 14))
        btn.pack(pady=8)

def show_analytics_popup(choice):

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    match choice:
        case 1 :
            cur.execute('''
                SELECT Gender, AVG(Age) AS Average_Age
                FROM Customer
                WHERE Gender IN ('M', 'F')
                GROUP BY Gender;
                          ''')
            res = cur.fetchall()
            print(res)
            messagebox.showinfo('Average age of customers', f"The avg {res[0][0]} age is {res[0][1]} and avg {res[1][0]} age is {res[1][1]}")
        case 5 :
            cur.execute('''
                SELECT CAST(SUM(Rating) / (COUNT(*) * 0.05) AS FLOAT) AS Avg_rating_of_all_drivers_in_PERCENT
                FROM DeliveryManReview ;
                          ''')
            res = cur.fetchall()
            print(res)
            messagebox.showinfo('Avg rating of all delivery drivers', f"Avg rating of all delivery drivers is {res[0][0]} %")
        case 10 :
            cur.execute('''
                SELECT AVG(Time_Taken) FROM (
                    SELECT c.Order_ID, 
                        c.Order_Time, 
                        d.Delivery_Time, 
                        AGE(d.Delivery_Time, c.Order_Time) AS Time_Taken
                    FROM ManageOrder c
                    JOIN DeliveredToCustomer d ON c.Order_ID = d.Order_ID
                    )
                ''')
            res = cur.fetchall()
            print(res)
            messagebox.showinfo('Avg time taken for a delivery', f"Avg time for a delivery is {res[0][0]} ")         

def show_table_popup(title, headers, data):
    popup = CTkToplevel()
    popup.title(title)
    popup.geometry("700x400")

    frame = CTkFrame(popup)
    frame.pack(padx=20, pady=20, fill="both", expand=True)

    # Headers
    for col_index, header in enumerate(headers):
        CTkLabel(frame, text=header, font=("Arial", 12, "bold")).grid(row=0, column=col_index, padx=10, pady=5)

    # Rows
    for row_index, row in enumerate(data, start=1):
        for col_index, cell in enumerate(row):
            CTkLabel(frame, text=str(cell)).grid(row=row_index, column=col_index, padx=10, pady=5)

def show_analytics_table(choice):

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    match choice:
        case 2:
            cur.execute('''
                SELECT DATE(Order_Time) AS Order_Date, COUNT(Order_ID) AS Total_Orders
                FROM ManageOrder
                GROUP BY DATE(Order_Time)
                ORDER BY Order_Date;
                          ''')
            res = cur.fetchall() 
            header = [desc[0] for desc in cur.description]   
            show_table_popup("Day-wise orders", header, res) 
        case 3 :
            cur.execute('''
                SELECT Customer_ID, AVG(Price) AS Average_Order_Price
                FROM CustomerOrder
                GROUP BY Customer_ID;
                          ''')
            res = cur.fetchall() 
            header = [desc[0] for desc in cur.description]   
            show_table_popup("Customer-wise orders", header, res) 
        case 4 :
            cur.execute('''
                SELECT * FROM (
                SELECT SUBSTRING(Delivery_address, 4, 90) AS Locality, COUNT(*) AS Num_of_Orders
                FROM ManageOrder
                GROUP BY SUBSTRING(Delivery_address, 4, 90)
                ORDER BY Num_of_Orders DESC  
                ) AS MAX_LOCALITY
                          ''')
            res = cur.fetchall() 
            header = [desc[0] for desc in cur.description]   
            show_table_popup("Locality-wise orders", header, res)        
        case 6 : 
            cur.execute('''
                SELECT 
                    DeliveryPerson_ID, 
                    COUNT(Order_ID) as Num_orders, 
                    COUNT(DISTINCT CAST(Delivery_Time AS DATE)) as Days_worked, 
                    CAST(COUNT(Order_ID) / (COUNT(DISTINCT CAST(Delivery_Time AS DATE)) * 1.0) AS DECIMAL(4,2)) as Avg_rides_per_day
                FROM DeliveredToCustomer
                GROUP BY DeliveryPerson_ID ;
                          ''')
            res = cur.fetchall() 
            header = [desc[0] for desc in cur.description]   
            show_table_popup("Rides per day per delivery person", header, res)      
        case 7 :
            cur.execute('''
                SELECT T1.Medicine_ID, T1.Medicine_Name, T1.Net_sale, T2.Net_cost, T1.Net_sale - T2. Net_cost AS Net_profit 
                FROM(
                SELECT Medicine_ID, Medicine_Name, SUM(Price) AS Net_sale
                FROM CustomerOrder
                GROUP BY Medicine_ID, Medicine_Name
                ) AS T1
                JOIN(
                SELECT Medicine_ID, SUM(Price_per_unit * Quantity) as Net_cost
                FROM SupplyOrder
                GROUP BY Medicine_ID
                ) AS T2
                ON T1.Medicine_ID = T2.Medicine_ID ;
                          ''')
            res = cur.fetchall() 
            header = [desc[0] for desc in cur.description]   
            show_table_popup("Medicine-wise profit", header, res)   
        case 8 :
            cur.execute('''
                SELECT Manufacturer, SUM(Medicine_quantity)
                FROM Medicine, CustomerOrder WHERE Medicine.Medicine_ID = CustomerOrder.Medicine_ID
                GROUP BY Manufacturer
                ORDER BY SUM(Medicine_quantity) DESC ;
                          ''')
            res = cur.fetchall() 
            header = [desc[0] for desc in cur.description]   
            show_table_popup("Manufacturer-wise medicines sold", header, res)           
        case 9 :
            cur.execute('''
                SELECT Supplier_ID, Medicine_ID, SUM(Quantity) as Net_quantity
                FROM SupplyOrder S1
                WHERE Medicine_ID IN (
                    SELECT S2.Medicine_ID
                    FROM SupplyOrder S2
                    WHERE S2.Medicine_ID = S1.Medicine_ID
                    GROUP BY Medicine_ID
                    ORDER BY SUM(Quantity) DESC LIMIT 1
                )
                GROUP BY Supplier_ID, Medicine_ID ;
                          ''')
            res = cur.fetchall() 
            header = [desc[0] for desc in cur.description]   
            show_table_popup("Supplier-wise most ordered medicine", header, res)                

def show_order_analytics():
    for widget in main_frame.winfo_children():
        widget.destroy()

    analytics_frame = CTkFrame(main_frame)
    analytics_frame.pack(fill="both", expand=True)

 


    # === Sidebar (Left Panel) ===
    sidebar = CTkFrame(analytics_frame, width=200)
    sidebar.pack(side="left", fill="y", padx=10, pady=10)

    # === Buttons ===
    CTkButton(sidebar, text="← Back", command=show_admin_dashboard).pack(fill="x", pady=(10, 20))

    buttons = [
        ("Average Customer Age", lambda: show_analytics_popup(1)),
        ("Average Daily Orders", lambda: show_analytics_table(2)),
        ("Average Order Price", lambda: show_analytics_table(3)),
        ("Locality Data", lambda: show_analytics_table(4)),
        ("Avg Delivery Person Rating", lambda: show_analytics_popup(5)),
        ("Avg Deliveries Per Person", lambda: show_analytics_popup(6)),
        ("Medicine-wise Profit", lambda: show_analytics_table(7)),
        ("Most Important Manufacturer", lambda: show_analytics_table(8)),
        ("Supplier-wise Most Ordered Medicine", lambda: show_analytics_table(9)),
        ("Average delivery time", lambda: show_analytics_popup(10))
    ]

    for text, command in buttons:
        btn = CTkButton(sidebar, text=text, command=command, height=32)
        btn.pack(pady=5)

    # === Right content panel (optional placeholder for result) ===
    result_frame = CTkFrame(analytics_frame)
    result_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    result_label = CTkLabel(result_frame, text="Select an analytics option from the left panel.", font=("Arial", 16))
    result_label.pack(pady=20)

    # Store result_label for updates from other functions if needed
    global analytics_result_label
    analytics_result_label = result_label

def view_manage_inventory():
    for widget in main_frame.winfo_children():
        widget.destroy()

    def get_connection():
        return psycopg2.connect(**DB_CONFIG)

    CTkLabel(main_frame, text="Manage Inventory", font=("Arial", 22, "bold")).pack(pady=20)
    CTkButton(main_frame, text="← Back to Dashboard", command=show_admin_dashboard).pack(anchor="w", padx=20, pady=10)

    # === Search and Sort ===
    top_frame = CTkFrame(main_frame)
    top_frame.pack(pady=10, padx=20, fill="x")

    search_entry = CTkEntry(top_frame, placeholder_text="Search by name or category")
    search_entry.pack(side="left", padx=5)

    CTkButton(top_frame, text="Search", command=lambda: refresh_inventory()).pack(side="left", padx=5)

    # === Treeview ===
    cols = ["ID", "Name", "Manufacturer", "Mfg", "Expiry", "Batch", "Price", "Sold", "Category", "Stock"]
    tree = ttk.Treeview(main_frame, columns=cols, show='headings', height=15)
    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, anchor='center', width=100)
    tree.pack(padx=20, pady=10, fill="both", expand=True)

    def refresh_inventory():
        tree.delete(*tree.get_children())
        search_value = search_entry.get().lower()
        #sort_query = "ORDER BY Price_per_unit" if sort_var.get() == "Price" else ""

        try:
            conn = get_connection()
            cur = conn.cursor()

            if search_value:
                query = f"""
                    SELECT * FROM Medicine
                    WHERE LOWER(Medicine_Name) LIKE %s OR LOWER(Category) LIKE %s
                    ORDER BY Price_per_unit
                """
                cur.execute(query, (f"%{search_value}%", f"%{search_value}%"))
            else:
                query = f"SELECT * FROM Medicine ORDER BY Price_per_unit "
                cur.execute(query)

            for row in cur.fetchall():
                tree.insert('', 'end', values=row)

            to_sort = ""

        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            if 'cur' in locals(): cur.close()
            if 'conn' in locals(): conn.close()

    # === Buttons Frame ===
    btn_frame = CTkFrame(main_frame)
    btn_frame.pack(pady=10)

    def delete_medicine():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Please select a medicine to delete.")
            return
        med_id = tree.item(selected[0])['values'][0]
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM Medicine WHERE Medicine_ID = %s;", (med_id,))
            conn.commit()
            refresh_inventory()
            messagebox.showinfo("Deleted", "Medicine deleted successfully.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            cur.close()
            conn.close()

    def modify_stock():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Select a medicine to modify stock.")
            return
        med_id = tree.item(selected[0])['values'][0]

        def update_stock():
            try:
                new_stock = int(stock_entry.get())
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("UPDATE Medicine SET Current_stock = %s WHERE Medicine_ID = %s;", (new_stock, med_id))
                conn.commit()
                refresh_inventory()
                top.destroy()
                messagebox.showinfo("Success", "Stock updated.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        top = ctk.CTkToplevel()
        top.title("Modify Stock")
        CTkLabel(top, text="Enter new stock:").pack(pady=5)
        stock_entry = CTkEntry(top)
        stock_entry.pack(pady=5)
        CTkButton(top, text="Update", command=update_stock).pack(pady=5)

    def edit_details():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Select a medicine to edit.")
            return
        values = tree.item(selected[0])['values']
        med_id = values[0]

        def save_changes():
            try:
                new_vals = (
                    name_entry.get(), manu_entry.get(),
                    mfg_entry.get(), exp_entry.get(),
                    batch_entry.get(), float(price_entry.get()), med_id
                )
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("""
                    UPDATE Medicine
                    SET Medicine_Name = %s, Manufacturer = %s,
                        Date_of_mfg = %s, ExpiryDate = %s,
                        Batch_no = %s, Price_per_unit = %s
                    WHERE Medicine_ID = %s;
                """, new_vals)
                conn.commit()
                refresh_inventory()
                top.destroy()
                messagebox.showinfo("Success", "Details updated.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        top = ctk.CTkToplevel()
        top.title("Edit Medicine Details")
        labels = ["Name", "Manufacturer", "Mfg Date (YYYY-MM-DD)", "Expiry (YYYY-MM-DD)", "Batch No", "Price"]
        defaults = values[1:7]
        entries = []

        for lbl, val in zip(labels, defaults):
            CTkLabel(top, text=lbl).pack()
            entry = CTkEntry(top)
            entry.insert(0, val)
            entry.pack()
            entries.append(entry)

        name_entry, manu_entry, mfg_entry, exp_entry, batch_entry, price_entry = entries
        CTkButton(top, text="Save", command=save_changes).pack(pady=10)

    def insert_medicine():
        def add_new():
            try:
                med_values = (
                    int(id_entry.get()), name_entry.get(), manu_entry.get(),
                    mfg_entry.get(), exp_entry.get(), batch_entry.get(),
                    float(price_entry.get()), int(sold_entry.get()),
                    category_entry.get(), int(stock_entry.get())
                )
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO Medicine
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                """, med_values)
                conn.commit()
                refresh_inventory()
                top.destroy()
                messagebox.showinfo("Inserted", "Medicine added.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        top = ctk.CTkToplevel()
        top.title("Insert New Medicine")

        labels = ["ID", "Name", "Manufacturer", "Mfg Date", "Expiry", "Batch No", "Price", "Units Sold", "Category", "Stock"]
        entries = []

        for lbl in labels:
            CTkLabel(top, text=lbl).pack()
            entry = CTkEntry(top)
            entry.pack()
            entries.append(entry)

        id_entry, name_entry, manu_entry, mfg_entry, exp_entry, batch_entry, price_entry, sold_entry, category_entry, stock_entry = entries
        CTkButton(top, text="Insert", command=add_new).pack(pady=10)

    CTkButton(btn_frame, text="Delete", command=delete_medicine).grid(row=0, column=0, padx=10)
    CTkButton(btn_frame, text="Modify Stock", command=modify_stock).grid(row=0, column=1, padx=10)
    CTkButton(btn_frame, text="Edit Details", command=edit_details).grid(row=0, column=2, padx=10)
    CTkButton(btn_frame, text="Insert New", command=insert_medicine).grid(row=0, column=3, padx=10)

    refresh_inventory()

def load_supply_orders():
    for widget in main_frame.winfo_children():
        widget.destroy()

    # Top bar with back button
    top_frame = CTkFrame(main_frame)
    top_frame.pack(fill="x", pady=(10, 20))

    back_btn = CTkButton(top_frame, text="←", width=40, height=30, command=show_admin_dashboard)
    back_btn.pack(side="left", padx=10)
    

    heading = CTkLabel(top_frame, text="Manage Supply", font=("Arial", 22, "bold"))
    heading.pack(side="left", padx=20)

    CTkLabel(main_frame, text="Supply Order", font=("Arial", 16, "bold")).pack(pady=5)

    # Add View Suppliers button to top right
    view_suppliers_btn = CTkButton(top_frame, text="View Suppliers", width=120, 
                                  command=show_suppliers_window)
    view_suppliers_btn.pack(side="right", padx=10)

    # Main container
    container = CTkFrame(main_frame)
    container.pack(pady=10, padx=20, fill="both", expand=True)

    # Treeview frame
    tree_frame = CTkFrame(container)
    tree_frame.pack(pady=(0, 5))

    columns = ["Request_ID", "Supplier_ID", "Supplier_Name", "Medicine_ID", "Medicine_Name",
               "Price_per_unit", "Quantity", "Order_date", "Delivery_status"]

    # Configure style
    style = ttk.Style()
    style.configure("Treeview.Heading", font=("Arial", 12, "bold"))
    style.configure("Treeview", font=("Arial", 11), rowheight=25)

    # Create Treeview
    tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=12)
    
    # Configure columns
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=120, anchor="center", minwidth=100)

    # Add scrollbar
    vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    vsb.pack(side='right', fill='y')
    tree.pack(side='left', fill='both', expand=True)

    # Populate table
    # ================== LOAD DATA FOR BOTH TABLES ==================
    def load_data():
        # Load Supply Orders
        tree.delete(*tree.get_children())
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM SupplyOrder ORDER BY Order_date DESC")
            for row in cursor.fetchall():
                tree.insert('', 'end', values=row)
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load supply orders:\n{str(e)}")
        
    load_data()



        # Add Filter Button Section
    filter_frame = CTkFrame(container)
    filter_frame.pack(fill='x', pady=(10, 0))

    CTkLabel(filter_frame, text="Filter by Status:").pack(side='left', padx=(0, 10))

    # Add this before creating the filter dropdown
    def get_status_counts():
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Delivery_status, COUNT(*) 
                FROM SupplyOrder 
                GROUP BY Delivery_status
            """)
            return {status: count for status, count in cursor.fetchall()}
        except Exception:
            return {}
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    status_counts = get_status_counts()
    filter_options = [
        f"All ({sum(status_counts.values())})",
        f"Shipped ({status_counts.get('Shipped   ', 0)})",
        f"On The Way ({status_counts.get('On The Way', 0)})",
        f"Delivered ({status_counts.get('Delivered', 0)})",
        f"Cancelled ({status_counts.get('Cancelled ', 0)})"
    ]

    filter_var = StringVar(value="All")
    filter_dropdown = CTkComboBox(filter_frame, 
                                values=filter_options, 
                                variable=filter_var,
                                width=150)
    filter_dropdown.pack(side='left', padx=(0, 10))

    def apply_filter():
        status_filter = filter_var.get()
        
        if status_filter == "All":
            refresh_table()  # Show all orders
            return
            
        # Create filtered window
        filtered_window = CTkToplevel(root)
        filtered_window.title(f"Orders - Status: {status_filter}")
        filtered_window.geometry("1000x600")
        
        # Create treeview for filtered results
        filtered_tree = ttk.Treeview(filtered_window, columns=columns, show='headings', height=20)
        
        for col in columns:
            filtered_tree.heading(col, text=col)
            filtered_tree.column(col, width=120, anchor="center", minwidth=100)
        
        vsb = ttk.Scrollbar(filtered_window, orient="vertical", command=filtered_tree.yview)
        filtered_tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side='right', fill='y')
        filtered_tree.pack(side='left', fill='both', expand=True)
        
        try:
            correct_status = ((status_filter.strip()).split())[0]
            if correct_status == "On" : correct_status = "On The Way"
            print(f"We will search for {correct_status}")
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM SupplyOrder 
                WHERE Delivery_status = %s 
                ORDER BY Order_date DESC
            """, (correct_status,))

            for row in cursor.fetchall():
                filtered_tree.insert('', 'end', values=row)
                
        except Exception as e:
            messagebox.showerror("Filter Error", f"Failed to filter orders:\n{str(e)}")
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    filter_btn = CTkButton(filter_frame, 
                         text="Apply Filter", 
                         command=apply_filter,
                         width=120)
    filter_btn.pack(side='left')


    CTkLabel(filter_frame, text="Update Delivery Status:").pack(side="left", padx=(10, 10))

    # Status dropdown
    status_options = ["Shipped", "On The Way", "Delivered", "Cancelled"]
    status_var = StringVar(value="Select Status")
    status_dropdown = CTkComboBox(filter_frame, 
                                values=status_options, 
                                variable=status_var,
                                width=150)
    status_dropdown.pack(side="left", padx=(10, 10))

    def update_status():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an order from the table first.")
            return

        new_status = status_var.get()
        
        # Enhanced validation
        if new_status in [None, "", "Select Status"]:
            messagebox.showwarning("Invalid Status", 
                                "Please select a valid delivery status from the dropdown.",
                                icon="warning")
            return

        if new_status == tree.item(selected[0])['values'][-1]:  # Check if status is unchanged
            messagebox.showinfo("No Change", 
                            "The selected order already has this status.",
                            icon="info")
            return

        # Proceed with update
        request_id = tree.item(selected[0])['values'][0]
        medicine_id = tree.item(selected[0])['values'][3]

        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()
            
            # Update database
            cursor.execute("""
                UPDATE SupplyOrder
                SET Delivery_status = %s
                WHERE Request_ID = %s AND Medicine_ID = %s
            """, (new_status, request_id, medicine_id))
            conn.commit()
            
            # Update the treeview
            current_values = list(tree.item(selected[0])['values'])
            current_values[-1] = new_status
            tree.item(selected[0], values=current_values)
            
            # Clear the dropdown selection
            status_var.set("Select Status")
            
            messagebox.showinfo("Success", 
                            f"Status updated to '{new_status}' for Order {request_id}",
                            icon="info")
            
        except Exception as e:
            messagebox.showerror("Update Failed", 
                            f"Failed to update status:\n{str(e)}",
                            icon="error")
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    update_btn = CTkButton(filter_frame, 
                          text="Update Status", 
                          command=update_status,
                          width=120)
    update_btn.pack(side="left", padx = (10, 10))






    # ================== SUPPLIER REQUESTS TABLE ==================
    CTkLabel(container, text="Supplier Requests", font=("Arial", 16, "bold")).pack(pady=(0, 5), anchor="w")

    requests_frame = CTkFrame(container)
    requests_frame.pack(fill="both", expand=True)

    requests_columns = ["Supplier_ID", "Medicine_ID", "Requested_quantity", 
                       "Requested_price", "Answered_quantity", "Answered_price", "Response_status", "Request_ID"]

    # Create Supplier Requests Treeview
    requests_tree = ttk.Treeview(requests_frame, columns=requests_columns, show='headings', height=8)
    
    # Configure column widths specifically for the requests table
    requests_col_widths = {   
        "Supplier_ID": 100,
        "Medicine_ID": 100,
        "Requested_quantity": 120,
        "Requested_price": 120,
        "Answered_quantity": 120,
        "Answered_price": 120,
        "Response_status": 120,
        "Request_ID": 100
    }
    
           # Load Supplier Requests
    requests_tree.delete(*requests_tree.get_children())
    try:
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Supplier_ID, Medicine_ID, Requested_quantity, Requested_price,
                       Answered_quantity, Answered_price, Response_status, Request_ID
                FROM SupplierRequests
                ORDER BY Request_ID DESC
            """)
            for row in cursor.fetchall():
                requests_tree.insert('', 'end', values=row)
    except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load supplier requests:\n{str(e)}")

    finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()


    for col in requests_columns:
        requests_tree.heading(col, text=col.replace('_', ' '))
        requests_tree.column(col, width=requests_col_widths.get(col, 120), anchor="center")

    requests_vsb = ttk.Scrollbar(requests_frame, orient="vertical", command=requests_tree.yview)
    requests_tree.configure(yscrollcommand=requests_vsb.set)
    requests_vsb.pack(side='right', fill='y')
    requests_tree.pack(side='left', fill='both', expand=True)


    # ================== ACTION BUTTONS ==================
    action_frame = CTkFrame(container)
    action_frame.pack(fill="x", pady=10)

    # Add buttons for supplier requests
    def update_request():
        selected = requests_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a request to update")
            return
            
        request_data = requests_tree.item(selected[0])['values']
        
        # Debug print to check the data structure
        print("Request Data:", request_data)  # Add this line to verify your data structure
        
        update_window = CTkToplevel(root)
        update_window.title("Update Supplier Request")
        update_window.geometry("400x350")
        
        # Create a mapping between field names and their positions
        column_positions = {col: idx for idx, col in enumerate(requests_columns)}
        
        entries = {}
        fields = [
            ("Request ID", "Request_ID", False),  # Not editable
            ("Supplier ID", "Supplier_ID", False),
            ("Medicine ID", "Medicine_ID", False),
            ("Answered Quantity", "Answered_quantity"),
            ("Answered Price", "Answered_price"),
            ("Response Status", "Response_status")
        ]
        
        for i, (label, key, *editable) in enumerate(fields):
            CTkLabel(update_window, text=label).grid(row=i, column=0, padx=10, pady=5, sticky="e")
            entries[key] = CTkEntry(update_window, width=200)
            
            # Get the value from the correct column position
            value = request_data[column_positions[key]] if request_data[column_positions[key]] is not None else ""
            entries[key].insert(0, str(value))
            
            if len(editable) > 0 and not editable[0]:
                entries[key].configure(state="disabled")
            entries[key].grid(row=i, column=1, padx=10, pady=5)
        
        # Add dropdown for status
        status_options = ["Pending", "Approved", "Rejected"]
        current_status = request_data[column_positions["Response_status"]] if request_data[column_positions["Response_status"]] else "Pending"
        status_var = StringVar(value=current_status)
        
        CTkLabel(update_window, text="Response Status:").grid(row=len(fields), column=0, padx=10, pady=5, sticky="e")
        status_menu = CTkComboBox(update_window, variable=status_var, values=status_options)
        status_menu.grid(row=len(fields), column=1, padx=10, pady=5)

        def submit_update():
            try:
                conn = psycopg2.connect(**DB_CONFIG)
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE SupplierRequests SET
                        Answered_quantity = %s,
                        Answered_price = %s,
                        Response_status = %s
                    WHERE Request_ID = %s AND Medicine_ID = %s
                """, (
                    int(entries["Answered_quantity"].get()) if entries["Answered_quantity"].get() else None,
                    int(entries["Answered_price"].get()) if entries["Answered_price"].get() else None,
                    status_var.get(),
                    request_data[column_positions["Request_ID"]],  # Request_ID
                    request_data[column_positions["Medicine_ID"]]   # Medicine_ID
                ))
                conn.commit()
                messagebox.showinfo("Success", "Request updated successfully!")
                load_data()
                update_window.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers for quantity and price")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update request:\n{str(e)}")
            finally:
                if 'cursor' in locals(): cursor.close()
                if 'conn' in locals(): conn.close()
        
        update_btn = CTkButton(update_window, text="Update Request", command=submit_update)
        update_btn.grid(row=len(fields)+1, column=1, pady=10)

    update_request_btn = CTkButton(action_frame, text="Update Request", command=update_request)
    update_request_btn.pack(side="left", padx=10)

    refresh_btn = CTkButton(action_frame, text="Refresh All", command=load_data)
    refresh_btn.pack(side="right", padx=10)









    # Refresh button
    def refresh_table():
        tree.delete(*tree.get_children())
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM SupplyOrder ORDER BY Order_date DESC")
            for row in cursor.fetchall():
                tree.insert('', 'end', values=row)
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    refresh_btn = CTkButton(filter_frame, 
                           text="Refresh Table", 
                           command=refresh_table,
                           width=120)
    refresh_btn.pack(pady=(0, 0))

def show_suppliers_window():
    """Create a new window to display and manage suppliers"""
    supplier_window = CTkToplevel(root)
    supplier_window.title("Manage Suppliers")
    supplier_window.geometry("900x600")
    
    # Main container
    container = CTkFrame(supplier_window)
    container.pack(pady=10, padx=10, fill="both", expand=True)
    
    # Treeview frame
    tree_frame = CTkFrame(container)
    tree_frame.pack(fill="both", expand=True)
    
    # Supplier table columns
    columns = ["Supplier_ID", "Supplier_Name", "Phone_no", "Email_ID", "Addr", "License_no"]
    
    # Create Treeview
    supplier_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
    
    # Configure columns
    column_widths = {
        "Supplier_ID": 100,
        "Supplier_Name": 150,
        "Phone_no": 120,
        "Email_ID": 180,
        "Addr": 200,
        "License_no": 120
    }
    
    for col in columns:
        supplier_tree.heading(col, text=col.replace('_', ' ').title())
        supplier_tree.column(col, width=column_widths.get(col, 120), anchor="center")
    
    # Add scrollbars
    vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=supplier_tree.yview)
    hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=supplier_tree.xview)
    supplier_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    
    supplier_tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")
    
    tree_frame.grid_rowconfigure(0, weight=1)
    tree_frame.grid_columnconfigure(0, weight=1)
    
    # Populate supplier data
    def load_suppliers():
        supplier_tree.delete(*supplier_tree.get_children())
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Supplier ORDER BY Supplier_ID")
            for row in cursor.fetchall():
                supplier_tree.insert('', 'end', values=row)
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()
    
    load_suppliers()
    
    # Action buttons frame
    btn_frame = CTkFrame(container)
    btn_frame.pack(pady=10)
    
    # Add Supplier button
    def add_supplier():
        add_window = CTkToplevel(supplier_window)
        add_window.title("Add New Supplier")
        add_window.geometry("400x400")
        
        entries = {}
        fields = [
            ("Supplier ID", "Supplier_ID"),
            ("Supplier Name", "Supplier_Name"),
            ("Phone Number", "Phone_no"),
            ("Email", "Email_ID"),
            ("Address", "Addr"),
            ("License No", "License_no")
        ]
        
        for i, (label, key) in enumerate(fields):
            CTkLabel(add_window, text=label).grid(row=i, column=0, padx=10, pady=5, sticky="e")
            entries[key] = CTkEntry(add_window, width=250)
            entries[key].grid(row=i, column=1, padx=10, pady=5)
        
        def submit_supplier():
            try:
                conn = psycopg2.connect(**DB_CONFIG)
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO Supplier (
                        Supplier_ID, Supplier_Name, Phone_no, 
                        Email_ID, Addr, License_no
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    entries["Supplier_ID"].get(),
                    entries["Supplier_Name"].get(),
                    entries["Phone_no"].get(),
                    entries["Email_ID"].get(),
                    entries["Addr"].get(),
                    entries["License_no"].get()
                ))
                conn.commit()
                messagebox.showinfo("Success", "Supplier added successfully!")
                load_suppliers()
                add_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add supplier: {str(e)}")
            finally:
                if 'cursor' in locals(): cursor.close()
                if 'conn' in locals(): conn.close()
        
        submit_btn = CTkButton(add_window, text="Add Supplier", command=submit_supplier)
        submit_btn.grid(row=len(fields), column=1, pady=10)
    
    add_btn = CTkButton(btn_frame, text="Add Supplier", command=add_supplier)
    add_btn.pack(side="left", padx=10)


    # Update Supplier button
    def update_supplier():
        selected = supplier_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a supplier to update")
            return
            
        supplier_data = supplier_tree.item(selected[0])['values']
        
        update_window = CTkToplevel(supplier_window)
        update_window.title("Update Supplier")
        update_window.geometry("400x400")
        
        entries = {}
        fields = [
            ("Supplier ID", "Supplier_ID", False),  # ID shouldn't be editable
            ("Supplier Name", "Supplier_Name", True),
            ("Phone Number", "Phone_no", True),
            ("Email", "Email_ID", True),
            ("Address", "Addr", True),
            ("License No", "License_no", True)
        ]
        
        for i, (label, key, editable) in enumerate(fields):
            CTkLabel(update_window, text=label).grid(row=i, column=0, padx=10, pady=5, sticky="e")
            entries[key] = CTkEntry(update_window, width=250)
            entries[key].insert(0, supplier_data[columns.index(key)])
            entries[key].grid(row=i, column=1, padx=10, pady=5)
            if not editable:
                entries[key].configure(state="disabled")
        
        def submit_update():
            try:
                conn = psycopg2.connect(**DB_CONFIG)
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE Supplier SET
                        Supplier_Name = %s,
                        Phone_no = %s,
                        Email_ID = %s,
                        Addr = %s,
                        License_no = %s
                    WHERE Supplier_ID = %s
                """, (
                    entries["Supplier_Name"].get(),
                    entries["Phone_no"].get(),
                    entries["Email_ID"].get(),
                    entries["Addr"].get(),
                    entries["License_no"].get(),
                    supplier_data[0]  # Original Supplier_ID
                ))
                conn.commit()
                messagebox.showinfo("Success", "Supplier updated successfully!")
                load_suppliers()
                update_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update supplier: {str(e)}")
            finally:
                if 'cursor' in locals(): cursor.close()
                if 'conn' in locals(): conn.close()
        
        update_btn = CTkButton(update_window, text="Update Supplier", command=submit_update)
        update_btn.grid(row=len(fields), column=1, pady=10)
    
    update_btn = CTkButton(btn_frame, text="Update Supplier", command=update_supplier)
    update_btn.pack(side="left", padx=10)



    
    # Delete Supplier button
    def delete_supplier():
        selected = supplier_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a supplier to delete")
            return
            
        supplier_id = supplier_tree.item(selected[0])['values'][0]
        supplier_name = supplier_tree.item(selected[0])['values'][1]
        
        if messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete supplier:\n{supplier_name} (ID: {supplier_id})?"
        ):
            try:
                conn = psycopg2.connect(**DB_CONFIG)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM Supplier WHERE Supplier_ID = %s", (supplier_id,))
                conn.commit()
                messagebox.showinfo("Success", "Supplier deleted successfully!")
                load_suppliers()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete supplier: {str(e)}")
            finally:
                if 'cursor' in locals(): cursor.close()
                if 'conn' in locals(): conn.close()
    
    delete_btn = CTkButton(btn_frame, text="Delete Supplier", command=delete_supplier)
    delete_btn.pack(side="left", padx=10)
    
    # Refresh button
    refresh_btn = CTkButton(btn_frame, text="Refresh", command=load_suppliers)
    refresh_btn.pack(side="left", padx=10)

def view_customer_orders_admin():
    for widget in main_frame.winfo_children():
        widget.destroy()

    # === Fetch delivered orders ===
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT Customer_ID, Order_ID, Delivery_address, Total_price, Order_Time 
            FROM ManageOrder 
            WHERE Order_status = 'Delivered'
            ORDER BY Order_Time DESC
        """)
        delivered_orders = cursor.fetchall()
        cursor.close()
        conn.close()
    except Exception as e:
        messagebox.showerror("Database Error", str(e))
        return

    # === Top Bar ===
    top_frame = CTkFrame(main_frame)
    top_frame.pack(fill="x", pady=(10, 20))

    back_btn = CTkButton(top_frame, text="← Back", command=show_admin_dashboard)
    back_btn.pack(side="left", padx=10)

    heading = CTkLabel(top_frame, text="Delivered Orders", font=("Arial", 20, "bold"))
    heading.pack(pady=5)

    # === Orders Table ===
    table_frame = CTkFrame(main_frame)
    table_frame.pack(padx=10, pady=10, fill="both", expand=True)

    headers = ["Customer ID", "Order ID", "Delivery Address", "Total Price", "Order Time", "Actions"]
    for col, header in enumerate(headers):
        label = CTkLabel(table_frame, text=header, font=("Arial", 14, "bold"))
        label.grid(row=0, column=col, padx=5, pady=5, sticky="ew")

    # === View Order Details Function ===
    def view_order_details(order_id):
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()
            
            # Get all medicines in this order with their full details
            cursor.execute("""
                SELECT Medicine_ID, Medicine_Name, ExpiryDate, Medicine_quantity, Price
                FROM CustomerOrder co
                WHERE co.Order_ID = %s
            """, (order_id,))
            order_items = cursor.fetchall()
            
            cursor.close()
            conn.close()

            # Create details popup window
            popup = CTkToplevel()
            popup.title(f"Order Details - {order_id}")
            popup.geometry("800x500")

            # Create a frame for the table
            details_frame = CTkFrame(popup)
            details_frame.pack(padx=10, pady=10, fill="both", expand=True)

            # Table headers
            item_headers = ["Medicine ID", "Medicine Name", "Expiry Date", "Quantity", 
                          "Price"]
            for col, header in enumerate(item_headers):
                label = CTkLabel(details_frame, text=header, font=("Arial", 12, "bold"))
                label.grid(row=0, column=col, padx=5, pady=5, sticky="ew")

            # Display each medicine in the order
            for row_idx, item in enumerate(order_items, start=1):
                for col_idx, value in enumerate(item):
                    label = CTkLabel(details_frame, text=str(value), font=("Arial", 12))
                    label.grid(row=row_idx, column=col_idx, padx=5, pady=2, sticky="w")

            # Add a close button
            close_btn = CTkButton(popup, text="Close", command=popup.destroy)
            close_btn.pack(pady=10)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch order details: {str(e)}")

    # Display each delivered order in the table
    for row_idx, order in enumerate(delivered_orders, start=1):
        customer_id, order_id, address, total_price, order_time = order
        
        # Display order information
        for col_idx, value in enumerate([customer_id, order_id, address, f"${total_price:.2f}", order_time]):
            label = CTkLabel(table_frame, text=str(value), font=("Arial", 12))
            label.grid(row=row_idx, column=col_idx, padx=5, pady=5, sticky="w")

        # Add "View Details" button for each order
        details_btn = CTkButton(table_frame, text="View Details", 
                              command=lambda oid=order_id: view_order_details(oid),
                              width=100)
        details_btn.grid(row=row_idx, column=len(headers)-1, padx=5, pady=5)

    # Configure grid weights to make columns expandable
    for i in range(len(headers)):
        table_frame.grid_columnconfigure(i, weight=1)

# === Error Popup ===
def show_error_popup(message):
    popup = CTkToplevel(root)
    popup.geometry("300x150")
    popup.title("Login Error")
    popup.grab_set()

    error_label = CTkLabel(popup, text=message, font=("Arial", 14))
    error_label.pack(pady=20)

    ok_button = CTkButton(popup, text="OK", command=popup.destroy)
    ok_button.pack(pady=10)

# === Welcome Popup and go to Dashboard ===
def show_success_popup():
    popup = CTkToplevel(root)
    popup.geometry("300x150")
    popup.title("Welcome")
    popup.grab_set()

    label = CTkLabel(popup, text="Welcome, Admin!", font=("Arial", 16))
    label.pack(pady=20)

    def go_to_dashboard():
        popup.destroy()
        show_admin_dashboard()

    ok_button = CTkButton(popup, text="OK", command=go_to_dashboard)
    ok_button.pack(pady=10)

# === Admin Login Screen ===
def show_admin_login():
    for widget in main_frame.winfo_children():
        widget.destroy()

    # Top bar
    top_frame = CTkFrame(main_frame)
    top_frame.pack(fill="x", pady=(10, 20))

    back_btn = CTkButton(top_frame, text="←", width=40, height=30, font=("Arial", 16), command=show_main_menu)
    back_btn.pack(side="left", padx=10)

    admin_heading = CTkLabel(top_frame, text="Admin Panel", font=("Arial", 22, "bold"))
    admin_heading.pack(side="left", padx=20)

    # Entry fields
    admin_id_entry = CTkEntry(main_frame, placeholder_text="Admin ID", width=250)
    admin_id_entry.pack(pady=10)

    admin_pass_entry = CTkEntry(main_frame, placeholder_text="Password", show="*", width=250)
    admin_pass_entry.pack(pady=10)

    # Login handler
    def handle_login():
        admin_id = admin_id_entry.get()
        password = admin_pass_entry.get()
        if check_admin_credentials(admin_id, password):
            show_success_popup()
        else:
            show_error_popup("Wrong ID or Password")

    login_btn = CTkButton(main_frame, text="Login", width=200, command=handle_login)
    login_btn.pack(pady=20)

# === Delivery Partner Registration Form ===
def show_delivery_partner_form():
    for widget in main_frame.winfo_children():
        widget.destroy()

    def clear_fields():
        for entry in [name_entry, email_entry, phone_entry, aadhaar_entry, dl_entry, vehicle_entry]:
            entry.delete(0, END)

    # def show_error(msg):
    #     popup = CTkToplevel(root)
    #     popup.geometry("350x150")
    #     popup.title("Invalid Input")
    #     popup.grab_set()
    #     CTkLabel(popup, text=msg, font=("Arial", 14), text_color="red").pack(pady=20)
    #     CTkButton(popup, text="OK", command=popup.destroy).pack(pady=10)

    def show_error(msg):
        popup = CTkToplevel(root)
        popup.geometry("350x160")
        popup.title("Error")
        popup.grab_set()  # Disable interaction with main window

        popup.resizable(False, False)
        popup.attributes("-topmost", True)


        CTkLabel(popup, text="⚠️ Invalid Input", font=("Arial", 16, "bold"), text_color="#ff4d4d").pack(pady=(20, 10))
        CTkLabel(popup, text=msg, font=("Arial", 13), wraplength=300, justify="center").pack(pady=(0, 10))

        CTkButton(popup, text="OK", command=popup.destroy, width=100).pack(pady=5)




    def submit_registration():
        name = name_entry.get().strip()
        email = email_entry.get().strip()
        phone = phone_entry.get().strip()
        aadhaar = aadhaar_entry.get().strip()
        dl = dl_entry.get().strip()
        vehicle = vehicle_entry.get().strip()

        # === Validation Rules ===
        if not name:
            show_error("Name cannot be empty.")
            return
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            show_error("Enter a valid email address.")
            return
        if not re.match(r"^[6-9]\d{9}$", phone):
            show_error("Enter a valid 10-digit Indian phone number.")
            return
        if not re.match(r"^\d{12}$", aadhaar):
            show_error("Aadhaar number must be 12 digits.")
            return
        if not re.match(r"^[A-Z]{2}\d{14}$", dl):
            show_error("Driving Licence must be in format: XX00000000000000")
            return
        if not re.match(r"^[A-Z]{2}\d{2}[A-Z]{1,2}\d{4}$", vehicle):
            show_error("Enter a valid vehicle number like DL09AB1234.")
            return

        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO requested_delivery_partners 
                (name_, email, phone, aadhaar, driving_licence, vehicle_no)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (name, email, phone, aadhaar, dl, vehicle))
            conn.commit()

            popup = CTkToplevel(root)
            popup.geometry("300x150")
            popup.title("Registered")
            popup.grab_set()

            CTkLabel(popup, text="Thanks for registration!", font=("Arial", 14)).pack(pady=20)

            def close_and_reset():
                popup.destroy()
                clear_fields()

            CTkButton(popup, text="OK", command=close_and_reset).pack(pady=10)

        except Exception as e:
            conn.rollback()
            show_error(f"Database error: {e}")

    def check_registration_status():
        popup = CTkToplevel(root)
        popup.geometry("300x180")
        popup.title("Check Registration Status")
        popup.grab_set()

        label = CTkLabel(popup, text="Enter Phone Number:", font=("Arial", 14))
        label.pack(pady=10)

        phone_entry_popup = CTkEntry(popup, placeholder_text="Phone Number", width=200)
        phone_entry_popup.pack(pady=5)

        def handle_check():
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()
            phone = phone_entry_popup.get().strip()
            cursor.execute("SELECT status_ FROM requested_delivery_partners WHERE phone = %s", (phone,))
            result = cursor.fetchone()
            status = "xyz" 
            if result :
                status = result[0]
            else:
                cursor.execute(f"SELECT * FROM DeliveryPerson where Phone_no = {phone}") 
                res = cursor.fetchone()
                if res :
                    status = "Accepted"
                else :
                    status = "Rejected"

            messagebox.showinfo("Status", f"Status for {phone}: {status}")

        check_btn = CTkButton(popup, text="Check Status", command=handle_check)
        check_btn.pack(pady=10)

    # === UI Layout ===
    top_frame = CTkFrame(main_frame)
    top_frame.pack(fill="x", pady=(10, 20))

    back_btn = CTkButton(top_frame, text="←", width=40, height=30, command=show_main_menu)
    back_btn.pack(side="left", padx=10)

    heading = CTkLabel(top_frame, text="Delivery Partner Registration", font=("Arial", 20, "bold"))
    heading.pack(side="left", padx=20)

    status_btn = CTkButton(top_frame, text="Check Registration Status", width=120, command=check_registration_status)
    status_btn.pack(side="right", padx=10)

    # === Form Fields ===
    name_label = CTkLabel(main_frame, text="Name", font=("Arial", 14))
    name_label.pack()
    name_entry = CTkEntry(main_frame, width=300)
    name_entry.pack(pady=5)

    email_label = CTkLabel(main_frame, text="Email ID", font=("Arial", 14))
    email_label.pack()
    email_entry = CTkEntry(main_frame, width=300)
    email_entry.pack(pady=5)

    phone_label = CTkLabel(main_frame, text="Phone Number", font=("Arial", 14))
    phone_label.pack()
    phone_entry = CTkEntry(main_frame, width=300)
    phone_entry.pack(pady=5)

    aadhaar_label = CTkLabel(main_frame, text="Aadhaar Number", font=("Arial", 14))
    aadhaar_label.pack()
    aadhaar_entry = CTkEntry(main_frame, width=300)
    aadhaar_entry.pack(pady=5)

    dl_label = CTkLabel(main_frame, text="Driving Licence Number", font=("Arial", 14))
    dl_label.pack()
    dl_entry = CTkEntry(main_frame, width=300)
    dl_entry.pack(pady=5)

    vehicle_label = CTkLabel(main_frame, text="Vehicle Number", font=("Arial", 14))
    vehicle_label.pack()
    vehicle_entry = CTkEntry(main_frame, width=300)
    vehicle_entry.pack(pady=5)

    submit_btn = CTkButton(main_frame, text="Register", width=200, command=submit_registration)
    submit_btn.pack(pady=20)

def manage_delivery_partners():
    for widget in main_frame.winfo_children():
        widget.destroy()

    def get_connection():
        return psycopg2.connect(**DB_CONFIG)


    # === Title & Back Button ===
    CTkLabel(main_frame, text="Manage Delivery Partners", font=("Arial", 22, "bold")).pack(pady=20)
    CTkButton(main_frame, text="← Back to Dashboard", command=show_admin_dashboard).pack(anchor="w", padx=20, pady=10)

    # === Current Delivery Partners ===
    CTkLabel(main_frame, text="Current Delivery Partners", font=("Arial", 16, "bold")).pack(pady=5)

    curr_tree = ttk.Treeview(main_frame, columns=("Name", "Email", "Phone", "Aadhaar", "DL", "Vehicle", "Bank"), show="headings")
    for col in curr_tree["columns"]:
        curr_tree.heading(col, text=col)
        curr_tree.column(col, width=120)

    curr_tree.pack(padx=20, pady=5, fill="x")

    # === Action Buttons for Current Partners ===
    button_frame = CTkFrame(main_frame)
    button_frame.pack(pady=10, padx=20, fill="x")

    def modify_partner():
        selected = curr_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a delivery partner first")
            return
        
        # Get selected partner's data
        partner_data = curr_tree.item(selected[0], 'values')
        
        # Create a modify window (you'll need to implement this)
        open_modify_window(partner_data)

    def delete_partner():
        selected = curr_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a delivery partner first")
            return
        
        partner_data = curr_tree.item(selected[0], 'values')
        partner_name = partner_data[0]  # First column is Name
        
        if messagebox.askyesno("Confirm", f"Delete {partner_name} permanently?"):
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("DELETE FROM DeliveryPerson WHERE DeliveryPerson_Name = %s", (partner_name,))
                conn.commit()
                messagebox.showinfo("Success", f"{partner_name} deleted successfully")
                load_current_partners()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete: {e}")
            finally:
                cur.close()
                conn.close()

    def open_modify_window(partner_data):
        modify_win = CTkToplevel()
        modify_win.title("Modify Delivery Partner")
        modify_win.geometry("400x300")
        
        # Labels and Entry fields
        fields = ["Name", "Email", "Phone", "Aadhaar", "DL", "Vehicle", "Bank"]
        entries = {}
        
        for i, field in enumerate(fields):
            CTkLabel(modify_win, text=field).grid(row=i, column=0, padx=10, pady=5)
            entry = CTkEntry(modify_win, width=200)
            entry.grid(row=i, column=1, padx=10, pady=5)
            entry.insert(0, partner_data[i] if i < len(partner_data) else "")
            entries[field] = entry
        
        def save_changes():
            # Get new values from entries
            new_values = {field: entries[field].get() for field in fields}
            
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("""
                    UPDATE DeliveryPerson SET
                        DeliveryPerson_Name = %s,
                        Email_ID = %s,
                        Phone_no = %s,
                        Aadhar_no = %s,
                        Driving_license_no = %s,
                        Vehicle_no = %s,
                        Bank_acc_no = %s
                    WHERE DeliveryPerson_Name = %s
                """, (
                    new_values["Name"],
                    new_values["Email"],
                    new_values["Phone"],
                    new_values["Aadhaar"],
                    new_values["DL"],
                    new_values["Vehicle"],
                    new_values["Bank"],
                    partner_data[0]  # Original name for WHERE clause
                ))
                conn.commit()
                messagebox.showinfo("Success", "Partner updated successfully")
                load_current_partners()
                modify_win.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Update failed: {e}")
            finally:
                cur.close()
                conn.close()
        
        CTkButton(modify_win, text="Save Changes", command=save_changes).grid(row=len(fields)+1, column=0, columnspan=2, pady=10)

    # Add buttons to the right side
    CTkButton(button_frame, text="Modify Partner", command=modify_partner).pack(side="right", padx=5)
    CTkButton(button_frame, text="Delete Partner", fg_color="#cc0000", hover_color="#990000", command=delete_partner).pack(side="right", padx=5)


    def load_current_partners():
        curr_tree.delete(*curr_tree.get_children())
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT DeliveryPerson_Name, Email_ID, Phone_no, Aadhar_no, Driving_license_no, Vehicle_no, Bank_acc_no FROM DeliveryPerson")
            for row in cur.fetchall():
                curr_tree.insert('', 'end', values=row)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load current partners: {e}")
        finally:
            cur.close()
            conn.close()

    load_current_partners()

    # === Requested Delivery Partners Section ===
    CTkLabel(main_frame, text="Requested Delivery Partners", font=("Arial", 16, "bold")).pack(pady=10)

    # Scrollable Frame for requested delivery partners
    req_scroll_frame = CTkScrollableFrame(main_frame, width=1000, height=300)
    req_scroll_frame.pack(padx=20, pady=10, fill="both", expand=True)
    

    def load_requested_partners():
        for widget in req_scroll_frame.winfo_children():
            widget.destroy()

        rows = []
        try:
            conn = get_connection()
            cur = conn.cursor()
            #cur.execute("SELECT * FROM DeliveryPerson ;")
            cur.execute("select id, name_, email, phone, aadhaar, requested_delivery_partners.driving_licence, vehicle_no, status_ from requested_delivery_partners")
            rows = cur.fetchall()
            print("Hello, world")
            print("Loaded requested_delivery_partners:", rows)  # <-- DEBUG
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load requested partners: {e}")
            return
        finally:
            if 'cur' in locals(): cur.close()
            if 'conn' in locals(): conn.close()


        if not rows:
            CTkLabel(req_scroll_frame, text="No requested delivery partners found.").pack()
            return

        # Header
        headers = ["ID", "Name", "Email", "Phone", "Aadhaar", "DL", "Vehicle", "Status", "Add", "Reject"]
        for i, h in enumerate(headers):
            CTkLabel(req_scroll_frame, text=h, font=("Arial", 12, "bold"), width = 120).grid(row=0, column=i, padx=8, pady=5)

        # Rows
        for idx, row in enumerate(rows, start=1):
            id_, name, email, phone, aadhaar, dl, vehicle, status_ = row

            CTkLabel(req_scroll_frame, text=id_).grid(row=idx, column=0)
            CTkLabel(req_scroll_frame, text=name).grid(row=idx, column=1)
            CTkLabel(req_scroll_frame, text=email).grid(row=idx, column=2)
            CTkLabel(req_scroll_frame, text=phone).grid(row=idx, column=3)
            CTkLabel(req_scroll_frame, text=aadhaar).grid(row=idx, column=4)
            CTkLabel(req_scroll_frame, text=dl).grid(row=idx, column=5)
            CTkLabel(req_scroll_frame, text=vehicle).grid(row=idx, column=6)

            status_var = StringVar(value=status_)
            status_dropdown = CTkComboBox(req_scroll_frame, values=["pending", "approved"], variable=status_var, width=140)
            status_dropdown.grid(row=idx, column=7, padx=5)

            def make_add_function(row_data):
                def add():
                    try:
                        conn = get_connection()
                        cur = conn.cursor()

                        cur.execute("SELECT MAX(DeliveryPerson_ID) FROM DeliveryPerson")
                        result = cur.fetchone()
                        max_id = result[0]

                        # Insert into current_delivery_partners
                        cur.execute("""
                            INSERT INTO DeliveryPerson
                            (DeliveryPerson_ID, DeliveryPerson_Name, Email_ID, Phone_no, Aadhar_no, Driving_license_no, Vehicle_no, Bank_acc_no)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, '')
                        """, (row_data[0] + max_id,
                             row_data[1],
                             row_data[2],
                             int(row_data[3]),
                             int(row_data[4]),
                             row_data[5],
                             row_data[6]) )

                        # Delete from requested_delivery_partners
                        cur.execute("DELETE FROM requested_delivery_partners WHERE id = %s", (row_data[0],))
                        conn.commit()

                        messagebox.showinfo("Success", f"{row_data[1]} moved to current delivery partners")
                        load_current_partners()
                        load_requested_partners()

                    except Exception as e:
                        messagebox.showerror("Error", f"Error moving partner: {e}")
                    finally:
                        cur.close()
                        conn.close()
                return add
            CTkButton(req_scroll_frame, text="Add", command=make_add_function(row)).grid(row=idx, column=8, padx=5)

            def make_reject_function(row_data):
                def reject():
                    try:
                        conn = get_connection()
                        cur = conn.cursor()
                        cur.execute("DELETE FROM requested_delivery_partners WHERE id = %s", (row_data[0],))
                        conn.commit()
                        messagebox.showinfo("Rejected", f"{row_data[1]} has been rejected.")
                        load_requested_partners()
                    except Exception as e:
                        messagebox.showerror("Error", f"Error rejecting partner: {e}")
                    finally:
                        cur.close()
                        conn.close()
                return reject
            CTkButton(req_scroll_frame, text="Reject", fg_color="red", hover_color="#cc0000", command=make_reject_function(row)).grid(row=idx, column=9, padx=5)


    load_requested_partners()

# === Customer interface ===

def show_user_login():
    for widget in main_frame.winfo_children():
        widget.destroy()

    # === Top Bar ===
    top_frame = CTkFrame(main_frame)
    top_frame.pack(fill="x", pady=(10, 20))

    back_btn = CTkButton(top_frame, text="←", width=40, height=30, command=show_main_menu)
    back_btn.pack(side="left", padx=10)

    user_heading = CTkLabel(top_frame, text="User Login", font=("Arial", 22, "bold"))
    user_heading.pack(side="left", padx=20)

    # === Login Form ===
    customer_id_entry = CTkEntry(main_frame, placeholder_text="Customer ID", width=250)
    customer_id_entry.pack(pady=10)

    password_entry = CTkEntry(main_frame, placeholder_text="Password", show="*", width=250)
    password_entry.pack(pady=10)

    def handle_user_login():
        customer_id = customer_id_entry.get()
        password = password_entry.get()

        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM CustomerPasswords WHERE Customer_ID = %s AND Password_ = %s",
                (customer_id, password)
            )
            result = cursor.fetchone()
            cursor.close()
            conn.close()

            if result:
                messagebox.showinfo("Login Success", f"Welcome, {result[0]}!")  # Assuming name is at index 1
                show_user_dashboard(customer_id, result[1])
            else:
                messagebox.showerror("Login Failed", "Invalid Customer ID or Password.")

        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    login_btn = CTkButton(main_frame, text="Login", width=200, command=handle_user_login)
    login_btn.pack(pady=15)

    signup_btn = CTkButton(main_frame, text="Sign Up", width=200, command=show_user_signup)
    signup_btn.pack(pady=5)

def show_user_dashboard(customer_id, customer_name):
    for widget in main_frame.winfo_children():
        widget.destroy()

    # === Main container frames ===
    left_panel = CTkFrame(main_frame, width=150)
    left_panel.pack(side="left", fill="y", padx=5, pady=5)

    content_frame = CTkFrame(main_frame)
    content_frame.pack(side="right", expand=True, fill="both", padx=5, pady=5)

    # === Left panel buttons ===
    update_btn = CTkButton(left_panel, text="Update details", command=lambda: update_user_details(customer_id))
    update_btn.pack(pady=(10, 5), fill="x")

    orders_btn = CTkButton(left_panel, text="View orders", command=lambda: view_user_orders(customer_id))
    orders_btn.pack(pady=5, fill="x")

    # latest_order_btn = CTkButton(left_panel, text="See latest order", command=lambda: view_latest_user_order(customer_id))
    # latest_order_btn.pack(pady=5, fill="x")

    # Spacer
    CTkLabel(left_panel, text="").pack(expand=True, fill="y")

    view_cart_btn = CTkButton(left_panel, text="View Cart", command=lambda: view_user_cart(customer_id))
    view_cart_btn.pack(pady=10, fill="x")

    # === Instruction text on top ===
    instruction_label = CTkLabel(content_frame, text="Select a medicine to add to cart, then choose it's quantity", font=("Arial", 16))
    instruction_label.pack(pady=20)

    # === Display medicines table ===
    display_medicines_table(content_frame, customer_id)

    # === Logout button at bottom right ===
    logout_btn = CTkButton(content_frame, text="Logout", command=show_main_menu)
    logout_btn.pack(side="bottom", anchor="se", padx=10, pady=10)

def display_medicines_table(parent_frame, customer_id):
    import tkinter as tk
    from tkinter import ttk, simpledialog

    tree = ttk.Treeview(parent_frame, columns=(
        "ID", "Name", "Manufacturer", "Mfg", "Expiry", "Batch", "Price", "Sold", "Category"), show="headings")

    headers = ["ID", "Name", "Manufacturer", "Mfg", "Expiry", "Batch", "Price", "Sold", "Category"]
    for header in headers:
        tree.heading(header, text=header)
        tree.column(header, width=100)

    tree.pack(fill="both", expand=True)

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute('''SELECT Medicine_ID, Medicine_Name, Manufacturer, Date_of_mfg, 
                          ExpiryDate, Batch_no, Price_per_unit, no_of_units_sold, Category
                       FROM Medicine''')
        rows = cursor.fetchall()
        for row in rows:
            tree.insert("", "end", values=row)
        cursor.close()
        conn.close()
    except Exception as e:
        messagebox.showerror("Database Error", str(e))
        return

    def add_to_cart():
        selected = tree.focus()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a medicine first.")
            return

        item = tree.item(selected)["values"]
        medicine_id, name, manufacturer, mfg, expiry, batch, price, sold, category = item

        # Ask user for quantity
        qty = simpledialog.askinteger("Quantity", f"Enter quantity for {name}:", minvalue=1)
        if qty is None:
            return

        total_price = float(price) * qty

        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO ShoppingCart (Customer_ID, Medicine_ID, Price, ExpiryDate)
                VALUES (%s, %s, %s, %s)
            """, (customer_id, medicine_id, int(total_price), expiry))
            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("Success", f"{name} added to cart successfully.")
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    add_btn = CTkButton(parent_frame, text="Add Selected to Cart", command=add_to_cart)
    add_btn.pack(pady=10)

def view_user_cart(customer_id):
    for widget in main_frame.winfo_children():
        widget.destroy()

    def remove_item(medicine_name, expiry_date):
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()

            # Get the Medicine_ID from name (assuming names are unique, otherwise adjust)
            cursor.execute("SELECT Medicine_ID FROM Medicine WHERE Medicine_Name = %s", (medicine_name,))
            medicine_id = cursor.fetchone()[0]

            # Remove only one occurrence of that medicine and expiry
            cursor.execute("""
                DELETE FROM ShoppingCart
                WHERE ctid IN (
                    SELECT ctid FROM ShoppingCart
                    WHERE Customer_ID = %s AND Medicine_ID = %s AND ExpiryDate = %s
                    LIMIT 1
                )
            """, (customer_id, medicine_id, expiry_date))

            conn.commit()
            cursor.close()
            conn.close()
            view_user_cart(customer_id)  # Refresh the cart
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # === Fetch cart data ===
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT M.Medicine_Name, M.Price_per_unit, S.ExpiryDate, S.Price
            FROM ShoppingCart S
            JOIN Medicine M ON S.Medicine_ID = M.Medicine_ID
            WHERE S.Customer_ID = %s
        """, (customer_id,))
        cart_items = cursor.fetchall()
        cursor.close()
        conn.close()
    except Exception as e:
        messagebox.showerror("Database Error", str(e))
        return

    # === Top bar ===
    top_frame = CTkFrame(main_frame)
    top_frame.pack(fill="x", pady=(10, 20))

    back_btn = CTkButton(top_frame, text="← Back", command=lambda: show_user_dashboard(customer_id, ""))
    back_btn.pack(side="left", padx=10)

    heading = CTkLabel(top_frame, text="Your Shopping Cart", font=("Arial", 20, "bold"))
    heading.pack(pady=5)

    # === Cart Table ===
    table_frame = CTkFrame(main_frame)
    table_frame.pack(padx=10, pady=10, fill="both", expand=True)

    headers = ["Medicine Name", "Unit Price", "Expiry Date", "Total Price", "Action"]
    for col, header in enumerate(headers):
        label = CTkLabel(table_frame, text=header, font=("Arial", 14, "bold"))
        label.grid(row=0, column=col, padx=10, pady=5)

    total_price = 0.0
    for row_index, row_data in enumerate(cart_items, start=1):
        med_name, unit_price, expiry, price = row_data
        total_price += float(price)

        # Display data
        for col_index, item in enumerate(row_data):
            label = CTkLabel(table_frame, text=str(item), font=("Arial", 12))
            label.grid(row=row_index, column=col_index, padx=10, pady=5)

        # Remove button
        remove_btn = CTkButton(
            table_frame, text="Remove",
            command=lambda m=med_name, e=expiry: remove_item(m, e)
        )
        remove_btn.grid(row=row_index, column=4, padx=10, pady=5)

    # === Total Price Label ===
    total_label = CTkLabel(main_frame, text=f"Total Price: ₹ {round(total_price, 2)}", font=("Arial", 16, "bold"))
    total_label.pack(pady=10)

    # === Place Order Button ===
    place_order_btn = CTkButton(
        main_frame, text="Place Order", width=150,
        command=lambda: place_order(customer_id)
    )
    place_order_btn.pack(side="right", anchor="se", padx=20, pady=10)

def update_user_details(customer_id):
    for widget in main_frame.winfo_children():
        widget.destroy()

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT Customer_Name, Email_ID, Phone_no, Age, Gender, Addr FROM Customer WHERE Customer_ID = %s", (customer_id,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if not user:
            messagebox.showerror("Error", "Customer not found.")
            return

    except Exception as e:
        messagebox.showerror("Database Error", str(e))
        return

    name_val, email_val, phone_val, age_val, gender_val, addr_val = user

    # Top bar with back button
    top_frame = CTkFrame(main_frame)
    top_frame.pack(fill="x", pady=(10, 10))

    back_btn = CTkButton(top_frame, text="← Back", command=lambda: show_user_dashboard(customer_id, name_val))
    back_btn.pack(side="left", padx=10)

    heading = CTkLabel(main_frame, text="Update Your Details", font=("Arial", 20, "bold"))
    heading.pack(pady=10)

    # Scrollable frame for inputs
    scroll_frame = CTkScrollableFrame(main_frame, width=400, height=300)
    scroll_frame.pack(pady=10)

    # Input fields
    field_data = {}

    def add_field(label_text, value):
        label = CTkLabel(scroll_frame, text=label_text, anchor="w", font=("Arial", 14))
        label.pack(fill="x", padx=10, pady=(10, 2))
        entry = CTkEntry(scroll_frame, width=300)
        entry.insert(0, value)
        entry.pack(padx=10, pady=(0, 5))
        field_data[label_text] = entry

    add_field("Full Name", name_val)
    add_field("Email", email_val)
    add_field("Phone Number", phone_val)
    add_field("Age", str(age_val))
    add_field("Address", addr_val)

    # Update button
    def update_in_db():
        try:
            updated_name = field_data["Full Name"].get()
            updated_email = field_data["Email"].get()
            updated_phone = field_data["Phone Number"].get()
            updated_age = int(field_data["Age"].get())
            updated_address = field_data["Address"].get()

            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE Customer
                SET Customer_Name = %s,
                    Email_ID = %s,
                    Phone_no = %s,
                    Age = %s,
                    Addr = %s
                WHERE Customer_ID = %s
            """, (updated_name, updated_email, updated_phone, updated_age, updated_address, customer_id))

            conn.commit()
            cursor.close()
            conn.close()

            messagebox.showinfo("Success", "Details updated successfully.")
            show_user_dashboard(customer_id, updated_name)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    update_btn = CTkButton(main_frame, text="Update", command=update_in_db, width=200)
    update_btn.pack(pady=10)

def place_order(customer_id):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # 1. Get new Order_ID
        cursor.execute("SELECT COALESCE(MAX(Order_ID), 0) + 1 FROM CustomerOrder")
        new_order_id = cursor.fetchone()[0]

        # 2. Get shopping cart items
        cursor.execute("SELECT Medicine_ID, Price, ExpiryDate FROM ShoppingCart WHERE Customer_ID = %s", (customer_id,))
        cart_items = cursor.fetchall()

        if not cart_items:
            messagebox.showinfo("Empty Cart", "Your shopping cart is empty.")
            return

        total_price = 0

        for item in cart_items:
            medicine_id, price, expiry = item
            price = float(price)
            total_price += price

            cursor.execute("SELECT Medicine_Name FROM Medicine WHERE Medicine_ID = %s", (medicine_id,))
            medicine_name = cursor.fetchone()[0]

            cursor.execute("SELECT Addr FROM Customer WHERE Customer_ID = %s", (customer_id,))
            address = cursor.fetchone()[0]

            cursor.execute(
                """
                INSERT INTO CustomerOrder (
                    Customer_ID, Medicine_ID, Price, ExpiryDate,
                    Medicine_Name, Order_ID, Delivery_address,
                    Medicine_quantity, Order_status
                )
                SELECT %s, %s, %s, %s, %s, %s, %s, COUNT(*), 'Pending'
                FROM ShoppingCart
                WHERE Customer_ID = %s AND Medicine_ID = %s
                """,
                (customer_id, medicine_id, price, expiry, medicine_name, new_order_id, address, customer_id, medicine_id)
            )

        # 3. Insert into ManageOrder
        delivery_person_id = random.randint(1, 5)  # Assuming delivery IDs range from 1 to 5
        cursor.execute(
            """
            INSERT INTO ManageOrder (
                DeliveryPerson_ID, Order_status, Order_ID,
                Delivery_address, Customer_ID, Total_price, Order_Time
            ) VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """,
            (delivery_person_id, "Pending", new_order_id, address, customer_id, total_price)
        )

        # Optionally clear the cart
        cursor.execute("DELETE FROM ShoppingCart WHERE Customer_ID = %s", (customer_id,))

        conn.commit()
        messagebox.showinfo("Order Placed", f"Your order #{new_order_id} has been placed successfully!")

    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        cursor.close()
        conn.close()

def view_user_orders(customer_id):
    for widget in main_frame.winfo_children():
        widget.destroy()

    # === Fetch orders ===
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DeliveryPerson_ID, Order_status, Order_ID, Delivery_address, Total_price, Order_Time 
            FROM ManageOrder 
            WHERE Customer_ID = %s
        """, (customer_id,))
        orders = cursor.fetchall()
        cursor.close()
        conn.close()
    except Exception as e:
        messagebox.showerror("Database Error", str(e))
        return

    # === Top Bar ===
    top_frame = CTkFrame(main_frame)
    top_frame.pack(fill="x", pady=(10, 20))

    back_btn = CTkButton(top_frame, text="← Back", command=lambda: show_user_dashboard(customer_id, ""))
    back_btn.pack(side="left", padx=10)

    heading = CTkLabel(top_frame, text="Your Orders", font=("Arial", 20, "bold"))
    heading.pack(pady=5)

    # === Orders Table ===
    table_frame = CTkFrame(main_frame)
    table_frame.pack(padx=10, pady=10, fill="both", expand=True)

    headers = ["", "DeliveryPerson ID", "Status", "Order ID", "Address", "Total Price", "Time"]
    for col, header in enumerate(headers):
        label = CTkLabel(table_frame, text=header, font=("Arial", 14, "bold"))
        label.grid(row=0, column=col, padx=5, pady=5)

    import tkinter as tk
    selected_order_id = tk.StringVar()

    for row_index, order in enumerate(orders, start=1):
        order_id = order[2]

        # Radio button for selection
        radio = tk.Radiobutton(table_frame, variable=selected_order_id, value=order_id)
        radio.grid(row=row_index, column=0, padx=5)

        # Now display all other columns starting from col=1
        for col_index, val in enumerate(order):
            label = CTkLabel(table_frame, text=str(val), font=("Arial", 12))
            label.grid(row=row_index, column=col_index + 1, padx=5, pady=5)

    # === Mark Delivered ===
    def mark_delivered():
        order_id = selected_order_id.get()
        if not order_id:
            messagebox.showwarning("No Selection", "Please select an order.")
            return

        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()

            # Get DeliveryPerson_ID
            cursor.execute("SELECT DeliveryPerson_ID FROM ManageOrder WHERE Order_ID = %s", (order_id,))
            delivery_person_id = cursor.fetchone()[0]

            # Insert into DeliveredToCustomer
            cursor.execute("""
                INSERT INTO DeliveredToCustomer (Customer_ID, DeliveryPerson_ID, Order_ID, Delivery_Time)
                VALUES (%s, %s, %s, NOW())
            """, (customer_id, delivery_person_id, order_id))

            # Update ManageOrder status
            cursor.execute("UPDATE ManageOrder SET Order_status = 'Delivered' WHERE Order_ID = %s", (order_id,))

            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("Success", "Order marked as delivered.")

        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    # === Review Delivery Person ===
    def review_delivery():
        order_id = selected_order_id.get()
        if not order_id:
            messagebox.showwarning("No Selection", "Please select an order.")
            return

        popup = tk.Toplevel()
        popup.title("Review Delivery")

        CTkLabel(popup, text="Enter Review:").pack(pady=5)
        review_entry = CTkEntry(popup, width=300)
        review_entry.pack(pady=5)

        CTkLabel(popup, text="Enter Rating (1-5):").pack(pady=5)
        rating_entry = CTkEntry(popup, width=100)
        rating_entry.pack(pady=5)

        def submit_review():
            review = review_entry.get()
            rating = rating_entry.get()

            try:
                rating_val = int(rating)
                if not (1 <= rating_val <= 5):
                    raise ValueError("Rating must be between 1 and 5")

                conn = psycopg2.connect(**DB_CONFIG)
                cursor = conn.cursor()
                cursor.execute("SELECT DeliveryPerson_ID FROM ManageOrder WHERE Order_ID = %s", (order_id,))
                delivery_person_id = cursor.fetchone()[0]

                cursor.execute("""
                    INSERT INTO DeliveryManReview (Order_ID, DeliveryPerson_ID, Review, Rating)
                    VALUES (%s, %s, %s, %s)
                """, (order_id, delivery_person_id, review, rating_val))

                conn.commit()
                cursor.close()
                conn.close()
                messagebox.showinfo("Thank you!", "Review submitted.")
                popup.destroy()

            except Exception as e:
                messagebox.showerror("Error", str(e))

        CTkButton(popup, text="Submit", command=submit_review).pack(pady=10)

    # === View More Details ===
    def view_order_details():
        order_id = selected_order_id.get()
        if not order_id:
            messagebox.showwarning("No Selection", "Please select an order.")
            return

        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Medicine_Name, Price, ExpiryDate, Medicine_quantity, Order_status
                FROM CustomerOrder
                WHERE Order_ID = %s
            """, (order_id,))
            details = cursor.fetchall()
            cursor.close()
            conn.close()

            popup = tk.Toplevel()
            popup.title("Order Details")

            for i, row in enumerate(details):
                for j, val in enumerate(row):
                    label = CTkLabel(popup, text=str(val), font=("Arial", 12))
                    label.grid(row=i, column=j, padx=10, pady=5)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # === Buttons ===
    btn_frame = CTkFrame(main_frame)
    btn_frame.pack(pady=20)

    CTkButton(btn_frame, text="Mark as Delivered", command=mark_delivered).grid(row=0, column=0, padx=10)
    CTkButton(btn_frame, text="Rate & Review Delivery Person", command=review_delivery).grid(row=0, column=1, padx=10)
    CTkButton(btn_frame, text="View More Details of Order", command=view_order_details).grid(row=0, column=2, padx=10)

def show_user_signup():
    for widget in main_frame.winfo_children():
        widget.destroy()

    form_frame = CTkFrame(main_frame)
    form_frame.pack(padx=20, pady=20)

    CTkLabel(form_frame, text="User Signup", font=("Arial", 20, "bold")).grid(row=0, column=0, columnspan=2, pady=15)

    # === Entry fields ===
    labels = ["Name", "Email", "Phone", "Age", "Address", "Password"]
    entries = {}

    for i, label in enumerate(labels):
        CTkLabel(form_frame, text=label + ":").grid(row=i+1, column=0, sticky="e", padx=10, pady=5)
        if label == "Password":
            entry = CTkEntry(form_frame, width=250, show="*")
        else:
            entry = CTkEntry(form_frame, width=250)
        entry.grid(row=i+1, column=1, padx=10, pady=5)
        entries[label] = entry

    # === Gender dropdown ===
    CTkLabel(form_frame, text="Gender:").grid(row=len(labels)+1, column=0, sticky="e", padx=10, pady=5)
    gender_var = StringVar(value="M")
    gender_dropdown = CTkComboBox(form_frame, values=["M", "F", "T"], variable=gender_var, width=120)
    gender_dropdown.grid(row=len(labels)+1, column=1, padx=10, pady=5)

    def is_valid_phone(phone):
        return re.fullmatch(r"[6-9]\d{9}", phone)

    def is_valid_email(email):
        return re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email)

    def is_valid_age(age):
        return age.isdigit() and int(age) > 0

    def submit_signup():
        name = entries["Name"].get().strip()
        email = entries["Email"].get().strip()
        phone = entries["Phone"].get().strip()
        age = entries["Age"].get().strip()
        gender = gender_var.get()
        addr = entries["Address"].get().strip()
        password = entries["Password"].get().strip()

        # === Validations ===
        if not all([name, email, phone, age, gender, addr, password]):
            messagebox.showerror("Error", "All fields are required.")
            return
        if not is_valid_phone(phone):
            messagebox.showerror("Error", "Phone number must be 10 digits and start with 6, 7, 8, or 9.")
            return
        if not is_valid_email(email):
            messagebox.showerror("Error", "Invalid email format.")
            return
        if not is_valid_age(age):
            messagebox.showerror("Error", "Age must be a positive number.")
            return
        if len(password) > 15:
            messagebox.showerror("Error", "Password must be at most 15 characters.")
            return

        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cur = conn.cursor()

            # Insert into Customer table
            cur.execute("SELECT MAX(Customer_ID) FROM Customer")
            res = cur.fetchone()
            max_id = res[0]
            cus_id = max_id + 1
            cur.execute("""
                INSERT INTO Customer (Customer_ID, Customer_Name, Email_ID, Phone_no, Age, Gender, Addr)
                VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING Customer_ID
            """, (cus_id, name, email, int(phone), int(age), gender, addr))


            # Insert password into CustomerPasswords table
            cur.execute("""
                INSERT INTO CustomerPasswords (Customer_ID, Password_)
                VALUES (%s, %s)
            """, (cus_id, password))

            conn.commit()
            messagebox.showinfo("Success", f"Account created successfully!\nYour customer ID is {cus_id}")
            show_user_login()

        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            if 'cur' in locals(): cur.close()
            if 'conn' in locals(): conn.close()

    CTkButton(form_frame, text="Sign Up", command=submit_signup).grid(row=len(labels)+3, columnspan=2, pady=15)

# === Main Menu Screen ===
def show_main_menu():
    for widget in main_frame.winfo_children():
        widget.destroy()

    heading_label = CTkLabel(main_frame, text="Pharmacy Management System", font=("Arial", 24, "bold"))
    heading_label.pack(pady=40)

    admin_btn = CTkButton(main_frame, text="Admin Login", width=200, height=40, font=("Arial", 14), command=show_admin_login)
    admin_btn.pack(pady=10)

    user_btn = CTkButton(main_frame, text="User Login", width=200, height=40, font=("Arial", 14), command=show_user_login)
    user_btn.pack(pady=10)

    # register_btn = CTkButton(main_frame, text="Register as Delivery Partner", width=200, height=40, font=("Arial", 14))
    register_btn = CTkButton(main_frame, text="Register as Delivery Partner", width=200, height=40, font=("Arial", 14), command=show_delivery_partner_form)

    register_btn.pack(pady=10)

# Start from main menu
show_main_menu()
root.mainloop()

   