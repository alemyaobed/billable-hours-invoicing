// Handle file selection and show file icon and name
document.getElementById("csvFile").addEventListener("change", function () {
  const fileInput = document.getElementById("csvFile");
  const filePreview = document.getElementById("filePreview");
  const fileName = document.getElementById("fileName");

  if (fileInput.files.length > 0) {
    filePreview.style.display = "block";
    fileName.textContent = fileInput.files[0].name;
  } else {
    filePreview.style.display = "none";
    fileName.textContent = "";
  }
});

function showFlashMessage(message, type) {
  const alertContainer = document.createElement("div");
  alertContainer.className = `alert alert-${type} flash-message`;
  alertContainer.textContent = message;

  // Append to the body
  document.body.appendChild(alertContainer);

  // Automatically disappear after a few seconds
  setTimeout(() => {
    alertContainer.classList.add("fade-out"); // Start fade out
    setTimeout(() => alertContainer.remove(), 500); // Remove after fade
  }, 3000); // Adjust duration as needed
}

// Existing form submission script with spinner and status polling
document.getElementById("uploadForm").onsubmit = function (event) {
  event.preventDefault();

  let uploadButton = document.getElementById("uploadButton");
  let buttonSpinner = document.getElementById("buttonSpinner");
  let buttonText = document.getElementById("buttonText");
  let uploadIcon = document.getElementById("uploadIcon");

  // Update button text and state
  buttonText.textContent = "Processing..."; // Change text to "Processing..."
  uploadIcon.style.display = "none"; // Hide the upload icon
  uploadButton.disabled = true; // Disable button
  buttonSpinner.style.display = "inline-block"; // Show spinner

  let formData = new FormData(this);

  fetch(upload_url, {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.error) {
        showFlashMessage(data.error, "danger");
      } else {
        showFlashMessage(
          "File uploaded successfully. Processing commenced.",
          "success"
        );
        const fileId = data.file_id;

        const intervalId = setInterval(() => {
          fetch(`/status/${fileId}/`)
            .then((response) => response.json())
            .then((statusData) => {
              if (statusData.status === "processed") {
                clearInterval(intervalId);
                window.location.href = `/invoices/${fileId}`;
              }
            })
            .catch((error) => {
              console.error("Error fetching upload status:", error);
            });
        }, 3000);
      }
    })
    .catch((error) => {
      console.error("Error uploading CSV:", error);
      showFlashMessage("Failed to upload CSV. Please try again.", "danger");
    });
};
