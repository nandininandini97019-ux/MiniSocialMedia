document.addEventListener("DOMContentLoaded", function () {
    // Prevent accidental duplicate submissions.
    document.querySelectorAll("form").forEach(function (form) {
        form.addEventListener("submit", function () {
            const button = form.querySelector(
                'button[type="submit"]'
            );

            if (button && form.checkValidity()) {
                button.dataset.originalText = button.textContent;
                button.textContent = "Please wait...";
                button.disabled = true;
            }
        });
    });

    // Preview selected images before uploading.
    document.querySelectorAll('input[type="file"]').forEach(function (input) {
        input.addEventListener("change", function () {
            const file = input.files[0];

            if (!file || !file.type.startsWith("image/")) {
                return;
            }

            let preview = input.parentElement.querySelector(
                ".image-preview"
            );

            if (!preview) {
                preview = document.createElement("img");
                preview.className = "image-preview";
                preview.style.maxWidth = "180px";
                preview.style.maxHeight = "180px";
                preview.style.objectFit = "contain";
                preview.style.display = "block";
                preview.style.marginTop = "12px";
                input.parentElement.appendChild(preview);
            }

            if (preview.dataset.objectUrl) {
                URL.revokeObjectURL(preview.dataset.objectUrl);
            }

            const objectUrl = URL.createObjectURL(file);
            preview.src = objectUrl;
            preview.dataset.objectUrl = objectUrl;
        });
    });
});