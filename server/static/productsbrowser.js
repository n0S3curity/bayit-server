document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const productsContainer = document.getElementById('productsContainer');
    const searchInput = document.getElementById('searchInput');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const emptyListMessage = document.getElementById('emptyListMessage');
    const sidebar = document.getElementById('sidebar');
    const hamburgerIcon = document.getElementById('hamburgerIcon');

    // Real Barcode Scanner Elements
    const barcodeScannerBtn = document.getElementById('barcodeScannerBtn');
    const barcodeModal = document.getElementById('barcodeModal');
    const closeBarcodeModalBtn = document.getElementById('closeBarcodeModal');
    const interactiveViewport = document.getElementById('interactive');
    const scannerFrame = document.getElementById('scannerFrame');

    let allProducts = [];

    // --- Utility Functions ---

    function showLoading() {
        loadingSpinner.style.display = 'block';
        productsContainer.innerHTML = '';
        emptyListMessage.classList.add('hidden');
    }

    function hideLoading() {
        loadingSpinner.style.display = 'none';
    }

    function showEmptyMessage() {
        emptyListMessage.classList.remove('hidden');
    }

    // A utility function to show messages, required by barcode_scanner.js for error feedback.
    function showMessage(message, level = 'info') {
        if (level === 'error') {
            console.error(message);
            // You can replace this with a more sophisticated toast notification
            alert(`שגיאה: ${message}`);
        } else {
            console.log(message);
        }
    }


    // --- Data Fetching and Rendering ---

    async function fetchProducts() {
        showLoading();
        try {
            const response = await fetch('/api/productsbrowser');
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            const data = await response.json();
            allProducts = Object.values(data); // Convert object to array
            renderProducts(allProducts);
        } catch (error) {
            console.error('Failed to fetch products:', error);
            productsContainer.innerHTML = `<p class="text-center text-red-500">שגיאה בטעינת המוצרים. אנא נסה שנית מאוחר יותר.</p>`;
        } finally {
            hideLoading();
        }
    }

    function renderProducts(products) {
        productsContainer.innerHTML = '';
        if (products.length === 0 && searchInput.value.trim() !== '') {
            showEmptyMessage();
            return;
        }
        emptyListMessage.classList.add('hidden');

        products.forEach(product => {
            const productCard = document.createElement('div');
            productCard.className = 'product-card bg-white p-4 rounded-lg shadow-sm border border-gray-200';
            productCard.innerHTML = `
                <div class="product-details flex-grow flex items-center">
                    <svg class="w-6 h-6 text-gray-500 ml-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4"></path></svg>
                    <div class="text-right">
                        <p class="text-xl font-bold text-gray-800">${product.name}</p>
                        <p class="text-sm text-gray-500 mt-1">ברקוד: ${product.barcode}</p>
                        <p class="text-lg font-bold text-indigo-500 mt-2">מחיר ממוצע: ₪${product.price.toFixed(2)}</p>
                    </div>
                </div>
                <div class="product-actions flex space-x-2 rtl:space-x-reverse flex-shrink-0">
                    <a href="/stats/${product.barcode}" class="p-2 rounded-full text-indigo-600 hover:bg-indigo-100 transition-colors duration-200" title="סטטיסטיקות"><svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z"></path></svg></a>
                    <a href="/product/${product.barcode}/settings" class="p-2 rounded-full text-gray-600 hover:bg-gray-200 transition-colors duration-200" title="הגדרות"><svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37h.001a1.724 1.724 0 002.572-1.065z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path></svg></a>
                </div>
            `;
            productsContainer.appendChild(productCard);
        });
    }

    function filterProducts(query) {
        const normalizedQuery = query.trim().toLowerCase();
        if (!normalizedQuery) {
            renderProducts(allProducts);
            return;
        }
        const filteredProducts = allProducts.filter(product => {
            const nameMatch = product.name.toLowerCase().includes(normalizedQuery);
            const barcodeMatch = product.barcode.includes(normalizedQuery);
            return nameMatch || barcodeMatch;
        });
        renderProducts(filteredProducts);
    }

    // --- Barcode Scanner Logic ---

    // This is the callback function executed when the scanner successfully detects a barcode.
    const onBarcodeDetected = (barcode) => {
        console.log("Barcode detected on products page:", barcode);
        searchInput.value = barcode; // Put the scanned code into the search bar
        stopBarcodeScanner(); // Stop the camera
        barcodeModal.style.display = 'none'; // Hide the modal
        filterProducts(barcode); // Trigger the search with the new barcode
        searchInput.focus();
    };

    // Function to close the modal and stop the scanner
    const closeScannerModal = () => {
        stopBarcodeScanner();
        barcodeModal.style.display = 'none';
    };


    // --- Event Listeners ---

    hamburgerIcon.addEventListener('click', () => {
        sidebar.classList.toggle('open');
    });

    searchInput.addEventListener('input', (event) => {
        filterProducts(event.target.value);
    });

    // Open the scanner modal and start the camera
    barcodeScannerBtn.addEventListener('click', () => {
        barcodeModal.style.display = 'flex';
        // Delay scanner start to allow modal transition animation to complete
        setTimeout(() => {
            // This function is in barcode_scanner.js
            startBarcodeScanner(interactiveViewport, scannerFrame, onBarcodeDetected);
        }, 300);
    });

    // Close the scanner modal with the 'X' button
    closeBarcodeModalBtn.addEventListener('click', closeScannerModal);

    // Close modal if user clicks on the background overlay
    window.addEventListener('click', (event) => {
        if (event.target === barcodeModal) {
            closeScannerModal();
        }
    });

    // --- Initial Load ---
    fetchProducts();
});