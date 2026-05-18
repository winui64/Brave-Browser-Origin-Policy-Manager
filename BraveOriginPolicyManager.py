import tkinter as tk
from tkinter import ttk, messagebox
import winreg
import ctypes
import sys

# =========================================================
# Brave Browser Origin Policy Editor
# =========================================================

REG_PATH = r"SOFTWARE\Policies\BraveSoftware\Brave"

POLICIES = {
    "BraveAIChatEnabled": 0,
    "BraveNewsDisabled": 1,
    "BraveP3AEnabled": 0,
    "BraveRewardsDisabled": 1,
    "BraveSpeedreaderEnabled": 0,
    "BraveStatsPingEnabled": 0,
    "BraveTalkDisabled": 1,
    "BraveVPNDisabled": 1,
    "BraveWalletDisabled": 1,
    "BraveWaybackMachineEnabled": 0,
    "BraveWebDiscoveryEnabled": 0,
    "TorDisabled": 1,
    "ExtensionManifestV2Availability": 2
}


# =========================================================
# Admin Check
# =========================================================

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(
        None,
        "runas",
        sys.executable,
        __file__,
        None,
        1
    )
    sys.exit()


# =========================================================
# Registry Functions
# =========================================================

def create_key():
    return winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, REG_PATH)


def set_policy(name, value):
    key = create_key()
    winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, value)
    winreg.CloseKey(key)


def delete_policy(name):
    try:
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            REG_PATH,
            0,
            winreg.KEY_SET_VALUE
        )
        winreg.DeleteValue(key, name)
        winreg.CloseKey(key)
    except FileNotFoundError:
        pass


def get_policy(name):
    try:
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            REG_PATH,
            0,
            winreg.KEY_READ
        )

        value, _ = winreg.QueryValueEx(key, name)
        winreg.CloseKey(key)
        return value

    except FileNotFoundError:
        return None


def remove_all_policies():
    for policy in POLICIES:
        delete_policy(policy)

    messagebox.showinfo(
        "Success",
        "All Brave policies have been removed."
    )

    refresh_ui()


# =========================================================
# GUI Logic
# =========================================================

policy_vars = {}


def apply_selected():
    try:
        for policy, data in policy_vars.items():

            enabled = data["enabled"].get()

            if enabled:
                set_policy(policy, data["value"])
            else:
                delete_policy(policy)

        messagebox.showinfo(
            "Success",
            "Selected policies have been applied."
        )

    except Exception as e:
        messagebox.showerror("Error", str(e))


def refresh_ui():
    for policy, data in policy_vars.items():

        current = get_policy(policy)

        if current is None:
            data["enabled"].set(False)
        else:
            data["enabled"].set(True)


# =========================================================
# GUI
# =========================================================

root = tk.Tk()
root.title("Brave Browser Origin Policy Editor")
root.geometry("550x650")
root.resizable(False, False)

title = ttk.Label(
    root,
    text="Brave Browser Origin Policy Editor",
    font=("Segoe UI", 16, "bold")
)
title.pack(pady=10)

frame = ttk.Frame(root)
frame.pack(fill="both", expand=True, padx=20, pady=10)

for policy, value in POLICIES.items():

    container = ttk.Frame(frame)
    container.pack(fill="x", pady=5)

    enabled_var = tk.BooleanVar()

    checkbox = ttk.Checkbutton(
        container,
        text=policy,
        variable=enabled_var
    )
    checkbox.pack(side="left")

    value_label = ttk.Label(
        container,
        text=f"DWORD = {value}"
    )
    value_label.pack(side="right")

    policy_vars[policy] = {
        "enabled": enabled_var,
        "value": value
    }

# Buttons
button_frame = ttk.Frame(root)
button_frame.pack(pady=15)

apply_btn = ttk.Button(
    button_frame,
    text="Apply Policies",
    command=apply_selected
)
apply_btn.grid(row=0, column=0, padx=10)

remove_btn = ttk.Button(
    button_frame,
    text="Remove All Policies",
    command=remove_all_policies
)
remove_btn.grid(row=0, column=1, padx=10)

refresh_btn = ttk.Button(
    button_frame,
    text="Refresh",
    command=refresh_ui
)
refresh_btn.grid(row=0, column=2, padx=10)

# Initial Load
refresh_ui()

root.mainloop()
