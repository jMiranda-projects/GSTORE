from model import ProductModel
import threading

class ProductViewModel:
    def __init__(self):
        self.model = ProductModel()
        self.app = None  # Reference to the view to trigger UI updates
        self.loadingProductsFlag = False
        self.lastSearchId = 0

    def startAsyncProductLoading(self):
        """Starts product loading in a background thread."""
        if not self.loadingProductsFlag and not self.model.productsLoaded:
            self.loadingProductsFlag = True
            loadingThread = threading.Thread(target=self._loadProductsInThread)
            loadingThread.daemon = True
            loadingThread.start()

    def _loadProductsInThread(self):
        """Loads products and triggers UI update on completion."""
        self.model.loadProducts()
        self.loadingProductsFlag = False
        if self.app:
            self.app.root.after(0, self.app.onProductsLoaded)

    def searchAutocompleteSuggestionsAsync(self, query, callback):
        """Starts an autocomplete suggestion search in a separate thread."""
        suggestionThread = threading.Thread(target=self._searchSuggestionsInThread, args=(query, callback))
        suggestionThread.daemon = True
        suggestionThread.start()

    def _searchSuggestionsInThread(self, query, callback):
        """Performs prefix-based search and returns suggestions."""
        results = self.model.searchSuggestionsByPrefix(query)
        if self.app and callback:
            self.app.root.after(0, callback, results)

    def searchFullProductsAsync(self, query, callback):
        """Starts a full product search in a separate thread."""
        searchThread = threading.Thread(target=self._searchFullProductsInThread, args=(query, callback))
        searchThread.daemon = True
        searchThread.start()

    def _searchFullProductsInThread(self, query, callback):
        """Performs full product matching based on the query string."""
        results = self.model.fullProductSearch(query)
        if self.app and callback:
            self.app.root.after(0, callback, results)

    def registerSale(self, soldItems, saleDate):
        """
        Sends a request to register a sale with its selected date.
        Returns (success: bool, message: str).
        """
        if not soldItems:
            return False, "No products selected for sale."
        return self.model.registerSale(soldItems, saleDate)

    def loadSalesRecordsAsync(self, year, month, callback):
        """Starts asynchronous loading of sales records for a specific month/year."""
        loadThread = threading.Thread(target=self._loadSalesRecordsInThread, args=(year, month, callback))
        loadThread.daemon = True
        loadThread.start()

    def _loadSalesRecordsInThread(self, year, month, callback):
        """Loads sales records and returns them via callback."""
        results = self.model.loadMonthlySalesRecords(year, month)
        if self.app and callback:
            self.app.root.after(0, callback, results)

    def updateRecord(self, year, month, saleId, updatedData):
        """
        Updates a specific record in the corresponding monthly CSV.
        Returns (success: bool, message: str).
        """
        return self.model.updateRecord(year, month, saleId, updatedData)
