/* ----------------------------------------------------------- */
/*  SCROLL INTO VIEW
  /* ----------------------------------------------------------- */

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

/* ----------------------------------------------------------- */
/*  LOADER
  /* ----------------------------------------------------------- */

var loader;

function loadNow(opacity) {
    if (opacity <= 0) {
        displayContent();
    } else {
        loader.style.opacity = opacity;
        window.setTimeout(function () {
            loadNow(opacity - 0.18);
        }, 50);
    }
}

function displayContent() {
    loader.style.display = 'none';
    document.getElementById('content').style.display = 'block';
}

document.addEventListener('DOMContentLoaded', function () {
    loader = document.getElementById('loader');
    loadNow(1);
});
