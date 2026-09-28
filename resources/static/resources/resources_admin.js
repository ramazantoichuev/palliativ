(function () {
    const mapping = {
        'specialist': ['symptom_control', 'end_of_life_care', 'npa'],
        'caregiver': ['symptom_control', 'care_feeding', 'psychologist_tips', 'meds_rights', 'social_support'],
        'pediatric': ['care_feeding', 'psychologist_tips', 'meds_rights', 'social_support', 'symptom_control', 'end_of_life_care', 'npa']
    };
    function applyDropdownVisibilityFilter() {
        const jq = window.django ? window.django.jQuery : window.jQuery;
        if (!jq) return;

        const audienceField = jq('select[id^="id_audience"]');
        const subcategoryField = jq('select[id^="id_subcategory"]');

        const selectedAudience = audienceField.val();
        if (!selectedAudience) return;
        const allowedKeys = mapping[selectedAudience] || [];
        const select2Options = jq('.select2-container--open .select2-results__option');

        if (select2Options.length > 0) {
            select2Options.each(function () {
                const item = jq(this);
                const currentText = item.text().trim();
                let itemKey = null;
                const itemData = item.data('data');
                if (itemData && itemData.id) {
                    itemKey = itemData.id;
                } else {
                    const originalOption = subcategoryField.find('option').filter(function() {
                        return jq(this).text().trim() === currentText;
                    });
                    if (originalOption.length) {
                        itemKey = originalOption.val();
                    }
                }
                // Выбранное значение не прячем: в базе есть пары вне маппинга,
                // скрытие ломало бы редактирование существующих ресурсов.
                if (itemKey && itemKey !== "" && itemKey !== subcategoryField.val()) {
                    if (allowedKeys.indexOf(itemKey) === -1) {
                        item.attr('style', 'display: none !important;');
                        item.removeClass('select2-results__option--highlighted');
                    }
                }
            });
        }
    }
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.addedNodes && mutation.addedNodes.length > 0) {
                for (let i = 0; i < mutation.addedNodes.length; i++) {
                    const node = mutation.addedNodes[i];
                    if (node.nodeType === 1 && (node.classList.contains('select2-container--open') || node.querySelector('.select2-results'))) {
                        const jq = window.django ? window.django.jQuery : window.jQuery;
                        if (jq) {
                            const activeSelect = jq('.select2-container--open').prev('select');
                            if (activeSelect.length && activeSelect.attr('id') && activeSelect.attr('id').indexOf('id_subcategory') === 0) {
                                applyDropdownVisibilityFilter();
                            }
                        }
                    }
                }
            }
        });
    });
    document.addEventListener('DOMContentLoaded', () => {
        observer.observe(document.body, { childList: true, subtree: true });
    });
    if (document.body) {
        observer.observe(document.body, { childList: true, subtree: true });
    }
    document.addEventListener('keyup', (event) => {
        if (event.target && event.target.classList.contains('select2-search__field')) {
            setTimeout(applyDropdownVisibilityFilter, 10);
        }
    }, true);
})();
