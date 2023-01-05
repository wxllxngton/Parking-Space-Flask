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

/* ----------------------------------------------------------- */
/*  SCROLL TO TOP BUTTON
  /* ----------------------------------------------------------- */
//Get the button
let mybutton = document.getElementById('btn-back-to-top');

// When the user scrolls down 20px from the top of the document, show the button
window.onscroll = function () {
    scrollFunction();
};

function scrollFunction() {
    if (
        document.body.scrollTop > 20 ||
        document.documentElement.scrollTop > 20
    ) {
        mybutton.style.display = 'block';
    } else {
        mybutton.style.display = 'none';
    }
}
// When the user clicks on the button, scroll to the top of the document
mybutton.addEventListener('click', backToTop);

function backToTop() {
    window.scrollTo({
        left: 0,
        top: 0,
        behavior: 'smooth',
    });
}

/* ----------------------------------------------------------- */
/*  COPYRIGHT YEAR
  /* ----------------------------------------------------------- */

document.querySelector('.copyright-year').textContent =
    new Date().getFullYear();

/* ----------------------------------------------------------- */
/*  FADE OUT LINK
  /* ----------------------------------------------------------- */

const navBar = document.querySelector('nav');
const handleHover = function (e) {
    if (e.target.classList.contains('nav-link')) {
        const link = e.target;
        const siblings = link.closest('nav').querySelectorAll('nav-link');
        const logo = link.closest('nav').querySelector('img');
        const navBrand = document.querySelectorAll('.navbar-brand');

        siblings.forEach((el) => {
            console.log(el);
            if (el !== link) el.style.opacity = this;
        });
        logo.style.opacity = this;
        navBrand.forEach((el) => (el.style.opacity = this));
    }
};

navBar.addEventListener('mouseover', handleHover.bind(0.5));
navBar.addEventListener('mouseout', handleHover.bind(1));
