import tkinter as tk
from tkinter import ttk
import random
import pyperclip

banks = {
    "بنك الإنماء": "05",
    "البنك الأهلي السعودي (SNB)": "10",
    "بنك البلاد": "15",
    "بنك الرياض": "20",
    "البنك العربي الوطني": "30",
    "بنك سامبا (اندمج مع الأهلي)": "40",
    "بنك ساب (SABB)": "45",
    "البنك الأول (SAB)": "50",
    "البنك السعودي الفرنسي": "55",
    "بنك الجزيرة": "60",
    "البنك السعودي للاستثمار": "65",
    "بنك البحرين الوطني": "71",
    "بنك الكويت الوطني": "75",
    "بنك مسقط": "76",
    "بنك الراجحي": "80",
    "دويتشه بنك": "81",
    "بنك باكستان الوطني": "82",
    "البنك الزراعي التركي": "84",
    "بنك بي إن بي باريبا (BNP)": "85",
    "جي بي مورغان تشيس (JPMorgan)": "86",
    "بنك الخليج الدولي (GIB)": "90",
    "بنك الإمارات الدولي": "95",
}

# Reverse lookup: code -> bank name (for validator)
bank_codes_lookup = {v: k for k, v in banks.items()}

# History storage
iban_history = []
is_dark_mode = False

# Theme colors
LIGHT_THEME = {
    "bg": "#f5f5f5",
    "fg": "#1a1a1a",
    "frame_bg": "#ffffff",
    "entry_bg": "#ffffff",
    "button_bg": "#e0e0e0",
    "accent": "#2196F3",
    "success": "#4CAF50",
    "error": "#f44336"
}

DARK_THEME = {
    "bg": "#1e1e1e",
    "fg": "#e0e0e0",
    "frame_bg": "#2d2d2d",
    "entry_bg": "#3d3d3d",
    "button_bg": "#404040",
    "accent": "#64B5F6",
    "success": "#81C784",
    "error": "#e57373"
}

def iban_letter_to_number(ch):
    return str(ord(ch) - 55) if ch.isalpha() else ch

def calculate_check_digits(bank_code, account_number):
    temp_iban = f"{bank_code}{account_number}SA00"
    numeric_iban = ''.join(iban_letter_to_number(c) for c in temp_iban)
    mod_result = int(numeric_iban) % 97
    check_digits = 98 - mod_result
    return f"{check_digits:02d}"

def format_iban(iban):
    """Format IBAN in groups of 4 for readability"""
    iban_clean = iban.replace(" ", "")
    return " ".join(iban_clean[i:i+4] for i in range(0, len(iban_clean), 4))

def get_bank_name_from_code(code):
    """Get bank name from 2-digit code"""
    return bank_codes_lookup.get(code, "بنك غير معروف")

def validate_iban(iban):
    """Validate IBAN using Mod 97 algorithm"""
    iban_clean = iban.replace(" ", "").upper()
    
    if len(iban_clean) != 24:
        return False, "طول الـ IBAN غير صحيح (يجب أن يكون 24 خانة)", ""
    
    if not iban_clean.startswith("SA"):
        return False, "الـ IBAN يجب أن يبدأ بـ SA", ""
    
    if not iban_clean[2:].isalnum():
        return False, "الـ IBAN يحتوي على أحرف غير صالحة", ""
    
    # Detect bank from code (positions 4-5)
    bank_code = iban_clean[4:6]
    bank_name = get_bank_name_from_code(bank_code)
    
    rearranged = iban_clean[4:] + iban_clean[:4]
    numeric_iban = ''.join(iban_letter_to_number(c) for c in rearranged)
    
    if int(numeric_iban) % 97 == 1:
        return True, "✓ الـ IBAN صحيح", bank_name
    else:
        return False, "✗ الـ IBAN غير صحيح (Check Digits خاطئة)", bank_name

def add_to_history(iban):
    """Add IBAN to history (max 10 items)"""
    if iban not in iban_history:
        iban_history.insert(0, iban)
        if len(iban_history) > 10:
            iban_history.pop()
        update_history_listbox()

def update_history_listbox():
    """Update the history listbox display"""
    history_listbox.delete(0, tk.END)
    for iban in iban_history:
        history_listbox.insert(tk.END, iban)

def copy_from_history(event=None):
    """Copy selected IBAN from history"""
    selection = history_listbox.curselection()
    if selection:
        iban = history_listbox.get(selection[0])
        pyperclip.copy(iban.replace(" ", ""))
        show_toast("✓ تم النسخ من السجل")

def generate_iban(event=None):
    bank_name = bank_combo.get()
    if not bank_name:
        result_var.set("اختر البنك أولاً")
        return

    bank_code = banks[bank_name]
    account_number = ''.join(str(random.randint(0, 9)) for _ in range(18))
    check_digits = calculate_check_digits(bank_code, account_number)
    iban = f"SA{check_digits}{bank_code}{account_number}"
    formatted_iban = format_iban(iban)
    result_var.set(formatted_iban)
    add_to_history(formatted_iban)

def copy_to_clipboard(event=None):
    iban = result_var.get()
    if iban and "اختر" not in iban:
        pyperclip.copy(iban.replace(" ", ""))
        show_copy_feedback()

def show_copy_feedback():
    """Show temporary feedback when copied"""
    original_text = copy_btn.cget("text")
    copy_btn.config(text="✓ تم النسخ")
    root.after(1500, lambda: copy_btn.config(text=original_text))

def show_toast(message):
    """Show a temporary toast notification"""
    toast = tk.Toplevel(root)
    toast.overrideredirect(True)
    toast.attributes('-topmost', True)
    
    theme = DARK_THEME if is_dark_mode else LIGHT_THEME
    
    label = tk.Label(toast, text=message, font=("Arial", 11), 
                     bg=theme["success"], fg="white", padx=20, pady=10)
    label.pack()
    
    # Position toast at bottom center of main window
    root.update_idletasks()
    x = root.winfo_x() + (root.winfo_width() // 2) - 75
    y = root.winfo_y() + root.winfo_height() - 60
    toast.geometry(f"+{x}+{y}")
    
    root.after(1500, toast.destroy)

def validate_input(event=None):
    """Validate the IBAN entered in the validator field"""
    iban = validate_entry_var.get()
    if not iban.strip():
        validate_result_var.set("أدخل IBAN للتحقق")
        validate_result_label.config(foreground="gray")
        validate_bank_var.set("")
        return
    
    is_valid, message, bank_name = validate_iban(iban)
    theme = DARK_THEME if is_dark_mode else LIGHT_THEME
    validate_result_var.set(message)
    validate_result_label.config(foreground=theme["success"] if is_valid else theme["error"])
    
    if bank_name:
        validate_bank_var.set(f"🏦 البنك: {bank_name}")
    else:
        validate_bank_var.set("")

def toggle_theme():
    """Toggle between dark and light theme"""
    global is_dark_mode
    is_dark_mode = not is_dark_mode
    apply_theme()

def apply_theme():
    """Apply the current theme to all widgets"""
    theme = DARK_THEME if is_dark_mode else LIGHT_THEME
    
    # Update root and main frames
    root.configure(bg=theme["bg"])
    
    # Update ttk style
    style.configure("TFrame", background=theme["bg"])
    style.configure("TLabel", background=theme["bg"], foreground=theme["fg"])
    style.configure("TButton", background=theme["button_bg"])
    style.configure("TLabelframe", background=theme["bg"])
    style.configure("TLabelframe.Label", background=theme["bg"], foreground=theme["fg"])
    style.configure("TCombobox", fieldbackground=theme["entry_bg"], background=theme["entry_bg"])
    style.configure("TEntry", fieldbackground=theme["entry_bg"])
    
    # Update custom widgets
    history_listbox.configure(bg=theme["entry_bg"], fg=theme["fg"], 
                              selectbackground=theme["accent"], selectforeground="white")
    
    # Update theme button text
    theme_btn.config(text="☀️ وضع فاتح" if is_dark_mode else "🌙 وضع داكن")

def clear_history():
    """Clear all history"""
    iban_history.clear()
    update_history_listbox()

# ===== واجهة البرنامج =====
root = tk.Tk()
root.title("مولد IBAN سعودي")
root.geometry("500x800")
root.resizable(False, False)

# Style
style = ttk.Style()
style.theme_use('clam')

# ===== Header with Theme Toggle =====
header_frame = ttk.Frame(root)
header_frame.pack(fill="x", padx=15, pady=5)

app_title = ttk.Label(header_frame, text="🏦 مولد IBAN سعودي", font=("Arial", 14, "bold"))
app_title.pack(side="left")

theme_btn = ttk.Button(header_frame, text="🌙 وضع داكن", command=toggle_theme, width=12)
theme_btn.pack(side="right")

# ===== Generator Section =====
generator_frame = ttk.LabelFrame(root, text=" توليد IBAN ", padding=15)
generator_frame.pack(fill="x", padx=15, pady=10)

title = ttk.Label(generator_frame, text="اختر البنك:", font=("Arial", 11))
title.pack(pady=5)

bank_combo = ttk.Combobox(generator_frame, values=list(banks.keys()), font=("Arial", 11), state="readonly", width=30)
bank_combo.pack(pady=5)

# Buttons frame for generate + copy
btn_frame = ttk.Frame(generator_frame)
btn_frame.pack(pady=10)

generate_btn = ttk.Button(btn_frame, text="توليد IBAN ⏎", command=generate_iban, width=15)
generate_btn.pack(side="left", padx=5)

copy_btn = ttk.Button(btn_frame, text="نسخ 📋", command=copy_to_clipboard, width=12)
copy_btn.pack(side="left", padx=5)

result_var = tk.StringVar()
result_entry = ttk.Entry(generator_frame, textvariable=result_var, font=("Consolas", 14), justify="center", width=32)
result_entry.pack(pady=10)

# Keyboard shortcut hint
shortcut_label = ttk.Label(generator_frame, text="⌨️ Enter = توليد | Ctrl+C = نسخ", font=("Arial", 9), foreground="gray")
shortcut_label.pack()

# ===== History Section =====
history_frame = ttk.LabelFrame(root, text=" السجل (آخر 10) ", padding=10)
history_frame.pack(fill="x", padx=15, pady=10)

history_listbox = tk.Listbox(history_frame, font=("Consolas", 11), height=4, selectmode=tk.SINGLE)
history_listbox.pack(fill="x", pady=5)
history_listbox.bind("<Double-Button-1>", copy_from_history)

history_hint = ttk.Label(history_frame, text="انقر مرتين للنسخ", font=("Arial", 9), foreground="gray")
history_hint.pack()

clear_btn = ttk.Button(history_frame, text="مسح السجل", command=clear_history, width=12)
clear_btn.pack(pady=5)

# ===== Validator Section =====
validator_frame = ttk.LabelFrame(root, text=" التحقق من IBAN ", padding=15)
validator_frame.pack(fill="x", padx=15, pady=10)

validate_label = ttk.Label(validator_frame, text="أدخل IBAN للتحقق:", font=("Arial", 11))
validate_label.pack(pady=5)

validate_entry_var = tk.StringVar()
validate_entry = ttk.Entry(validator_frame, textvariable=validate_entry_var, font=("Consolas", 12), justify="center", width=32)
validate_entry.pack(pady=5)

validate_btn = ttk.Button(validator_frame, text="تحقق ✓", command=validate_input, width=12)
validate_btn.pack(pady=10)

validate_result_var = tk.StringVar()
validate_result_label = ttk.Label(validator_frame, textvariable=validate_result_var, font=("Arial", 11))
validate_result_label.pack(pady=5)

validate_bank_var = tk.StringVar()
validate_bank_label = ttk.Label(validator_frame, textvariable=validate_bank_var, font=("Arial", 11, "bold"))
validate_bank_label.pack(pady=2)

# ===== Keyboard Shortcuts =====
root.bind("<Return>", generate_iban)
root.bind("<Control-c>", copy_to_clipboard)
root.bind("<Control-C>", copy_to_clipboard)
validate_entry.bind("<Return>", validate_input)

# Apply initial theme
apply_theme()

root.mainloop()
