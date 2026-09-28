document.addEventListener("DOMContentLoaded", function () {

    const form = document.getElementById("comicForm");
    const button = document.querySelector(".generate-button");

    if (!form || !button) {
        return;
    }

    form.addEventListener("submit", function () {

        button.disabled = true;

        button.innerHTML = `
            <span class="button-sparkle">✦</span>
            <span>Creating your story...</span>
        `;

    });

});