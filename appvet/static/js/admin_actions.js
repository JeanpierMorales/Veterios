// Manejo global de la interfaz administrativa
$(document).ready(function () {
    //NOTITAS 
    // 1. Colapso del Sidebar
    $('#toggleBtn').on('click', function (e) {
        e.preventDefault();
        $('#sidebar').toggleClass('collapsed');

        const isCollapsed = $('#sidebar').hasClass('collapsed');
        localStorage.setItem('sidebarState', isCollapsed ? 'collapsed' : 'expanded');
    });

    // 2. Mantener el estado del sidebar al recargar
    if (localStorage.getItem('sidebarState') === 'collapsed') {
        $('#sidebar').addClass('collapsed');
    }

    // 3. Auto-ocultar mensajes de alerta (TempData) después de 5 segundos
    setTimeout(function () {
        $(".alert").fadeOut("slow");
    }, 5000);
});