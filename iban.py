import tkinter as tk
from tkinter import ttk
import random
import pyperclip

banks = {
    "البنك الأهلي السعودي": "80",
    "بنك الراجحي": "30",
    "بنك الرياض": "50",
    "البنك السعودي الفرنسي": "55",
    "بنك ساب": "60",
    "البنك العربي الوطني": "65",
    "بنك الجزيرة": "35",
    "بنك البلاد": "70",
    "البنك السعودي للاستثمار": "45",
    "بنك الإنماء": "75"
}

def iban_letter_to_number(ch):
    return str(ord(ch) - 55) if ch.isalpha() else ch

def calculate_check_digits(bank_code, account_number):
    # Create IBAN with temporary check digits '00'
    temp_iban = f"{bank_code}{account_number}SA00"
    # Convert letters to numbers
    numeric_iban = ''.join(iban_letter_to_number(c) for c in temp_iban)
    # Calculate mod 97
    mod_result = int(numeric_iban) % 97
    check_digits = 98 - mod_result
    return f"{check_digits:02d}"

def generate_iban():
    bank_name = bank_combo.get()
    if not bank_name:
        result_var.set("اختر البنك أولاً")
        return

    bank_code = banks[bank_name]
    account_number = ''.join(str(random.randint(0, 9)) for _ in range(18))
    check_digits = calculate_check_digits(bank_code, account_number)
    iban = f"SA{check_digits}{bank_code}{account_number}"
    result_var.set(iban)

def copy_to_clipboard():
    pyperclip.copy(result_var.get())

# واجهة البرنامج
root = tk.Tk()
root.title("مولد IBAN سعودي حقيقي للتست")
root.geometry("400x250")
root.resizable(False, False)

title = ttk.Label(root, text="اختر البنك:", font=("Arial", 12))
title.pack(pady=10)

bank_combo = ttk.Combobox(root, values=list(banks.keys()), font=("Arial", 11), state="readonly")
bank_combo.pack(pady=5)

generate_btn = ttk.Button(root, text="توليد IBAN", command=generate_iban)
generate_btn.pack(pady=10)

result_var = tk.StringVar()
result_label = ttk.Entry(root, textvariable=result_var, font=("Arial", 12), justify="center", width=35)
result_label.pack(pady=5)

copy_btn = ttk.Button(root, text="نسخ إلى الحافظة", command=copy_to_clipboard)
copy_btn.pack(pady=10)

root.mainloop()
