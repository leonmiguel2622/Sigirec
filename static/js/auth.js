(function () {
    "use strict";

    const root = document.querySelector("[data-auth-root]");

    if (!root) {
        return;
    }

    const modeLinks = Array.from(root.querySelectorAll("[data-auth-switch]"));
    const panels = Array.from(root.querySelectorAll("[data-auth-panel]"));
    const titles = {
        login: "Iniciar sesión | SIGIREC",
        register: "Crear cuenta | SIGIREC"
    };

    function modeFromLocation() {
        return location.pathname.replace(/\/+$/, "").endsWith("/register")
            ? "register"
            : "login";
    }

    function currentMode() {
        return root.dataset.mode === "register" ? "register" : "login";
    }

    function focusPanelHeading(mode) {
        const panel = root.querySelector(
            '[data-auth-panel="' + mode + '"]'
        );
        const heading = panel ? panel.querySelector("h2[tabindex='-1']") : null;

        if (heading) {
            heading.focus({ preventScroll: true });
        }
    }

    function applyMode(mode, options) {
        const settings = options || {};
        const nextMode = mode === "register" ? "register" : "login";

        root.dataset.mode = nextMode;

        panels.forEach(function (panel) {
            const isActive = panel.dataset.authPanel === nextMode;

            panel.toggleAttribute("inert", !isActive);
            panel.setAttribute("aria-hidden", isActive ? "false" : "true");

            if (isActive) {
                panel.scrollTop = 0;
            }
        });

        modeLinks.forEach(function (link) {
            if (link.dataset.authSwitch === nextMode) {
                link.setAttribute("aria-current", "page");
            } else {
                link.removeAttribute("aria-current");
            }
        });

        document.title = titles[nextMode];

        if (settings.focus) {
            window.requestAnimationFrame(function () {
                focusPanelHeading(nextMode);
            });
        }
    }

    function switchMode(mode, options) {
        const settings = options || {};
        const nextMode = mode === "register" ? "register" : "login";
        const link = modeLinks.find(function (item) {
            return item.dataset.authSwitch === nextMode;
        });

        if (nextMode === currentMode()) {
            if (settings.focus) {
                focusPanelHeading(nextMode);
            }
            return;
        }

        applyMode(nextMode, { focus: settings.focus });

        if (settings.push && link) {
            history.pushState(
                Object.assign({}, history.state, { authMode: nextMode }),
                "",
                link.href
            );
        }
    }

    modeLinks.forEach(function (link) {
        link.addEventListener("click", function (event) {
            const mode = link.dataset.authSwitch;

            if (
                event.defaultPrevented ||
                event.button !== 0 ||
                event.metaKey ||
                event.ctrlKey ||
                event.shiftKey ||
                event.altKey
            ) {
                return;
            }

            event.preventDefault();
            switchMode(mode, {
                push: true,
                focus: event.detail === 0
            });
        });
    });

    window.addEventListener("popstate", function (event) {
        const mode = event.state && event.state.authMode
            ? event.state.authMode
            : modeFromLocation();

        switchMode(mode, { focus: true });
    });

    root.querySelectorAll("[data-password-toggle]").forEach(function (button) {
        button.addEventListener("click", function () {
            const inputId = button.getAttribute("aria-controls");
            const input = inputId ? document.getElementById(inputId) : null;

            if (!input) {
                return;
            }

            const willShow = input.type === "password";
            const caret = input.selectionStart;

            input.type = willShow ? "text" : "password";
            button.setAttribute("aria-pressed", willShow ? "true" : "false");
            button.setAttribute(
                "aria-label",
                willShow ? "Ocultar contraseña" : "Mostrar contraseña"
            );

            input.focus({ preventScroll: true });

            if (typeof caret === "number") {
                input.setSelectionRange(caret, caret);
            }
        });
    });

    root.querySelectorAll("form.auth-form").forEach(function (form) {
        form.addEventListener("submit", function () {
            const button = form.querySelector('button[type="submit"]');

            if (!button) {
                return;
            }

            button.disabled = true;
            button.dataset.loading = "true";
            button.setAttribute("aria-busy", "true");
        });
    });

    window.addEventListener("pageshow", function (event) {
        if (!event.persisted) {
            return;
        }

        root.querySelectorAll('.auth-submit[data-loading="true"]').forEach(
            function (button) {
                button.disabled = false;
                button.removeAttribute("data-loading");
                button.removeAttribute("aria-busy");
            }
        );
    });

    try {
        history.replaceState(
            Object.assign({}, history.state, { authMode: currentMode() }),
            "",
            location.href
        );
    } catch (error) {
        return;
    }
})();
