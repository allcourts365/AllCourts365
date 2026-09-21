document.addEventListener('DOMContentLoaded', function() {
    function toggleFields() {
        const isStaffCheckbox = document.querySelector('#id_is_staff');
        const adminTypeSelect = document.querySelector('#id_admin_type');
        
        if (!isStaffCheckbox || !adminTypeSelect) return;

        const isStaff = isStaffCheckbox.checked;
        const adminType = adminTypeSelect.value;
        
        // Find the form rows for the custom fields
        const adminTypeRow = adminTypeSelect.closest('.form-row');
        
        const managedClubSelect = document.querySelector('#id_managed_club');
        const managedClubRow = managedClubSelect ? managedClubSelect.closest('.form-row') : null;
        
        const managedDeptSelect = document.querySelector('#id_managed_department');
        const managedDeptRow = managedDeptSelect ? managedDeptSelect.closest('.form-row') : null;

        if (isStaff) {
            if (adminTypeRow) adminTypeRow.style.display = '';
            
            if (adminType === 'clube') {
                if (managedClubRow) managedClubRow.style.display = '';
                if (managedDeptRow) managedDeptRow.style.display = 'none';
            } else if (adminType === 'departamento') {
                if (managedClubRow) managedClubRow.style.display = 'none';
                if (managedDeptRow) managedDeptRow.style.display = '';
            } else {
                if (managedClubRow) managedClubRow.style.display = 'none';
                if (managedDeptRow) managedDeptRow.style.display = 'none';
            }
        } else {
            if (adminTypeRow) adminTypeRow.style.display = 'none';
            if (managedClubRow) managedClubRow.style.display = 'none';
            if (managedDeptRow) managedDeptRow.style.display = 'none';
        }
    }

    const isStaffCheckbox = document.querySelector('#id_is_staff');
    const adminTypeSelect = document.querySelector('#id_admin_type');
    
    if (isStaffCheckbox) {
        isStaffCheckbox.addEventListener('change', toggleFields);
    }
    
    if (adminTypeSelect) {
        adminTypeSelect.addEventListener('change', toggleFields);
    }
    
    // Initial call
    toggleFields();
});
