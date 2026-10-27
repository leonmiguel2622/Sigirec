document.addEventListener("DOMContentLoaded", function () {
    const userInput = document.getElementById("identificacion");
    const userSuggestions = document.getElementById("user-suggestions");
    const userOptions = Array.from(document.querySelectorAll(".mov-user-option"));
    const productCards = Array.from(document.querySelectorAll(".mov-product-card"));
    const searchButton = document.getElementById("btn-buscar");
    const redeemButton = document.getElementById("btn-canjar");
    const userPanel = document.getElementById("usuario-info");
    const summaryPanel = document.getElementById("resumen-canje");
    const emptySummary = document.getElementById("sin-seleccion");
    const warning = document.getElementById("checkout-warning");
    const successMessage = document.getElementById("mov-exito");
    const errorMessage = document.getElementById("mov-error");
    let currentUser = null;
    let currentProduct = null;

    userInput.addEventListener("input", function () {
        currentUser = null;
        userPanel.hidden = true;
        setProductCardsEnabled(false);
        updateSummary();
        hideMessages();
        renderSuggestions(userInput.value.trim());
    });

    userInput.addEventListener("keydown", function (event) {
        if (event.key === "Escape") {
            closeSuggestions();
        } else if (event.key === "Enter") {
            event.preventDefault();
            closeSuggestions();
            searchUser();
        } else if (event.key === "ArrowDown" && !userSuggestions.hidden) {
            const firstOption = userOptions.find(function (option) {
                return !option.hidden;
            });
            if (firstOption) {
                event.preventDefault();
                firstOption.focus();
            }
        }
    });

    userSuggestions.addEventListener("mousedown", function (event) {
        if (event.target.closest(".mov-user-option")) {
            event.preventDefault();
        }
    });

    userSuggestions.addEventListener("click", function (event) {
        const option = event.target.closest(".mov-user-option");
        if (!option) return;
        userInput.value = option.dataset.identificacion;
        closeSuggestions();
        searchUser();
    });

    searchButton.addEventListener("click", searchUser);

    productCards.forEach(function (card) {
        card.addEventListener("click", function () {
            if (card.disabled || !currentUser) return;

            productCards.forEach(function (item) {
                item.setAttribute("aria-pressed", String(item === card));
            });

            currentProduct = {
                id: Number(card.dataset.id),
                name: card.dataset.name,
                cost: Number(card.dataset.cost),
                stock: Number(card.dataset.stock),
                image: card.dataset.image
            };
            updateSummary();
            hideMessages();
        });
    });

    redeemButton.addEventListener("click", redeemProduct);

    function renderSuggestions(query) {
        const normalizedQuery = query.toLocaleLowerCase();
        let visibleCount = 0;

        userOptions.forEach(function (option) {
            const matches = normalizedQuery.length > 0 &&
                option.dataset.search.includes(normalizedQuery);
            option.hidden = !matches;
            option.setAttribute("aria-selected", "false");
            if (matches) visibleCount += 1;
        });

        userSuggestions.hidden = !normalizedQuery || visibleCount === 0;
        userInput.setAttribute("aria-expanded", String(!userSuggestions.hidden));
    }

    function closeSuggestions() {
        userSuggestions.hidden = true;
        userInput.setAttribute("aria-expanded", "false");
        userOptions.forEach(function (option) {
            option.hidden = true;
            option.setAttribute("aria-selected", "false");
        });
    }

    async function searchUser() {
        const query = userInput.value.trim();
        if (!query) {
            showError("Escribe un nombre o una identificación para buscar.");
            userInput.focus();
            return;
        }

        const queryLower = query.toLocaleLowerCase();
        const matchingOption = userOptions.find(function (option) {
            return option.dataset.identificacion.toLocaleLowerCase() === queryLower ||
                option.dataset.nombre.toLocaleLowerCase() === queryLower;
        });
        const identification = matchingOption
            ? matchingOption.dataset.identificacion
            : query;

        searchButton.disabled = true;
        searchButton.textContent = "Buscando...";
        closeSuggestions();
        hideMessages();

        try {
            const response = await fetch(
                "/admin/api/usuario/" + encodeURIComponent(identification),
                { credentials: "same-origin" }
            );
            const data = await response.json();
            if (!response.ok || data.error) {
                throw new Error(data.error || "No se pudo encontrar el usuario.");
            }

            currentUser = data;
            userInput.value = data.numero_identificacion;
            document.getElementById("info-avatar").textContent =
                (data.nombre_completo || "?").trim().charAt(0).toUpperCase();
            document.getElementById("info-nombre").textContent = data.nombre_completo;
            document.getElementById("info-id").textContent = data.numero_identificacion;
            document.getElementById("info-correo").textContent = data.correo || "Sin correo registrado";
            document.getElementById("info-puntos").textContent = formatPoints(data.puntos_totales);
            userPanel.hidden = false;
            setProductCardsEnabled(true);
            updateSummary();
        } catch (error) {
            currentUser = null;
            userPanel.hidden = true;
            setProductCardsEnabled(false);
            updateSummary();
            showError(error.message || "No fue posible buscar al usuario.");
        } finally {
            searchButton.disabled = false;
            searchButton.textContent = "Buscar usuario";
        }
    }

    function setProductCardsEnabled(enabled) {
        productCards.forEach(function (card) {
            card.disabled = !enabled || Number(card.dataset.stock) <= 0;
        });
    }

    function updateSummary() {
        if (!currentUser || !currentProduct) {
            summaryPanel.hidden = true;
            emptySummary.hidden = false;
            warning.hidden = true;
            redeemButton.disabled = true;
            return;
        }

        summaryPanel.hidden = false;
        emptySummary.hidden = true;
        document.getElementById("res-usuario").textContent = currentUser.nombre_completo;
        document.getElementById("res-producto").textContent = currentProduct.name;

        const productImage = document.getElementById("res-producto-imagen");
        productImage.src = currentProduct.image;
        productImage.hidden = false;

        const balance = Number(currentUser.puntos_totales) || 0;
        const cost = Number(currentProduct.cost) || 0;
        const newBalance = balance - cost;
        document.getElementById("res-saldo-actual").textContent =
            formatPoints(balance) + " SIGIPUNTOS";
        document.getElementById("res-costo").textContent =
            "− " + formatPoints(cost) + " SIGIPUNTOS";

        const resultingBalance = document.getElementById("res-saldo-nuevo");
        resultingBalance.textContent = formatPoints(newBalance) + " SIGIPUNTOS";
        resultingBalance.classList.toggle("mov-saldo-negativo", newBalance < 0);

        const outOfStock = currentProduct.stock <= 0;
        warning.hidden = newBalance >= 0 && !outOfStock;
        warning.textContent = outOfStock
            ? "Este producto ya no tiene unidades disponibles."
            : "Saldo insuficiente para realizar este canje.";
        redeemButton.disabled = newBalance < 0 || outOfStock;
    }

    async function redeemProduct() {
        if (!currentUser || !currentProduct || redeemButton.disabled) return;

        const confirmation = window.confirm(
            "¿Confirmar canje de " + currentProduct.name + " para " +
            currentUser.nombre_completo + " por " + formatPoints(currentProduct.cost) +
            " SIGIPUNTOS?"
        );
        if (!confirmation) return;

        redeemButton.disabled = true;
        redeemButton.textContent = "Procesando...";
        hideMessages();
        const csrfMeta = document.querySelector('meta[name="csrf-token"]');

        try {
            const response = await fetch("/admin/movimientos/canjar", {
                method: "POST",
                credentials: "same-origin",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfMeta ? csrfMeta.content : ""
                },
                body: JSON.stringify({
                    id_usuario: currentUser.id_usuario,
                    id_producto: currentProduct.id
                })
            });
            const data = await response.json();
            if (!response.ok || data.error) {
                throw new Error(data.error || "No fue posible completar el canje.");
            }

            currentUser.puntos_totales = data.saldo_nuevo;
            currentProduct.stock -= 1;
            document.getElementById("info-puntos").textContent = formatPoints(data.saldo_nuevo);

            const selectedCard = productCards.find(function (card) {
                return Number(card.dataset.id) === currentProduct.id;
            });
            if (selectedCard) {
                selectedCard.dataset.stock = String(currentProduct.stock);
                selectedCard.querySelector(".mov-product-stock").textContent =
                    currentProduct.stock > 0 ? currentProduct.stock + " en stock" : "Agotado";
            }

            showSuccess(
                data.mensaje + " Saldo restante: " + formatPoints(data.saldo_nuevo) +
                " SIGIPUNTOS. Comprobante: " + data.numero_canje + "."
            );
            updateSummary();
            if (currentProduct.stock <= 0 && selectedCard) {
                selectedCard.disabled = true;
            }
        } catch (error) {
            showError(error.message || "No fue posible completar el canje.");
        } finally {
            redeemButton.textContent = "Confirmar canje";
            updateSummary();
        }
    }

    function formatPoints(value) {
        return new Intl.NumberFormat("es-CO", { maximumFractionDigits: 0 })
            .format(Number(value) || 0);
    }

    function showError(message) {
        document.getElementById("msg-error").textContent = message;
        errorMessage.hidden = false;
        successMessage.hidden = true;
    }

    function showSuccess(message) {
        document.getElementById("msg-exito").textContent = message;
        successMessage.hidden = false;
        errorMessage.hidden = true;
    }

    function hideMessages() {
        successMessage.hidden = true;
        errorMessage.hidden = true;
    }
});