/** @odoo-module **/

const FORM_SELECTOR = ".o_form_view.ar_fb_demande_form";

function closeAutofocusedDatepicker(form) {
    const dateInput = form.querySelector(".o_field_widget[name='date_besoin'] input");
    if (!dateInput || document.activeElement !== dateInput) {
        return;
    }

    dateInput.dispatchEvent(new KeyboardEvent("keydown", {
        key: "Escape",
        bubbles: true,
    }));
    dateInput.blur();
}

function animateForm(form) {
    if (!form || form.dataset.arFbAnimated === "1") {
        return;
    }
    form.dataset.arFbAnimated = "1";

    form.querySelectorAll(".ar_sortie_caisse_panel").forEach((element) => {
        element.classList.add("ar_sc_reveal");
    });

    window.requestAnimationFrame(() => closeAutofocusedDatepicker(form));
}

function scan() {
    document.querySelectorAll(FORM_SELECTOR).forEach(animateForm);
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", scan);
} else {
    scan();
}

if (document.body) {
    const bodyObserver = new MutationObserver(scan);
    bodyObserver.observe(document.body, {
        childList: true,
        subtree: true,
    });
}
