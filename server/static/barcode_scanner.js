// barcode_scanner.js
// This script handles the barcode scanning functionality using QuaggaJS.

let isScanning = false;
let lastCode = null; // To store the last scanned barcode and prevent duplicates

/**
 * Starts the barcode scanner.
 * @param {HTMLElement} viewport The HTML element to render the video stream into.
 * @param {HTMLElement} frame The HTML element to use as a visual frame.
 * @param {Function} onDetected The callback function to execute when a barcode is detected.
 */
function startBarcodeScanner(viewport, frame, onDetected) {
    if (isScanning) {
        console.log("Scanner is already running.");
        return;
    }

    // Reset the last scanned code
    lastCode = null;

    Quagga.init({
        inputStream: {
            name: "Live",
            type: "LiveStream",
            target: viewport,
            constraints: {
                width: { min: 640 },
                height: { min: 480 },
                facingMode: "environment" // Use the back camera
            },
        },
        locator: {
            patchSize: "large", // Use a larger patch size for better detection
            halfSample: true,
            patchCanvasSize: "small" // Improves decoding performance
        },
        decoder: {
            readers: ["ean_reader", "upc_reader", "ean_8_reader", "upc_e_reader"], // Specify barcode types
            debug: {
                showCanvas: false,
                drawBoundingBox: true,
                drawScanline: false
            }
        },
        frequency: 5, // Slow down the scanning frequency for better accuracy
        numOfWorkers: 2, // Use 2 workers for balanced performance
    }, function(err) {
        if (err) {
            console.error("Error initializing Quagga:", err);
            showMessage("שגיאה בפתיחת המצלמה. אנא ודא שהרשאה ניתנה.", 'error');
            return;
        }
        console.log("QuaggaJS initialized successfully. Starting...");
        Quagga.start();
        isScanning = true;
    });

    // This event is triggered when a barcode is detected.
    Quagga.onDetected(function(result) {
        if (!isScanning) return; // Prevent scanning after it's stopped

        const barcode = result.codeResult.code;

        // Check for a minimum length to avoid false positives
        if (barcode && barcode.length >= 8 && barcode !== lastCode) {
            console.log("Barcode detected:", barcode);
            lastCode = barcode;

            // Flash the green frame for feedback
            frame.classList.add('scanning-success');
            setTimeout(() => {
                frame.classList.remove('scanning-success');
            }, 500);

            onDetected(barcode);
            stopBarcodeScanner();
        }
    });
}

/**
 * Stops the barcode scanner and releases the camera stream.
 */
function stopBarcodeScanner() {
    if (isScanning) {
        Quagga.stop();
        isScanning = false;
        lastCode = null;
        console.log("QuaggaJS stopped.");
        const scannerFrame = document.getElementById('scannerFrame');
        if (scannerFrame) {
            scannerFrame.classList.remove('scanning-success');
        }
    }
}
