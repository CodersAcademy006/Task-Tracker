def toggle_theme(current_theme, root, style):
    if current_theme[0] == 'light':
        style.theme_use('clam')
        root.configure(bg='black')
        style.configure('.', background='black', foreground='white')
        style.configure('TLabel', background='black', foreground='white')
        style.configure('TButton', background='gray30', foreground='white')
        style.configure('TFrame', background='black')
        style.configure('TEntry', background='gray20', foreground='white')  # Added Entry field styling
        style.configure('TCombobox', background='gray20', foreground='white')  # Added Combobox styling
        current_theme[0] = 'dark'
    else:
        style.theme_use('default')
        root.configure(bg='SystemButtonFace')
        style.configure('.', background='SystemButtonFace', foreground='black')
        style.configure('TLabel', background='SystemButtonFace', foreground='black')
        style.configure('TButton', background='SystemButtonFace', foreground='black')
        style.configure('TFrame', background='SystemButtonFace')
        style.configure('TEntry', background='white', foreground='black')  # Reset Entry field styling
        style.configure('TCombobox', background='white', foreground='black')  # Reset Combobox styling
        current_theme[0] = 'light'
