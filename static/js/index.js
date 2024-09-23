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
  let tryAgainButton = document.getElementById("tryAgainButton");
  let tryAgainText = document.getElementById("tryAgainText");
  let tryAgainSpinner = document.getElementById("tryAgainSpinner");
  let tryAgainIcon = document.getElementById("tryAgainIcon");

  let formData = new FormData(this);

  // Function to reset the upload button and UI
  function resetUploadButton() {
    buttonText.textContent = "Upload";
    uploadIcon.style.display = "inline";
    uploadButton.disabled = false;
    buttonSpinner.style.display = "none";
    tryAgainButton.style.display = "none"; // Hide the try again button
  }

  // Reset the "Try Again" button
  function resetTryAgainButton() {
    tryAgainText.textContent = "Try Again";
    tryAgainButton.disabled = false;
    tryAgainSpinner.style.display = "none";
    tryAgainIcon.style.display = "inline";
    tryAgainButton.style.display = "none"; // Hide the "Try Again" button
  }

  fetch(upload_url, {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.error) {
        showFlashMessage(data.error, "danger");
        resetUploadButton();
        return;
      }

      buttonText.textContent = "Processing...";
      uploadIcon.style.display = "none";
      uploadButton.disabled = true;
      buttonSpinner.style.display = "inline-block";
      showFlashMessage(data.message, "success");

      const fileId = data.file_id;

      let pollingInterval = 3000; // Start with 3 seconds
      let attempts = 0;
      let intervalId; // Declare the intervalId
      let maxAttempts = 8; // Total attempts to reach 12 seconds

      const startPolling = () => {
        intervalId = setInterval(() => {
          fetch(`/status/${fileId}/`)
            .then((response) => response.json())
            .then((statusData) => {
              if (statusData.status === "PROCESSED") {
                clearInterval(intervalId);
                window.location.href = `/invoices/${fileId}`;
              } else if (
                statusData.status === "FAILED" ||
                statusData.status === "error"
              ) {
                clearInterval(intervalId);
                showFlashMessage(
                  statusData.message || "An unknown error occurred.",
                  "danger"
                );
                resetUploadButton();
              }

              attempts++;
              if (attempts === maxAttempts) {
                clearInterval(intervalId); // Stop polling
                tryAgainButton.style.display = "inline-block"; // Show the "Try Again" button
                uploadButton.style.display = "none"; // Hide the upload button

                // Show the message after first multiple attempts
                showFlashMessage(
                  "Please wait a bit before trying again.",
                  "warning"
                );
              }

              // Update polling interval for next request
              pollingInterval += 1500; // Increase by 1.5 seconds
            })
            .catch((error) => {
              console.error("Error fetching upload status:", error);
              clearInterval(intervalId);
              showFlashMessage(
                "Error fetching upload status. Please try again.",
                "danger"
              );
              resetUploadButton();
            });
        }, pollingInterval);
      };

      // Start the polling process
      startPolling();

      // Handle "Try Again" button click
      tryAgainButton.onclick = function () {
        // Stop the existing polling
        clearInterval(intervalId);

        // Reset button UI
        tryAgainText.textContent = "Trying again...";
        tryAgainButton.disabled = true;
        tryAgainSpinner.style.display = "inline-block"; // Show spinner
        tryAgainIcon.style.display = "none"; // Hide the icon

        // Restart the polling process
        let newAttempts = 0; // Reset attempts for "Try Again"
        let newPollingInterval = 3000; // Reset to 3 seconds

        const retryIntervalId = setInterval(() => {
          fetch(`/status/${fileId}/`)
            .then((response) => response.json())
            .then((statusData) => {
              if (statusData.status === "PROCESSED") {
                clearInterval(retryIntervalId);
                window.location.href = `/invoices/${fileId}`;
              } else if (
                statusData.status === "FAILED" ||
                statusData.status === "error"
              ) {
                clearInterval(retryIntervalId);
                showFlashMessage(
                  statusData.message || "An unknown error occurred.",
                  "danger"
                );
                resetUploadButton();
              }

              newAttempts++;
              if (newAttempts >= maxAttempts) {
                // After 8 attempts (12 seconds), stop retrying and show the message
                clearInterval(retryIntervalId);
                showFlashMessage(
                  "No response after multiple attempts. Please try uploading again.",
                  "warning"
                );
                resetUploadButton();
                uploadButton.style.display = "inline-block"; // Show the upload button
                resetTryAgainButton(); // Reset the "Try Again" button
              }

              // Update polling interval for next request
              newPollingInterval += 1500; // Increase by 1.5 seconds
            })
            .catch((error) => {
              console.error("Error fetching upload status:", error);
              clearInterval(retryIntervalId);
              showFlashMessage(
                "Error fetching upload status. Please try again.",
                "danger"
              );
              resetUploadButton();
            });
        }, newPollingInterval);
      };
    })
    .catch((error) => {
      console.error("Error uploading CSV:", error);
      showFlashMessage("Failed to upload CSV. Please try again.", "danger");
      resetUploadButton();
    });
};
