document.addEventListener("DOMContentLoaded", function() {
    if (typeof jQuery !== 'undefined') {
        // Para selects normais (sem select2): O evento original garante que foi um clique de usuário real
        jQuery('#changelist-search select, .changelist-filter select').on('change', function(e) {
            if (e.originalEvent) {
                var form = jQuery(this).closest('form');
                if (form.length > 0) {
                    form.submit();
                }
            }
        });

        // Para selects com Select2 do Jazzmin: usar o evento específico select2:select
        // Ele não dispara no carregamento inicial, apenas quando o usuário faz uma escolha real
        jQuery('#changelist-search select, .changelist-filter select').on('select2:select', function(e) {
            var form = jQuery(this).closest('form');
            if (form.length > 0) {
                form.submit();
            }
        });
    }
});
