# File: view.py (Standardized in camelCase, interface remains in Spanish)
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from PIL import Image, ImageTk
import datetime
import os
import sys
from uuid import uuid4
import calendar
import locale
from pathlib import Path
from tkcalendar import DateEntry

class ModernSalesApp:
    def __init__(self, root, viewModel):
        self.root = root
        self.viewModel = viewModel
        self.root.title("Gestión de Ventas")

        screenWidth, screenHeight = root.winfo_screenwidth(), root.winfo_screenheight()
        self.root.geometry(f"{int(screenWidth * 0.8)}x{int(screenHeight * 0.8)}")
        self.root.minsize(900, 600)
        self.root.configure(bg="#F8F8F8")

        self.primaryColor = "#7100B3"
        self.secondaryColor = "#BBBCC7"
        self.textColor = "#333333"
        self.searchPlaceholder = "Escribe el nombre del producto..."
        self.productById = {}

        self.baseFontSize = 14
        self.largeFontSize = 16
        self.titleFontSize = 18
        self.headerFontSize = 24

        self._setupStyles()

        currentDir = Path(__file__).resolve().parent
        imagePath = currentDir.parent / 'image' / 'Lupa.png'
        self.searchIcon = self._loadImage(imagePath, 20, 20)

        self.createWidgets()
        self.initializeDateFilters()
        self._setupLocale()

    def _setupStyles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TNotebook", background=self.root.cget('bg'), borderwidth=0)
        self.style.configure("TNotebook.Tab", background="#DDDDDD", foreground=self.textColor, font=('Arial', self.largeFontSize, 'bold'))
        self.style.map("TNotebook.Tab", background=[("selected", self.primaryColor)], foreground=[("selected", "white")])
        self.style.configure("TButton", font=('Arial', self.baseFontSize), background=self.primaryColor, foreground="white", borderwidth=0)
        self.style.map("TButton", background=[('active', '#5A0099')])
        self.style.configure("Treeview.Heading", font=('Arial', self.largeFontSize, 'bold'), background=self.primaryColor, foreground="white")
        self.style.configure("Treeview", font=('Arial', self.baseFontSize), rowheight=25)
        self.style.map("Treeview", background=[('selected', self.secondaryColor)], foreground=[('selected', self.textColor)])
        self.style.configure("TLabel", font=('Arial', self.baseFontSize), background=self.root.cget('bg'), foreground=self.textColor)
        self.style.configure("TEntry", font=('Arial', self.baseFontSize), fieldbackground="white", foreground=self.textColor)
        self.style.configure("TCombobox", font=('Arial', self.baseFontSize))
        self.style.configure("TLabelframe.Label", font=('Arial', self.titleFontSize, 'bold'), foreground=self.primaryColor)

    def _setupLocale(self):
        try:
            locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
        except locale.Error:
            try:
                locale.setlocale(locale.LC_TIME, 'Spanish_Spain.1252')
            except locale.Error:
                print("Advertencia: No se pudo establecer la configuración regional a español.")

    def _loadImage(self, path, width, height):
        try:
            return ImageTk.PhotoImage(Image.open(path).resize((width, height), Image.LANCZOS))
        except Exception as e:
            print(f"Error al cargar la imagen {path}: {e}")
            return None

    def showLoadingScreen(self):
        self.loading_window = tk.Toplevel(self.root)
        self.loading_window.title("Cargando...")
        parent_x, parent_y = self.root.winfo_x(), self.root.winfo_y()
        parent_w, parent_h = self.root.winfo_width(), self.root.winfo_height()
        self.loading_window.geometry(f"300x150+{parent_x + (parent_w - 300) // 2}+{parent_y + (parent_h - 150) // 2}")
        self.loading_window.transient(self.root)
        self.loading_window.grab_set()
        ttk.Label(self.loading_window, text="Cargando productos...", font=('Arial', self.largeFontSize, 'bold')).pack(pady=30)
        progressbar = ttk.Progressbar(self.loading_window, mode='indeterminate', length=200)
        progressbar.pack(pady=10)
        progressbar.start()
        self.root.update_idletasks()

    def onProductsLoaded(self):
        if hasattr(self, 'loading_window') and self.loading_window.winfo_exists():
            self.loading_window.destroy()
        messagebox.showinfo("Carga Completa", "Productos cargados correctamente.")
        self.root.deiconify()
        self.searchEntry.focus_set()

    def createWidgets(self):
        self.mainFrame = ttk.Frame(self.root, padding="10", style="TNotebook")
        self.mainFrame.pack(fill="both", expand=True)
        self.notebook = ttk.Notebook(self.mainFrame)
        self.notebook.pack(fill="both", expand=True)

        self.salesTab = ttk.Frame(self.notebook, style="TNotebook")
        self.notebook.add(self.salesTab, text="Registrar Venta")
        self.createSalesTabWidgets(self.salesTab)

        self.recordsTab = ttk.Frame(self.notebook, style="TNotebook")
        self.notebook.add(self.recordsTab, text="Revisar Registros")
        self.createRecordsTabWidgets(self.recordsTab)

    def createSalesTabWidgets(self, parentFrame):
        canvas = tk.Canvas(parentFrame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parentFrame, orient="vertical", command=canvas.yview)
        scrollableFrame = ttk.Frame(canvas)
        scrollWindow = canvas.create_window((0, 0), window=scrollableFrame, anchor="nw")

        def configureScrollRegion(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def configureFrameWidth(event):
            canvas.itemconfig(scrollWindow, width=event.width)

        scrollableFrame.bind("<Configure>", configureScrollRegion)
        canvas.bind("<Configure>", configureFrameWidth)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        dateFrame = ttk.LabelFrame(scrollableFrame, text="Fecha de Venta", padding="10")
        dateFrame.pack(fill="x", pady=10, padx=10)
        self.saleDateEntry = DateEntry(dateFrame, width=18, font=('Arial', self.largeFontSize),
                                       borderwidth=2, date_pattern='dd/mm/yyyy', locale='es_ES')
        self.saleDateEntry.pack()

        searchFrame = ttk.LabelFrame(scrollableFrame, text="Buscar Productos", padding="10")
        searchFrame.pack(fill="x", pady=10, padx=10)

        self.searchEntry = ttk.Entry(searchFrame, font=('Arial', self.largeFontSize))
        self.searchEntry.insert(0, self.searchPlaceholder)
        self.searchEntry.bind("<FocusIn>", self._clearPlaceholder)
        self.searchEntry.bind("<FocusOut>", self._addPlaceholder)
        self.searchEntry.bind("<KeyRelease>", self._onKeyRelease)
        self.searchEntry.pack(side="left", fill="x", expand=True, padx=(0, 5))

        searchButton = ttk.Button(searchFrame, text="Buscar",
                                  command=self._searchProductCommand,
                                  image=self.searchIcon, compound=tk.LEFT)
        searchButton.pack(side="left")

        self._createSuggestionsTree(scrollableFrame)
        self._createCurrentSaleTree(scrollableFrame)
        self._createSaleActions(scrollableFrame)

    def _createSuggestionsTree(self, parent):
        suggestionsFrame = ttk.Frame(parent)
        suggestionsFrame.pack(fill="x", pady=10, padx=10)

        self.suggestionsTree = ttk.Treeview(
            suggestionsFrame,
            columns=("descripcion", "precio", "cantidad"),
            show="headings",
            height=8,
            selectmode="extended"
        )
        self.suggestionsTree.heading("descripcion", text="Descripción")
        self.suggestionsTree.heading("precio", text="Costo Unitario")
        self.suggestionsTree.heading("cantidad", text="Cantidad")
        self.suggestionsTree.column("descripcion", width=500, minwidth=300)
        self.suggestionsTree.column("precio", width=150, minwidth=100, anchor=tk.E)
        self.suggestionsTree.column("cantidad", width=100, minwidth=80, anchor=tk.CENTER)
        self.suggestionsTree.bind("<Button-1>", self._toggleSelection)
        self.suggestionsTree.bind("<Double-1>", self._editQuantityCell)
        self.suggestionsTree.pack(side="top", fill="x", expand=True)

        ttk.Button(suggestionsFrame, text="Añadir Productos Seleccionados",
                   command=self._addSelectedProductsToSale).pack(pady=10)

    def _createCurrentSaleTree(self, parent):
        saleFrame = ttk.LabelFrame(parent, text="Productos en la Venta Actual", padding="10")
        saleFrame.pack(fill="both", expand=True, pady=10, padx=10)

        self.currentSaleTree = ttk.Treeview(
            saleFrame,
            columns=("id", "descripcion", "cantidad", "precio_unitario", "subtotal"),
            show="headings"
        )
        self.currentSaleTree.heading("id", text="ID")
        self.currentSaleTree.heading("descripcion", text="Descripción")
        self.currentSaleTree.heading("cantidad", text="Cantidad")
        self.currentSaleTree.heading("precio_unitario", text="P. Unitario")
        self.currentSaleTree.heading("subtotal", text="Subtotal")
        self.currentSaleTree.column("id", width=0, stretch=tk.NO)
        self.currentSaleTree.column("cantidad", anchor=tk.CENTER)
        self.currentSaleTree.pack(fill="both", expand=True, side="left")

        scrollbar = ttk.Scrollbar(saleFrame, orient="vertical", command=self.currentSaleTree.yview)
        scrollbar.pack(side="right", fill="y")
        self.currentSaleTree.configure(yscrollcommand=scrollbar.set)

        self.currentSaleItems = {}

    def _createSaleActions(self, parent):
        actionFrame = ttk.Frame(parent, padding="10")
        actionFrame.pack(fill="x", pady=10, padx=10)
        ttk.Label(actionFrame, text="Total:",
                  font=('Arial', self.headerFontSize, 'bold')).pack(side="left", padx=10)
        self.totalLabel = ttk.Label(actionFrame, text="$0.00",
                                    font=('Arial', self.headerFontSize, 'bold'),
                                    foreground=self.primaryColor)
        self.totalLabel.pack(side="left", fill="x", expand=True)

        ttk.Button(actionFrame, text="Quitar Producto", command=self._removeSelectedFromSale).pack(side="right", padx=5)
        ttk.Button(actionFrame, text="Vaciar Venta", command=self._clearSale).pack(side="right", padx=5)
        ttk.Button(actionFrame, text="Confirmar Venta", command=self._confirmSale).pack(side="right", padx=5)

    def _searchProductCommand(self):
        query = self.searchEntry.get()
        if query == self.searchPlaceholder:
            query = ""
        self.viewModel.searchFullProductsAsync(query, self._updateSuggestionsTree)

    def _onKeyRelease(self, event):
        if len(self.searchEntry.get()) >= 2:
            self.viewModel.searchAutocompleteSuggestionsAsync(self.searchEntry.get(), self._updateSuggestionsTree)
        else:
            self.suggestionsTree.delete(*self.suggestionsTree.get_children())

    def _clearPlaceholder(self, event):
        if self.searchEntry.get() == self.searchPlaceholder:
            self.searchEntry.delete(0, tk.END)
            self.searchEntry.config(foreground=self.textColor)

    def _addPlaceholder(self, event):
        if not self.searchEntry.get():
            self.searchEntry.insert(0, self.searchPlaceholder)
            self.searchEntry.config(foreground="grey")

    def _toggleSelection(self, event):
        itemId = self.suggestionsTree.identify_row(event.y)
        if not itemId:
            return
        if itemId in self.suggestionsTree.selection():
            self.suggestionsTree.selection_remove(itemId)
        else:
            self.suggestionsTree.selection_add(itemId)
        return "break"

    def _editQuantityCell(self, event):
        if self.suggestionsTree.identify_region(event.x, event.y) != "cell":
            return
        columnId = self.suggestionsTree.identify_column(event.x)
        if columnId != "#3":
            return
        itemId = self.suggestionsTree.identify_row(event.y)
        if not itemId:
            return
        x, y, width, height = self.suggestionsTree.bbox(itemId, columnId)
        currentValue = self.suggestionsTree.set(itemId, columnId)
        entry = ttk.Entry(self.suggestionsTree)
        entry.place(x=x, y=y, width=width, height=height)
        entry.insert(0, currentValue)
        entry.select_range(0, 'end')
        entry.focus_set()
        entry.bind("<FocusOut>", lambda e: self._saveEditedQuantity(e, itemId, columnId))
        entry.bind("<Return>", lambda e: self._saveEditedQuantity(e, itemId, columnId))
        entry.bind("<Escape>", lambda e: e.widget.destroy())

    def _saveEditedQuantity(self, event, itemId, columnId):
        newValue = event.widget.get()
        event.widget.destroy()
        try:
            if int(newValue) > 0:
                self.suggestionsTree.set(itemId, columnId, newValue)
            else:
                messagebox.showwarning("Cantidad Inválida", "La cantidad debe ser mayor a 0.", parent=self.root)
        except ValueError:
            messagebox.showerror("Error de Formato", "La cantidad debe ser un número entero.", parent=self.root)

    def _addSelectedProductsToSale(self):
        selectedIds = self.suggestionsTree.selection()
        if not selectedIds:
            messagebox.showwarning("Sin Selección", "Selecciona productos de la lista de búsqueda primero.",
                                   parent=self.root)
            return
        for itemId in selectedIds:
            try:
                product = self.productById.get(itemId)
                quantity = int(self.suggestionsTree.set(itemId, "cantidad"))
                if product and quantity > 0:
                    self._addItemToSale(product, quantity)
            except (ValueError, TypeError) as e:
                print(f"Error processing item {itemId}: {e}")
        self.suggestionsTree.selection_remove(selectedIds)
        self._updateCurrentSaleTree()

    def _addItemToSale(self, product, quantity):
        key = product['Descripcion'].lower()
        if key in self.currentSaleItems:
            self.currentSaleItems[key]['cantidad'] += quantity
        else:
            self.currentSaleItems[key] = {
                "id": key,
                "producto": product,
                "cantidad": quantity,
                "precio_unitario": float(product.get('Costo', 0.0))
            }

    def _updateSuggestionsTree(self, suggestions):
        self.suggestionsTree.delete(*self.suggestionsTree.get_children())
        self.productById = {}
        for product in suggestions:
            uniqueId = str(uuid4())
            self.productById[uniqueId] = product

            rawPrice = product.get('Costo', '0').strip()
            try:
                price = float(rawPrice) if rawPrice else 0.0
            except ValueError:
                price = 0.0

            values = (
                product['Descripcion'],
                f"${price:.2f}",
                1
            )
            self.suggestionsTree.insert("", "end", iid=uniqueId, values=values)


    def _updateCurrentSaleTree(self):
        self.currentSaleTree.delete(*self.currentSaleTree.get_children())
        total = 0.0
        for key, item in self.currentSaleItems.items():
            subtotal = item['cantidad'] * item['precio_unitario']
            values = (
                item['id'],
                item['producto']['Descripcion'],
                item['cantidad'],
                f"${item['precio_unitario']:.2f}",
                f"${subtotal:.2f}"
            )
            self.currentSaleTree.insert("", "end", iid=key, values=values)
            total += subtotal
        self.totalLabel.config(text=f"${total:.2f}")

    def _removeSelectedFromSale(self):
        selectedIds = self.currentSaleTree.selection()
        if not selectedIds:
            messagebox.showwarning("Selección", "Selecciona productos para quitar.", parent=self.root)
            return
        for itemId in selectedIds:
            if itemId in self.currentSaleItems:
                del self.currentSaleItems[itemId]
        self._updateCurrentSaleTree()

    def _clearSale(self):
        self.currentSaleItems = {}
        self._updateCurrentSaleTree()

    def _confirmSale(self):
        if not self.currentSaleItems:
            messagebox.showwarning("Venta Vacía", "No hay productos en la venta actual.", parent=self.root)
            return
        saleDate = self.saleDateEntry.get_date()
        items = list(self.currentSaleItems.values())
        success, message = self.viewModel.registerSale(items, saleDate)
        if success:
            messagebox.showinfo("Venta Registrada", message, parent=self.root)
            self._clearSale()
        else:
            messagebox.showerror("Error al Registrar Venta", message, parent=self.root)

    def createRecordsTabWidgets(self, parentFrame):

        records_labelframe = ttk.LabelFrame(parentFrame, text="Registros de Ventas por Mes", padding="10")
        records_labelframe.pack(fill="both", expand=True, pady=(10, 10))
        filter_frame = ttk.Frame(records_labelframe, padding="10", style="TNotebook")
        filter_frame.pack(fill="x", pady=(0, 10))
        ttk.Label(filter_frame, text="Año:", font=('Arial', self.baseFontSize)).pack(side="left", padx=5)
        self.anio_seleccion = ttk.Combobox(filter_frame, font=('Arial', self.baseFontSize), width=6, state="readonly")
        self.anio_seleccion.pack(side="left", padx=5)
        ttk.Label(filter_frame, text="Mes:", font=('Arial', self.baseFontSize)).pack(side="left", padx=5)
        self.mes_seleccion = ttk.Combobox(filter_frame, font=('Arial', self.baseFontSize), width=12, state="readonly")
        self.mes_seleccion.pack(side="left", padx=5)
        ttk.Button(filter_frame, text="Cargar Registros", command=self.load_records_command).pack(side="left", padx=10)
        self.records_tree = ttk.Treeview(records_labelframe, columns=("id", "fecha", "rfc", "descripcion", "categoria", "cantidad", "costo_unitario"), show="headings")
        self.records_tree.heading("id", text="ID Interno")
        self.records_tree.heading("fecha", text="Fecha")
        self.records_tree.heading("rfc", text="RFC")
        self.records_tree.heading("descripcion", text="Descripción")
        self.records_tree.heading("categoria", text="Categoría")
        self.records_tree.heading("cantidad", text="Cantidad")
        self.records_tree.heading("costo_unitario", text="Costo Unitario")
        self.records_tree.column("id", width=0, stretch=tk.NO)
        self.records_tree.bind("<Double-1>", self.edit_selected_record)
        self.records_tree.pack(fill="both", expand=True)
        records_scrollbar = ttk.Scrollbar(records_labelframe, orient="vertical", command=self.records_tree.yview)
        records_scrollbar.pack(side="right", fill="y")
        self.records_tree.configure(yscrollcommand=records_scrollbar.set)

    def initializeDateFilters(self):
        current_year = datetime.datetime.now().year
        self.anio_seleccion['values'] = [str(y) for y in range(current_year - 5, current_year + 2)]
        self.anio_seleccion.set(str(current_year))
        self.mes_seleccion['values'] = [calendar.month_name[i].capitalize() for i in range(1, 13)]
        self.mes_seleccion.set(datetime.datetime.now().strftime('%B').capitalize())

    def _clear_placeholder(self, event):
        if self.search_entry.get() == self.SEARCH_PLACEHOLDER:
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(foreground=self.textColor)

    def _add_placeholder(self, event):
        if not self.search_entry.get():
            self.search_entry.insert(0, self.SEARCH_PLACEHOLDER)
            self.search_entry.config(foreground="grey")

    def _on_key_release(self, event):
        if len(self.search_entry.get()) >= 2:
            self.viewmodel.buscar_sugerencias_autocompletado_async(self.search_entry.get(), self.update_suggestions_tree)
        else:
            self.suggestions_tree.delete(*self.suggestions_tree.get_children())

    def search_product_button_command(self):
        query = self.search_entry.get()
        if query == self.SEARCH_PLACEHOLDER: query = ""
        self.viewmodel.buscar_productos_completa_async(query, self.update_suggestions_tree)
        
    def load_records_command(self):
        anio = self.anio_seleccion.get()
        mes = self.mes_seleccion.get().lower()
        if not anio or not mes:
            messagebox.showwarning("Filtro Incompleto", "Por favor, selecciona tanto el año como el mes.", parent=self.root)
            return
        self.viewmodel.cargar_registros_async(anio, mes, self.update_records_tree)

    def update_records_tree(self, records):
        self.records_tree.delete(*self.records_tree.get_children())
        if not records:
            messagebox.showinfo("Sin Registros", "No se encontraron registros para el mes y año seleccionados.", parent=self.root)
            return
        for record in records:
            self.records_tree.insert("", "end", iid=record.get('id'), values=(
                record.get('id', 'N/A'), record.get('fecha', 'N/A'), record.get('RFC', 'N/A'),
                record.get('descripcion', 'N/A'), record.get('categoria', 'N/A'), record.get('cantidad', 'N/A'),
                f"${float(record.get('costo_unitario', 0.0)):.2f}"
            ))

    def edit_selected_record(self, event):
        selected_item_id = self.records_tree.focus()
        if not selected_item_id: return
        datos_registro = self.records_tree.item(selected_item_id, 'values')
        editor = RecordEditorDialog(self.root, self.viewmodel, self, selected_item_id, datos_registro)
        self.root.wait_window(editor.top)
        self.load_records_command()

class RecordEditorDialog(simpledialog.Dialog):
    def __init__(self, parent, viewmodel, main_view, venta_id, datos):
        self.viewmodel = viewmodel
        self.main_view = main_view
        self.venta_id = venta_id
        self.datos = datos
        super().__init__(parent, "Editar Registro de Venta")

    def body(self, master):
        tk.Label(master, text="Descripción:", font=('Arial', self.main_view.baseFontSize)).grid(row=0, column=0, sticky="w", padx=5, pady=2)
        tk.Label(master, text="Cantidad:", font=('Arial', self.main_view.baseFontSize)).grid(row=1, column=0, sticky="w", padx=5, pady=2)
        tk.Label(master, text="Costo Unitario:", font=('Arial', self.main_view.baseFontSize)).grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.desc_entry = tk.Entry(master, width=40, font=('Arial', self.main_view.baseFontSize))
        self.cant_entry = tk.Entry(master, width=15, font=('Arial', self.main_view.baseFontSize))
        self.costo_entry = tk.Entry(master, width=15, font=('Arial', self.main_view.baseFontSize))
        self.desc_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        self.cant_entry.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        self.costo_entry.grid(row=2, column=1, sticky="w", padx=5, pady=2)
        self.desc_entry.insert(0, self.datos[3])
        self.cant_entry.insert(0, self.datos[5])
        costo_limpio = self.datos[6].replace("$", "").strip()
        self.costo_entry.insert(0, costo_limpio)
        return self.desc_entry

    def apply(self):
        try:
            descripcion = self.desc_entry.get()
            cantidad = int(self.cant_entry.get())
            costo = float(self.costo_entry.get())
            if not descripcion or cantidad <= 0 or costo < 0:
                messagebox.showerror("Datos Inválidos", "Por favor, verifica que todos los campos sean correctos.", parent=self)
                return
        except ValueError:
            messagebox.showerror("Error de Formato", "La cantidad y el costo deben ser números válidos.", parent=self)
            return
        datos_actualizados = {'descripcion': descripcion, 'cantidad': cantidad, 'costo_unitario': costo}
        anio = self.main_view.anio_seleccion.get()
        mes = self.main_view.mes_seleccion.get().lower()
        exito, mensaje = self.viewmodel.actualizar_registro(anio, mes, self.venta_id, datos_actualizados)
        if exito:
            messagebox.showinfo("Éxito", "El registro ha sido actualizado.", parent=self.main_view)
        else:
            messagebox.showerror("Error", f"No se pudo actualizar el registro: {mensaje}", parent=self.main_view)