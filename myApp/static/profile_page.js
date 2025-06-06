document.addEventListener('DOMContentLoaded', function () {
    const editButton = document.getElementById('editButton');
    const saveButton = document.getElementById('saveButton');

    const fields = [
        { textId: 'firstNameText', inputId: 'firstNameInput' },
        { textId: 'lastNameText', inputId: 'lastNameInput' },
        { textId: 'phoneText', inputId: 'phoneInput' },
    ];

    editButton.addEventListener('click', function () {
        fields.forEach(field => {
            document.getElementById(field.textId).classList.add('d-none');
            document.getElementById(field.inputId).classList.remove('d-none');
        });

        editButton.classList.add('d-none');
        saveButton.classList.remove('d-none');
    });
});