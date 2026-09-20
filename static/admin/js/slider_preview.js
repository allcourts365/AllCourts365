document.addEventListener("DOMContentLoaded", function() {
    const rangeInputs = document.querySelectorAll('input[type="range"]');
    
    rangeInputs.forEach(input => {
        let valDisplay = document.createElement('span');
        valDisplay.style.marginLeft = '10px';
        valDisplay.style.fontWeight = 'bold';
        valDisplay.style.color = '#fff';
        
        // Append it after the input
        input.parentNode.appendChild(valDisplay);
        
        const updateDisplay = () => {
            valDisplay.textContent = input.value + '%';
        };
        
        // Initial set
        updateDisplay();
        
        // Update on change
        input.addEventListener('input', updateDisplay);
    });
});
