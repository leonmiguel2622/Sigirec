(function () {
    "use strict";

    var btn = document.getElementById("mobile-hamburger");
    var sidebar = document.getElementById("mobile-sidebar");
    var overlay = document.getElementById("mobile-overlay");
    var abrirPorDefecto = "Abrir menú";
    var cerrarPorDefecto = "Cerrar menú";

    function setOpen(open) {
        if (!sidebar || !overlay || !btn) return;
        sidebar.classList.toggle("mobile-open", open);
        overlay.classList.toggle("active", open);
        btn.setAttribute("aria-expanded", open ? "true" : "false");
        btn.setAttribute("aria-label", open ? cerrarPorDefecto : abrirPorDefecto);
        if (open) {
            var primero = sidebar.querySelector("a, button");
            if (primero) primero.focus();
        } else {
            btn.focus();
        }
    }

    if (btn && sidebar && overlay) {
        btn.addEventListener("click", function () {
            setOpen(!sidebar.classList.contains("mobile-open"));
        });

        overlay.addEventListener("click", function () {
            setOpen(false);
        });

        document.addEventListener("keydown", function (e) {
            if (e.key === "Escape") setOpen(false);
        });
    }

    var modalOverlay = document.getElementById("modal-usuario-overlay");
    if (modalOverlay) {
        document.addEventListener("keydown", function (e) {
            if (e.key === "Escape" && modalOverlay.classList.contains("visible")) {
                var cerrarBtn = modalOverlay.querySelector(".modal-usuario-close");
                if (cerrarBtn) cerrarBtn.click(); else modalOverlay.classList.remove("visible");
            }
        });
    }
})();
