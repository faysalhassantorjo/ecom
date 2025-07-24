const categoryWrapper = document.querySelector(".category-wrapper");
const arrowLeft = document.querySelector(".arrow-left");
const arrowRight = document.querySelector(".arrow-right");
const categoryCards = document.querySelectorAll(".category-card");

function updateArrows() {
  const scrollLeft = categoryWrapper.scrollLeft;
  const maxScrollLeft =
    categoryWrapper.scrollWidth - categoryWrapper.clientWidth;

  if (scrollLeft > 0) {
    arrowLeft.style.display = "block";
  } else {
    arrowLeft.style.display = "none";
  }

  if (scrollLeft < maxScrollLeft) {
    arrowRight.style.display = "block";
  } else {
    arrowRight.style.display = "none";
  }
}

arrowLeft.addEventListener("click", () => {
  categoryWrapper.scrollBy({
    left: -screen.width,
    behavior: "smooth",
  });
  console.log(screen.width);
});

arrowRight.addEventListener("click", () => {
  categoryWrapper.scrollBy({
    left: screen.width - 30,
    behavior: "smooth",
  });
  console.log(screen.width);
});

categoryWrapper.addEventListener("scroll", updateArrows);

window.addEventListener("load", () => {
  if (categoryCards.length > 0) {
    updateArrows();
  } else {
    arrowLeft.style.display = "none";
    arrowRight.style.display = "none";
  }
});
