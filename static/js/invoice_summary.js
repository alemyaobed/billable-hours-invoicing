document.getElementById("download-pdf").addEventListener("click", function () {
  var element = document.getElementById("invoice-content");

  html2pdf()
    .from(element)
    .set({
      margin: 1,
      filename: "Invoice_" + fileId + ".pdf", // Pass fileId from Django
      html2canvas: { scale: 2 },
      jsPDF: { orientation: "portrait", unit: "in", format: "letter" },
    })
    .save();
});

// Scroll to Top Function
function scrollToTop() {
  window.scrollTo({ top: 0, behavior: "smooth" });
}

// Show Back to Top Button when Scrolling
window.onscroll = function () {
  var backToTopBtn = document.getElementById("back-to-top");
  if (
    document.body.scrollTop > 200 ||
    document.documentElement.scrollTop > 200
  ) {
    backToTopBtn.style.display = "block";
  } else {
    backToTopBtn.style.display = "none";
  }
};
