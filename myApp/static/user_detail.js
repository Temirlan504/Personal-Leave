document.addEventListener('DOMContentLoaded', function () {
    const editBtn = document.getElementById('edit-btn');
    const saveBtn = document.getElementById('save-btn');
    const cancelBtn = document.getElementById('cancel-btn');

    const displayFields = document.querySelectorAll(
        '#first-name-display, #last-name-display, #email-display, #phone-display, #role-display, #salary-display, #date-display'
    );
    const inputFields = document.querySelectorAll(
        '#first-name-input, #last-name-input, #email-input, #phone-input, #role-input, #salary-input, #date-input'
    );

    editBtn.addEventListener('click', function () {
        displayFields.forEach(el => el.classList.add('d-none'));
        inputFields.forEach(el => el.classList.remove('d-none'));

        editBtn.classList.add('d-none');
        saveBtn.classList.remove('d-none');
        cancelBtn.classList.remove('d-none');
    });

    cancelBtn.addEventListener('click', function () {
        window.location.reload();
    });
});
