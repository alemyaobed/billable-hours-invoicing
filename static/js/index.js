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

// Show flash message function
function showFlashMessage(message, type) {
  const alertContainer = document.createElement("div");
  alertContainer.className = `alert alert-${type} flash-message`;
  alertContainer.textContent = message;

  // Append to the body
  document.body.appendChild(alertContainer);

  // Calculate duration based on message length
  const baseDuration = 3000; // Minimum duration of 3 seconds
  const extraDuration = Math.max(0, message.length * 100); // 100ms for each character
  const duration = Math.max(baseDuration, extraDuration + baseDuration); // Ensure minimum duration

  // Automatically disappear after the calculated duration
  setTimeout(() => {
    alertContainer.classList.add("fade-out"); // Start fade out
    setTimeout(() => alertContainer.remove(), 500); // Remove after fade
  }, duration);
}

// Existing form submission script with spinner and status polling
document.getElementById("uploadForm").onsubmit = function (event) {
  event.preventDefault();

  let uploadButton = document.getElementById("uploadButton");
  let buttonSpinner = document.getElementById("buttonSpinner");
  let buttonText = document.getElementById("buttonText");
  let uploadIcon = document.getElementById("uploadIcon");

  let formData = new FormData(this);

  // Function to reset the upload button and UI
  function resetUploadButton() {
    buttonText.textContent = "Upload"; // Reset button text
    uploadIcon.style.display = "inline"; // Show the upload icon
    uploadButton.disabled = false; // Re-enable button
    buttonSpinner.style.display = "none"; // Hide spinner
  }

  fetch(upload_url, {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.error) {
        showFlashMessage(data.error, "danger");
      } else {
        // Update button text and state if successful
        buttonText.textContent = "Processing..."; // Change text to "Processing..."
        uploadIcon.style.display = "none"; // Hide the upload icon
        uploadButton.disabled = true; // Disable button
        buttonSpinner.style.display = "inline-block"; // Show spinner

        showFlashMessage(data.message, "success");

        const fileId = data.file_id;

        const intervalId = setInterval(() => {
          fetch(`/status/${fileId}/`)
            .then((response) => response.json())
            .then((statusData) => {
              if (statusData.status === "PROCESSED") {
                clearInterval(intervalId);
                window.location.href = `/invoices/${fileId}`;
              } else if (statusData.status === "FAILED") {
                clearInterval(intervalId);

                // Show error message
                showFlashMessage(
                  statusData.message || "An unknown error occurred.",
                  "danger"
                );

                // Reset the upload button and UI
                resetUploadButton();
              } else if (statusData.status === "error") {
                clearInterval(intervalId); // Clear interval on error
                showFlashMessage(
                  statusData.message || "An unknown error occurred.",
                  "danger"
                );

                // Reset the upload button and UI
                resetUploadButton();
              }
            })
            .catch((error) => {
              console.error("Error fetching upload status:", error);
              clearInterval(intervalId); // Clear interval on fetch error
              showFlashMessage(
                "Error fetching upload status. Please try again.",
                "danger"
              );

              // Reset the upload button and UI
              resetUploadButton();
            });
        }, 3000);
      }
    })
    .catch((error) => {
      console.error("Error uploading CSV:", error);
      showFlashMessage("Failed to upload CSV. Please try again.", "danger");

      // Reset the upload button and UI
      resetUploadButton();
    });
};
