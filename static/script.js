document.querySelector('.navbar-nav').addEventListener('click', function (e) {
    // console.log(e.currentTarget); // Parent element

    // 2. Determine what element orgianated the event
    // Matching strategy
    if (e.target.classList.contains('nav-real')) {
        e.preventDefault();

        document
            .querySelector(e.target.getAttribute('href'))
            .scrollIntoView({ behavior: 'smooth' });
    }
});
