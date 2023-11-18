const navbtn = document.getElementById('nav-btn');
const navinput = document.getElementById('nav-input');
const headtext = document.getElementById('head-text');
const headtext2 = document.getElementById('head-text2');
const headerinput = document.getElementById('header-input');
const search_form = document.getElementById('search-form');
const nav_search_form = document.querySelectorAll('.nav-search-form');

const cngNavElemets = (e) => {
    navbtn.innerText = e
    if (navbtn.innerText == 'Company') {
        //nav_search_form.action = '/search-address'
        nav_search_form.forEach((e) => {
            e.action = '/search-address'
        })
    } else {
        //nav_search_form.action = '/search-employee'
        nav_search_form.forEach((e) => {
            e.action = '/search-employee'
        })
    }
}
const cngHeadText = () => {
    if (headtext2.innerText == 'Find your perfect Company today!') {
        headtext2.innerText = 'Find your perfect Employee today!'
        headerinput.placeholder = 'Enter company name'
        search_form.action = '/search-address'
    }
    else {
        headtext2.innerText = 'Find your perfect Company today!'
        headerinput.placeholder = 'Enter Employee name'
        search_form.action = '/search-employee'
    }

}

// check if search-address in url
const url = window.location.href;
if (url.includes('search-address')) {
    cngNavElemets('Address')
}

const accordionSidebar = document.querySelector('#accordionSidebar');
if (window.innerWidth > 768) {
    accordionSidebar.classList.remove('toggled');
}

const select_style = document.querySelectorAll('.select-style');
select_style.forEach((e) => {
    e.addEventListener('change', () => {
        const value = e.value;
        if (value == 'Company') {
            cngNavElemets('Company')
        } else {
            cngNavElemets('Address')
        }
    })
})