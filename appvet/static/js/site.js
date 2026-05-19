
document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('container');
    const registerBtn = document.getElementById('registerBtn');
    const loginBtn = document.getElementById('loginBtn');

    if (registerBtn && loginBtn && container) {
        registerBtn.addEventListener('click', () => {
            container.classList.add("active");
        });
        loginBtn.addEventListener('click', () => {
            container.classList.remove("active");
        });
    }
});



document.addEventListener('DOMContentLoaded', function () {
    const btnToggle = document.getElementById('toggleSidebar');
    const wrapper = document.getElementById('dashboardWrapper');

    if (btnToggle) {
        btnToggle.addEventListener('click', function () {
            wrapper.classList.toggle('sidebar-collapsed');
        });
    }
});