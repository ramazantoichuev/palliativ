document.addEventListener('DOMContentLoaded', function () {
    const toggleBtn = document.getElementById('headerSearchToggle');
    const searchBar = document.getElementById('headerSearchBar');
    const searchInput = document.getElementById('headerSearchInput');

    if (!toggleBtn || !searchBar || !searchInput) return;

    function openSearch() {
        searchBar.classList.remove('d-none');
        toggleBtn.setAttribute('aria-expanded', 'true');
        searchInput.focus();
    }

    function closeSearch() {
        searchBar.classList.add('d-none');
        toggleBtn.setAttribute('aria-expanded', 'false');
    }

    toggleBtn.addEventListener('click', function (event) {
        event.stopPropagation();
        if (searchBar.classList.contains('d-none')) {
            openSearch();
        } else {
            closeSearch();
        }
    });

    document.addEventListener('click', function (event) {
        if (searchBar.classList.contains('d-none')) return;
        if (!searchBar.contains(event.target) && event.target !== toggleBtn) {
            closeSearch();
        }
    });
});