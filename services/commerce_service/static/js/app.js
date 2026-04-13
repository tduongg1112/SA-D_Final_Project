const sidebar = document.getElementById("sidebar");
const sidebarToggle = document.getElementById("sidebar-toggle");
const sidebarClose = document.getElementById("sidebar-close");

function closeSidebar() {
    if (sidebar) {
        sidebar.classList.remove("open");
    }
}

if (sidebar && sidebarToggle) {
    sidebarToggle.addEventListener("click", () => {
        sidebar.classList.add("open");
    });
}

if (sidebar && sidebarClose) {
    sidebarClose.addEventListener("click", closeSidebar);
}

document.addEventListener("click", (event) => {
    if (!sidebar || !sidebar.classList.contains("open")) {
        return;
    }
    if (sidebar.contains(event.target) || sidebarToggle?.contains(event.target)) {
        return;
    }
    closeSidebar();
});
