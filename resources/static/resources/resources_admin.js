document.addEventListener('DOMContentLoaded', function () {
    const audienceSelect = document.getElementById('id_audience');
    const subcategorySelect = document.getElementById('id_subcategory');

    if (!audienceSelect || !subcategorySelect) return;

    const subcategories = {
        'specialist': [
            { value: 'symptom_control', text: 'Контроль симптомов' },
            { value: 'end_of_life_care', text: 'Уход в конце жизни' },
            { value: 'npa', text: 'НПА (Нормативно-правовые акты)' }
        ],
        'caregiver': [
            { value: 'care_feeding', text: 'Уход и кормление' },
            { value: 'psychologist_tips', text: 'Советы психолога' },
            { value: 'meds_rights', text: 'Лекарства и права пациента' },
            { value: 'social_support', text: 'Соцподдержка' }
        ]
    };

    function updateSubcategories() {
        const selectedAudience = audienceSelect.value;
        const currentSubcategory = subcategorySelect.value;
        subcategorySelect.innerHTML = '<option value="">---------</option>';

        if (selectedAudience && subcategories[selectedAudience]) {
            subcategories[selectedAudience].forEach(sub => {
                const option = document.createElement('option');
                option.value = sub.value;
                option.text = sub.text;
                if (sub.value === currentSubcategory) {
                    option.selected = true;
                }
                subcategorySelect.appendChild(option);
            });
        }
    }
    audienceSelect.addEventListener('change', updateSubcategories);
    updateSubcategories();
});