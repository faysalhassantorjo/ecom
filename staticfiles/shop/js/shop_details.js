document.addEventListener("DOMContentLoaded", function () {
  // Add hover effects for cart icon
  const cartIcon = document.querySelector(".fa-shopping-cart");
  if (cartIcon) {
    cartIcon.addEventListener("mouseenter", function () {
      this.style.transform = "scale(1.1)";
      this.style.borderColor = "#f74f06";
    });
    cartIcon.addEventListener("mouseleave", function () {
      this.style.transform = "scale(1)";
      this.style.borderColor = "#fff";
    });
  }

  const button = document.getElementById("unstiched-button");
  const priceElement = document.getElementById("product-price");

  const inputContainer = document.getElementById("form_c");
  const unstitchedPrice = document.body.dataset['unstitched_price']

  const Unstitched_info = document.getElementById("Unstitched-info");

  if (button) {
    button.addEventListener("click", function () {
      priceElement.textContent = `${unstitchedPrice}`;
      const inputField = document.createElement("input");
      inputField.type = "hidden";
      inputField.value = unstitchedPrice;
      inputField.name = "unstitched";
      inputField.classList.add("form-control", "mt-2");
      inputContainer.appendChild(inputField);
      button.innerText = "Unstitched Price is  " + unstitchedPrice;
      button.classList = "";
      button.style.border = "none";
      button.style.color = "#fff";
      Unstitched_info.innerText = "Select a Random Size ";
    });
  }

  const form = document.getElementById("updateForm");

  var messageElement = document.getElementById("success-message");

  form.addEventListener("submit", async function (e) {
    e.preventDefault();
    const size = form.querySelector('input[name="size"]:checked');
    if (!size) {
      alert("Please select a size.");
      return;
    }
    const formData = new FormData(form);
    const loadingElement = document.getElementById("loading");
    loadingElement.style.display = "block";
    loadingElement.style.display = "flex";
    fetch("/update_item/", {
      method: "POST",
      body: formData,
    })
      .then((response) => {
        loadingElement.style.display = "none";
        if (!response.ok) throw new Error("Network response was not ok");
        return response.json();
      })
      .then((data) => {
        console.log("Success:", data);
        messageElement.style.display = "block";
        messageElement.innerText = data.message;

        let cart_items = document.getElementById("cart_items");
        let currentCount = parseInt(cart_items.innerText) || 0; // fallback to 0 if NaN
        cart_items.innerText = currentCount + 1;

        window.scrollTo({
                top: 0,
                behavior: 'smooth'
        });

        form.reset();
        setTimeout(function () {
          messageElement.style.display = "none";
        }, 2000);
      })
      .catch((error) => {
        loadingElement.style.display = "none";
        console.error("Fetch error:", error);
        alert("Something went wrong.");
      });
  });
});

function changeImage(src) {
  document.getElementById("mainImage").src = src;
}
function toggleReviewSection() {
  const reviewSection = document.getElementById("all-reviews");
  const toggleButton = document.getElementById("toggleButton");

  if (reviewSection.classList.contains("hidden-reviews")) {
    reviewSection.classList.remove("hidden-reviews");
    reviewSection.classList.add("visible-reviews");
    toggleButton.textContent = "Hide Reviews";
  } else {
    reviewSection.classList.remove("visible-reviews");
    reviewSection.classList.add("hidden-reviews");
    toggleButton.textContent = "See Reviews";
  }
}
