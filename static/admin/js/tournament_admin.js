document.addEventListener('DOMContentLoaded', function() {
    var typeField = document.getElementById('id_tournament_type');
    var schedulingField = document.getElementById('id_allow_player_scheduling');
    var resultsField = document.getElementById('id_allow_player_results');

    function checkKnockoutRule(event) {
        // If tournament type is knockout or it's implicitly a knockout form (if typeField is hidden/missing but it's KnockoutTournament)
        var isKnockout = false;
        if (typeField) {
            isKnockout = (typeField.value === 'knockout');
        } else {
            // Check body class or form to guess if it's knockout tournament admin
            if (document.body.classList.contains('model-knockouttournament')) {
                isKnockout = true;
            }
        }

        if (isKnockout && event.target.checked) {
            alert('Atenção: Para Torneio Eliminatório é melhor que o agendamento e lançamento de resultados sejam gerenciados pelo administrador. Esta opção será desativada.');
            event.target.checked = false;
        }
    }

    if (schedulingField) {
        schedulingField.addEventListener('change', checkKnockoutRule);
    }
    
    if (resultsField) {
        resultsField.addEventListener('change', checkKnockoutRule);
    }
    
    // Also run on type change
    if (typeField) {
        typeField.addEventListener('change', function() {
            if (typeField.value === 'knockout') {
                if (schedulingField && schedulingField.checked) {
                    alert('Atenção: Para Torneio Eliminatório é melhor que o agendamento e lançamento de resultados sejam gerenciados pelo administrador.');
                    schedulingField.checked = false;
                }
                if (resultsField && resultsField.checked) {
                    resultsField.checked = false;
                }
            }
        });
    }

    // Move TournamentFeeInline (taxas) right above fee_observation
    var feeObservationField = document.querySelector('.field-fee_observation');
    var allInlines = document.querySelectorAll('.inline-group');
    var feeInline = null;
    
    // Find the inline group whose h2 contains "Taxas de Inscrição"
    allInlines.forEach(function(inline) {
        var h2 = inline.querySelector('h2');
        if (h2 && h2.textContent.includes('Taxas de Inscrição')) {
            feeInline = inline;
        }
    });

    if (feeInline && feeObservationField) {
        feeObservationField.parentNode.insertBefore(feeInline, feeObservationField);
        // Tweak styles to look integrated within the fieldset
        feeInline.style.margin = '15px 0 20px 0';
        feeInline.style.boxShadow = 'none';
        feeInline.style.border = 'none';
        feeInline.style.padding = '0';
    }
});
