        document.addEventListener('DOMContentLoaded', () => {
            const receiptsContainer = document.getElementById('receiptsContainer');
            const emptyListMessage = document.getElementById('emptyListMessage');
            const loadingSpinner = document.getElementById('loadingSpinner');
            const sidebar = document.getElementById('sidebar');
            const hamburgerIcon = document.getElementById('hamburgerIcon');
            const addReceiptBtn = document.getElementById('addReceiptBtn');
            const addReceiptModal = document.getElementById('addReceiptModal');
            const closeModalBtn = document.getElementById('closeModalBtn');
            const pasteArea = document.getElementById('pasteArea');
            const linksListContainer = document.getElementById('linksListContainer');
            const successToast = document.getElementById('successToast');
            const successMessage = document.getElementById('successMessage');

            // --- Mock Data with Supermarket, Branch, Date/Time, and Amount ---
            const mockReceiptsData = [
                { supermarketName: "אושר עד", branchName: "ירושלים", transactionId: "TID-001", date: "2024-07-25", time: "11:30", amount: 150.75, downloadLink: "#", showLink: "https://placehold.co/800x600/E9E9F0/3F3F46?text=Receipt+1" },
                { supermarketName: "יוחננוף", branchName: "תל אביב", transactionId: "TID-002", date: "2024-07-26", time: "14:00", amount: 250.00, downloadLink: "#", showLink: "https://placehold.co/800x600/E9E9F0/3F3F46?text=Receipt+2" },
                { supermarketName: "אושר עד", branchName: "ירושלים", transactionId: "TID-003", date: "2024-07-27", time: "18:15", amount: 320.50, downloadLink: "#", showLink: "https://placehold.co/800x600/E9E9F0/3F3F46?text=Receipt+3" },
                { supermarketName: "אושר עד", branchName: "חיפה", transactionId: "TID-004", date: "2024-07-27", time: "15:45", amount: 185.30, downloadLink: "#", showLink: "https://placehold.co/800x600/E9E9F0/3F3F46?text=Receipt+4" },
                { supermarketName: "יוחננוף", branchName: "תל אביב", transactionId: "TID-005", date: "2024-07-28", time: "10:00", amount: 450.10, downloadLink: "#", showLink: "https://placehold.co/800x600/E9E9F0/3F3F46?text=Receipt+5" },
                { supermarketName: "אושר עד", branchName: "חיפה", transactionId: "TID-006", date: "2024-07-28", time: "19:20", amount: 50.00, downloadLink: "#", showLink: "https://placehold.co/800x600/E9E9F0/3F3F46?text=Receipt+6" },
                { supermarketName: "יוחננוף", branchName: "רחובות", transactionId: "TID-007", date: "2024-07-29", time: "09:00", amount: 75.90, downloadLink: "#", showLink: "https://placehold.co/800x600/E9E9F0/3F3F46?text=Receipt+7" },
                { supermarketName: "יוחננוף", branchName: "תל אביב", transactionId: "TID-008", date: "2024-07-29", time: "17:40", amount: 125.00, downloadLink: "#", showLink: "https://placehold.co/800x600/E9E9F0/3F3F46?text=Receipt+8" }
            ];

            // --- Utility Functions ---

            function showLoading() {
                loadingSpinner.style.display = 'block';
                receiptsContainer.innerHTML = '';
                emptyListMessage.classList.add('hidden');
            }

            function hideLoading() {
                loadingSpinner.style.display = 'none';
            }

            function showEmptyMessage() {
                emptyListMessage.classList.remove('hidden');
            }

            // Function to show a temporary success toast
            function showSuccessToast(message) {
                successMessage.textContent = message;
                successToast.classList.add('show');
                setTimeout(() => {
                    successToast.classList.remove('show');
                }, 3000); // Hide after 3 seconds
            }

            // Function to sort receipts by date and time, newest first
            function sortReceipts(receipts) {
                return receipts.sort((a, b) => {
                    const dateA = new Date(`${a.date}T${a.time}`);
                    const dateB = new Date(`${b.date}T${b.time}`);
                    return dateB - dateA; // Sort descending
                });
            }

            // Function to render the receipts with nested grouping
            function renderReceipts(receipts) {
                if (receipts.length === 0) {
                    showEmptyMessage();
                    return;
                }
                emptyListMessage.classList.add('hidden');
                receiptsContainer.innerHTML = '';

                // First, sort the entire list of receipts by date and time
                const sortedReceipts = sortReceipts(receipts);

                // Group receipts by supermarket
                const groupedBySupermarket = sortedReceipts.reduce((acc, receipt) => {
                    const { supermarketName } = receipt;
                    if (!acc[supermarketName]) {
                        acc[supermarketName] = [];
                    }
                    acc[supermarketName].push(receipt);
                    return acc;
                }, {});

                // Sort supermarkets alphabetically
                const sortedSupermarkets = Object.keys(groupedBySupermarket).sort();

                sortedSupermarkets.forEach(supermarketName => {
                    const supermarketReceipts = groupedBySupermarket[supermarketName];

                    // Create supermarket header
                    const supermarketHeader = document.createElement('div');
                    supermarketHeader.className = 'supermarket-header text-xl font-semibold text-gray-700 hover:bg-gray-400 transition-colors duration-200';
                    supermarketHeader.dataset.supermarketName = supermarketName;
                    supermarketHeader.innerHTML = `
                        <div class="supermarket-title-wrapper">
                            <span>${supermarketName} (${supermarketReceipts.length})</span>
                        </div>
                        <div class="flex items-center">
                            <svg class="w-5 h-5 collapse-arrow" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                            </svg>
                        </div>
                    `;
                    receiptsContainer.appendChild(supermarketHeader);

                    const supermarketContent = document.createElement('div');
                    supermarketContent.className = 'supermarket-content space-y-4 pt-2 border-r-2 border-gray-400';
                    supermarketContent.classList.add('hidden'); // Initially collapsed
                    receiptsContainer.appendChild(supermarketContent);

                    // Group by branch within the current supermarket
                    const groupedByBranch = supermarketReceipts.reduce((acc, receipt) => {
                        const { branchName } = receipt;
                        if (!acc[branchName]) {
                            acc[branchName] = [];
                        }
                        acc[branchName].push(receipt);
                        return acc;
                    }, {});

                    // Sort branches alphabetically
                    const sortedBranches = Object.keys(groupedByBranch).sort();

                    sortedBranches.forEach(branchName => {
                        const branchReceipts = groupedByBranch[branchName];

                        // Create branch header
                        const branchHeader = document.createElement('div');
                        branchHeader.className = 'branch-header text-lg font-semibold text-gray-700 hover:bg-gray-200 transition-colors duration-200';
                        branchHeader.dataset.branchName = branchName;
                        branchHeader.innerHTML = `
                            <div class="branch-title-wrapper">
                                <span>${branchName} (${branchReceipts.length})</span>
                            </div>
                            <div class="flex items-center">
                                <svg class="w-5 h-5 collapse-arrow" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                                </svg>
                            </div>
                        `;
                        supermarketContent.appendChild(branchHeader);

                        // Create container for receipts within this branch
                        const branchContent = document.createElement('div');
                        branchContent.className = 'branch-content space-y-4 pr-4 border-r-2 border-indigo-400';
                        branchContent.dataset.branchName = branchName;
                        branchContent.classList.add('hidden'); // Initially collapsed
                        supermarketContent.appendChild(branchContent);

                        // Add receipts to the branch container
                        branchReceipts.forEach(receipt => {
                            const receiptCard = createReceiptCard(receipt);
                            branchContent.appendChild(receiptCard);
                        });

                        // Attach click listener to the branch header to toggle collapse
                        branchHeader.addEventListener('click', () => {
                            const isHidden = branchContent.classList.toggle('hidden');
                            branchHeader.classList.toggle('collapsed');
                            if (!isHidden) {
                                branchHeader.scrollIntoView({ behavior: 'smooth', block: 'center' });
                            }
                        });
                    });

                    // Attach click listener to the supermarket header to toggle collapse
                    supermarketHeader.addEventListener('click', () => {
                        const isHidden = supermarketContent.classList.toggle('hidden');
                        supermarketHeader.classList.toggle('collapsed');
                        // Optional: Collapse all branches when supermarket is collapsed
                        if (isHidden) {
                            supermarketContent.querySelectorAll('.branch-content').forEach(el => el.classList.add('hidden'));
                            supermarketContent.querySelectorAll('.branch-header').forEach(el => el.classList.add('collapsed'));
                        }
                        if (!isHidden) {
                            supermarketHeader.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        }
                    });
                });
            }

            // Function to create a single receipt card
            function createReceiptCard(receipt) {
                const card = document.createElement('div');
                card.className = 'receipt-card bg-white p-4 rounded-lg shadow-sm border border-gray-200';
                card.innerHTML = `
                    <div class="receipt-details">
                        <!-- Receipt Icon (inline SVG) -->
                        <svg class="w-6 h-6 text-gray-500 ml-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                        </svg>
                        <div>
                            <p class="font-semibold text-gray-800">מספר קבלה: ${receipt.transactionId}</p>
                            <p class="text-sm text-gray-500">
                                <span class="ml-2">${receipt.supermarketName} - ${receipt.branchName}</span>
                                <span class="ml-2">|</span>
                                <span class="ml-2">${receipt.date}</span>
                                <span class="ml-2">${receipt.time}</span>
                            </p>
                            <p class="text-lg font-bold text-green-600 mt-2">₪${receipt.amount.toFixed(2)}</p>
                        </div>
                    </div>
                    <div class="receipt-actions flex space-x-2">
                        <button class="show-btn p-2 rounded-full text-indigo-600 hover:bg-indigo-100 transition-colors duration-200" data-link="${receipt.showLink}">
                            <!-- Show Icon (inline SVG) -->
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                            </svg>
                        </button>
                        <button class="download-btn p-2 rounded-full text-green-600 hover:bg-green-100 transition-colors duration-200" data-link="${receipt.downloadLink}">
                            <!-- Download Icon (inline SVG) -->
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
                            </svg>
                        </button>
                    </div>
                `;

                // Add event listeners for the buttons
                card.querySelector('.show-btn').addEventListener('click', (e) => {
                    e.preventDefault();
                    window.open(e.currentTarget.dataset.link, '_blank');
                });
                card.querySelector('.download-btn').addEventListener('click', (e) => {
                    e.preventDefault();
                    console.log(`Downloading receipt: ${e.currentTarget.dataset.link}`);
                });

                return card;
            }

            // Function to extract URLs from a string
            function extractLinks(text) {
                const urlRegex = /(https?:\/\/[^\s]+)/g;
                const matches = text.match(urlRegex);
                return matches ? [...new Set(matches)] : []; // Return unique links
            }

            // Function to render extracted links in the modal
            function renderLinks(links) {
                linksListContainer.innerHTML = ''; // Clear previous links
                if (links.length === 0) {
                    linksListContainer.innerHTML = '<p class="text-center text-gray-500">לא נמצאו קישורים.</p>';
                    return;
                }

                const ul = document.createElement('ul');
                ul.className = 'space-y-2 text-sm';
                links.forEach(link => {
                    const li = document.createElement('li');
                    li.className = 'flex items-center justify-between p-2 bg-gray-100 rounded-lg';
                    li.innerHTML = `
                        <span class="text-gray-700 truncate">${link}</span>
                        <button class="choose-btn bg-indigo-500 text-white px-4 py-2 rounded-lg hover:bg-indigo-600 transition-colors duration-200" data-url="${link}">
                            בחר
                        </button>
                    `;
                    ul.appendChild(li);
                });
                linksListContainer.appendChild(ul);
            }

            // Function to simulate API call to fetch receipt
            async function fetchReceipt(url) {
                // Simulate API request
                console.log(`Simulating API call to fetch receipt from: ${url}`);
                try {
                    // Simulating a network request delay
                    await new Promise(resolve => setTimeout(resolve, 1500));

                    // You would replace this with a real fetch call:
                    /*
                    const response = await fetch('/api/fetchReceipt', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ url: url })
                    });
                    const result = await response.json();
                    if (result.success) {
                        showSuccessToast('הקבלה נקלטה בהצלחה!');
                    } else {
                        // Handle error message
                        console.error('API Error:', result.message);
                    }
                    */

                    // For now, just show a success message
                    showSuccessToast('הקבלה נקלטה בהצלחה!');
                    console.log('API call successful.');

                } catch (error) {
                    console.error('Error fetching receipt:', error);
                    // You might want to show an error message here
                }
            }


            // --- API Simulation Function ---

            async function fetchReceipts() {
                showLoading();
                await new Promise(resolve => setTimeout(resolve, 1000));

                const data = mockReceiptsData;

                hideLoading();
                renderReceipts(data);
            }

            // --- Event Listeners ---

            hamburgerIcon.addEventListener('click', () => {
                sidebar.classList.toggle('open');
            });

            addReceiptBtn.addEventListener('click', () => {
                addReceiptModal.classList.remove('hidden');
                pasteArea.value = ''; // Clear text area on open
                linksListContainer.innerHTML = ''; // Clear links list
            });

            closeModalBtn.addEventListener('click', () => {
                addReceiptModal.classList.add('hidden');
            });

            // Close modal if user clicks outside of it
            window.addEventListener('click', (event) => {
                if (event.target === addReceiptModal) {
                    addReceiptModal.classList.add('hidden');
                }
            });

            pasteArea.addEventListener('input', (event) => {
                const text = event.target.value;
                const links = extractLinks(text);
                renderLinks(links);
            });

            linksListContainer.addEventListener('click', (event) => {
                if (event.target.classList.contains('choose-btn')) {
                    const url = event.target.dataset.url;
                    if (url) {
                        addReceiptModal.classList.add('hidden'); // Close modal
                        fetchReceipt(url); // Call the API
                    }
                }
            });

            // Initial fetch of receipts
            fetchReceipts();
        });
