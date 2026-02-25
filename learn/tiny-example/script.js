// script.ts
// 1. Grab the elements from the HTML
var input = document.getElementById('billAmount');
var button = document.getElementById('calcBtn');
var resultDisplay = document.getElementById('result');
// 2. Validate elements exist
if (!input || !button || !resultDisplay) {
    console.error('Required HTML elements not found');
    throw new Error('Missing required HTML elements');
}
// 3. Define the logic
function calculateTotal(amount) {
    var tip = amount * 0.15;
    return amount + tip;
}
// 4. Connect the logic to the button
button.addEventListener('click', function () {
    var value = parseFloat(input.value);
    // Validate input
    if (isNaN(value) || value < 0) {
        alert("Please enter a valid positive number!");
        resultDisplay.innerText = "0";
        return;
    }
    var finalTotal = calculateTotal(value);
    resultDisplay.innerText = finalTotal.toFixed(2);
});
input.addEventListener('keydown', function (e) {
    if (e.key === "Enter") {
        var value = parseFloat(input.value);
        if (isNaN(value) || value < 0) {
            alert("Please enter a valid positive number!");
            resultDisplay.innerText = "0";
            return;
        }
        var finalTotal = calculateTotal(value);
        resultDisplay.innerText = finalTotal.toFixed(2);
    }
});
