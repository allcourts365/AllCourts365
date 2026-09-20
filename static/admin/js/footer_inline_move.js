document.addEventListener('DOMContentLoaded', function () {
    // Acha o fieldset 'Rodape (Footer)'
    var fieldsets = document.querySelectorAll('fieldset');
    var footerFieldset = null;
    for (var i = 0; i < fieldsets.length; i++) {
        var h2 = fieldsets[i].querySelector('h2');
        if (h2 && h2.textContent.trim().includes('Rodap')) {
            footerFieldset = fieldsets[i];
            break;
        }
    }

    // Acha o grupo inline
    var inlineGroup = document.querySelector('#footerlink_set-group');

    if (footerFieldset && inlineGroup) {
        // Esconde o cabecalho azul do inline
        var inlineTitle = inlineGroup.querySelector('h2');
        if (inlineTitle) {
            inlineTitle.style.display = 'none';
        }
        // Muda a aparencia do inline para parecer parte do fieldset
        inlineGroup.style.margin = '15px 0 0 0';
        inlineGroup.style.border = 'none';
        inlineGroup.style.boxShadow = 'none';
        // Move para dentro do fieldset
        footerFieldset.appendChild(inlineGroup);
    }
});
