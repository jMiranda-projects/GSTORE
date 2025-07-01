import tkinter as tk
from viewmodel import ProductViewModel
from view import ModernSalesApp

if __name__ == "__main__":
    root = tk.Tk()

    # Initialize the ViewModel
    viewModel = ProductViewModel()

    # Initialize the View and inject the ViewModel
    app = ModernSalesApp(root, viewModel)

    # Link back the ViewModel to the View
    viewModel.app = app

    # Show the loading screen and begin async product loading
    app.showLoadingScreen()
    viewModel.startAsyncProductLoading()

    # Start main loop
    root.mainloop()
