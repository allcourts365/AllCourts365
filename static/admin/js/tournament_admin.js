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

    // Logic for CategoryInline (use_limited_registrations -> max_players)
    function toggleMaxPlayers(row) {
        var checkbox = row.querySelector('input[name$="-use_limited_registrations"]');
        var maxPlayersInput = row.querySelector('input[name$="-max_players"]');
        if (checkbox && maxPlayersInput) {
            maxPlayersInput.disabled = !checkbox.checked;
            if (!checkbox.checked) {
                maxPlayersInput.value = '';
                maxPlayersInput.title = 'Ative a opção ao lado para usar limite de inscritos';
            } else {
                maxPlayersInput.title = '';
            }
        }
    }

    function initCategoryRows() {
        var categoryRows = document.querySelectorAll('.inline-related.tabular table tbody tr.form-row, .inline-group[id="categories-group"] .inline-related');
        categoryRows.forEach(function(row) {
            // Only apply if this row belongs to categories
            var checkbox = row.querySelector('input[name^="categories-"][name$="-use_limited_registrations"]');
            if (checkbox) {
                toggleMaxPlayers(row);
                // Remove existing listener to prevent duplicates if called multiple times
                var newCheckbox = checkbox.cloneNode(true);
                checkbox.parentNode.replaceChild(newCheckbox, checkbox);
                newCheckbox.addEventListener('change', function() {
                    toggleMaxPlayers(row);
                });
            }
        });
    }

    initCategoryRows();

    if (typeof django !== 'undefined' && django.jQuery) {
        django.jQuery(document).on('formset:added', function(event, $row, formsetName) {
            if (formsetName === 'categories') {
                initCategoryRows();
            }
        });
    }
});
