# GSTORE 🛒 - Point of Sale System for Small Retail Businesses

**GSTORE** is a desktop application built in Python using Tkinter. It is designed to help small retail stores (e.g., convenience stores) register sales, search products efficiently, and organize monthly reports in CSV format.

> The graphical user interface (GUI) is in Spanish for accessibility to local users, while the source code and documentation are written in English for maintainability and community contributions.

---

## 🚀 Features

- 🔎 **Smart product search** with autocomplete and fuzzy matching
- 🛒 **Sale registration** with date selection
- 📁 **Sales saved in monthly CSV files**, automatically sorted by date
- 📊 **Record viewer and editor** for monthly sales
- ⚡ **Asynchronous loading** of large product lists (tested with 150,000+ entries)
- ✅ Designed using the **MVVM pattern** for better separation of concerns

---

## 🧱 Technologies Used

- Python 3.10+
- Tkinter & ttk
- [tkcalendar](https://github.com/j4321/tkcalendar)
- Pillow (for image rendering)
- CSV (as local storage backend)

---

## 📦 Installation

### 1. Clone this repository

```bash
git clone https://github.com/YourUser/GSTORE.git
cd GSTORE


GSTORE/
├── model.py                  # Business logic: product search, CSV storage
├── view.py                   # GUI: product search, sales UI (in Spanish)
├── viewmodel.py              # Logic between GUI and model
├── main.py                   # Application entry point
├── productos-de-supermercados-main/
│   └── consolidado_ventas_unicos.csv  # Product catalog
├── image/
│   └── Lupa.png              # Search icon
└── ventasTienda/             # Auto-generated: monthly sales files saved here
