// script.ts

// 1. Grab the elements from the HTML
const input = document.getElementById('billAmount') as HTMLInputElement | null;
const button = document.getElementById('calcBtn') as HTMLButtonElement | null;
const resultDisplay = document.getElementById('result') as HTMLSpanElement | null;

// 2. Validate elements exist
if (!input || !button || !resultDisplay) {
    console.error('Required HTML elements not found');
    throw new Error('Missing required HTML elements');
}

// 3. Define the logic
function calculateTotal(amount: number): number {
    const tip = amount * 0.15;
    return amount + tip;
}

// 4. Connect the logic to the button
button.addEventListener('click', () => {
    const value = parseFloat(input.value);

    // Validate input
    if (isNaN(value) || value < 0) {
        alert("Please enter a valid positive number!");
        resultDisplay.innerText = "0";
        return;
    }

    const finalTotal = calculateTotal(value);
    resultDisplay.innerText = finalTotal.toFixed(2);
});
input.addEventListener('keydown', (e) => {
    if (e.key === "Enter") {
        const value = parseFloat(input.value);
        
        if (isNaN(value) || value < 0) {
            alert("Please enter a valid positive number!");
            resultDisplay.innerText = "0";
            return;
        }
        
        const finalTotal = calculateTotal(value);
        resultDisplay.innerText = finalTotal.toFixed(2);
    }
});