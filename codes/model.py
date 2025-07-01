import csv
import difflib
from pathlib import Path
from collections import defaultdict
import locale
from uuid import uuid4
import os
import sys

class ProductModel:
    def __init__(self):
        try:
            locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
        except locale.Error:
            try:
                locale.setlocale(locale.LC_TIME, 'Spanish_Spain.1252')
            except locale.Error:
                print("Warning: Could not set locale to Spanish.")

        homeDir = Path.home()
        documentsPath = homeDir / 'Documents'
        self.salesDirPath = documentsPath / 'ventasTienda'
        self.salesDirPath.mkdir(parents=True, exist_ok=True)

        if getattr(sys, 'frozen', False):
            baseDir = Path(sys._MEIPASS) / 'productos-de-supermercados-main'
        else:
            baseDir = Path(__file__).resolve().parent.parent / 'productos-de-supermercados-main'

        self.productsCsvPath = baseDir / 'consolidado_ventas_unicos.csv'

        self.products = []
        self.productsLoaded = False
        self.nameToProduct = {}
        self.prefixIndex = defaultdict(list)

    def loadProducts(self):
        print("Loading products from CSV...")
        tempProducts = []
        tempNameToProduct = {}
        tempPrefixIndex = defaultdict(list)
        try:
            with open(self.productsCsvPath, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    cleanRow = {key.strip(): value for key, value in row.items()}
                    if '\ufeffRFC' in cleanRow:
                        cleanRow['RFC'] = cleanRow.pop('\ufeffRFC')
                    product = cleanRow
                    tempProducts.append(product)
                    nameLower = product['Descripcion'].lower()
                    tempNameToProduct[nameLower] = product
                    for i in range(1, len(nameLower) + 1):
                        prefix = nameLower[:i]
                        tempPrefixIndex[prefix].append(product)
            self.products = tempProducts
            self.nameToProduct = tempNameToProduct
            self.prefixIndex = tempPrefixIndex
            self.productsLoaded = True
            print(f"Products loaded and indexed: {len(self.products)}")
        except FileNotFoundError:
            print(f"Error: CSV file not found at {self.productsCsvPath}")
        except Exception as e:
            print(f"Error while loading products: {e}")

    def searchSuggestionsByPrefix(self, query):
        if not self.productsLoaded:
            return []
        query = query.strip().lower()
        if not query:
            return []
        suggestions = self.prefixIndex.get(query, [])
        seenNames = set()
        uniqueProducts = []
        for product in suggestions:
            if product['Descripcion'] not in seenNames:
                seenNames.add(product['Descripcion'])
                uniqueProducts.append(product)
        return uniqueProducts[:10]

    def fullProductSearch(self, query):
        if not self.productsLoaded:
            return []
        queryLower = query.strip().lower()
        if not queryLower:
            return []
        results = []
        addedNames = set()

        if queryLower in self.nameToProduct:
            exact = self.nameToProduct[queryLower]
            if exact['Descripcion'].lower() not in addedNames:
                results.append(exact)
                addedNames.add(exact['Descripcion'].lower())

        queryWords = set(queryLower.split())
        if queryWords:
            for product in self.products:
                nameLower = product['Descripcion'].lower()
                if nameLower in addedNames:
                    continue
                nameWords = set(nameLower.split())
                if queryWords.issubset(nameWords):
                    results.append(product)
                    addedNames.add(nameLower)

        if not results:
            allNames = [p['Descripcion'].lower() for p in self.products]
            matches = difflib.get_close_matches(queryLower, allNames, n=5, cutoff=0.7)
            for match in matches:
                if match not in addedNames:
                    results.append(self.nameToProduct[match])
                    addedNames.add(match)
        return results

    def _getCsvPathByMonth(self, year, monthName):
        filename = f"ventas_{monthName.lower()}_{year}_gemma_app.csv"
        return self.salesDirPath / filename

    def registerSale(self, soldItems, saleDate):
        csvPath = self._getCsvPathByMonth(saleDate.year, saleDate.strftime('%B'))
        headers = ["id", "fecha", "RFC", "descripcion", "categoria", "cantidad", "costo_unitario"]
        existingRecords = []

        if csvPath.exists():
            try:
                with open(csvPath, mode='r', newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    existingRecords = list(reader)
            except Exception as e:
                return False, f"Failed to read existing sales file: {e}"

        dateStr = saleDate.strftime("%Y-%m-%d")
        for item in soldItems:
            product = item.get('producto', {})
            newRow = {
                'id': str(uuid4()),
                'fecha': dateStr,
                'RFC': product.get('RFC', 'N/A'),
                'descripcion': product.get('Descripcion', 'N/A'),
                'categoria': product.get('NOMBRE', 'N/A'),
                'cantidad': item.get('cantidad', 0),
                'costo_unitario': item.get('precio_unitario', 0.0)
            }
            existingRecords.append(newRow)

        try:
            existingRecords.sort(key=lambda x: x.get('fecha', ''))
        except Exception as e:
            return False, f"Could not sort records by date: {e}"

        try:
            with open(csvPath, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                writer.writerows(existingRecords)
            print(f"Sale saved and sorted successfully in: {csvPath}")
            return True, "Sale registered successfully."
        except Exception as e:
            return False, f"Error saving updated sales file: {e}"

    def loadMonthlySalesRecords(self, year, monthName):
        csvPath = self._getCsvPathByMonth(year, monthName)
        if not csvPath.exists():
            return []
        try:
            with open(csvPath, mode='r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                return list(reader)
        except Exception as e:
            print(f"Error loading records from {csvPath}: {e}")
            return []

    def updateRecord(self, year, monthName, saleId, updatedData):
        csvPath = self._getCsvPathByMonth(year, monthName)
        if not csvPath.exists():
            return False, f"No file found for {monthName} {year}."
        try:
            with open(csvPath, mode='r', newline='', encoding='utf-8') as f:
                records = list(csv.DictReader(f))

            updated = False
            fieldNames = records[0].keys() if records else []
            for record in records:
                if record['id'] == saleId:
                    record['descripcion'] = updatedData['descripcion']
                    record['cantidad'] = str(updatedData['cantidad'])
                    record['costo_unitario'] = str(updatedData['costo_unitario'])
                    updated = True
                    break

            if not updated:
                return False, f"Sale with ID {saleId} not found."

            records.sort(key=lambda x: x.get('fecha', ''))

            with open(csvPath, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldNames)
                writer.writeheader()
                writer.writerows(records)

            return True, "Record updated successfully."
        except Exception as e:
            return False, f"Error updating record: {e}"
