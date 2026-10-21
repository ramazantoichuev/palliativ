document.addEventListener('DOMContentLoaded', function () {
    const toggleBtns = document.querySelectorAll('.js-search-toggle');
    const searchBar = document.getElementById('headerSearchBar');
    const searchInput = document.getElementById('headerSearchInput');

    if (!toggleBtns.length || !searchBar || !searchInput) return;

    function setExpanded(value) {
        toggleBtns.forEach(function (btn) {
            btn.setAttribute('aria-expanded', value);
        });
    }

    function openSearch() {
        searchBar.classList.remove('d-none');
        setExpanded('true');
        searchInput.focus();
    }

    function closeSearch() {
        searchBar.classList.add('d-none');
        setExpanded('false');
    }

    toggleBtns.forEach(function (btn) {
        btn.addEventListener('click', function (event) {
            event.stopPropagation();
            if (searchBar.classList.contains('d-none')) {
                openSearch();
            } else {
                closeSearch();
            }
        });
    });

    document.addEventListener('click', function (event) {
        if (searchBar.classList.contains('d-none')) return;
        const onToggle = Array.from(toggleBtns).some(function (btn) {
            return btn.contains(event.target);
        });
        if (!searchBar.contains(event.target) && !onToggle) {
            closeSearch();
        }
    });
});