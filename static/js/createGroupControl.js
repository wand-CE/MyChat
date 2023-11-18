import { createChatElement, chat_list } from "./principalsFunctions.js";

let menuControl = $("#myCarousel");

function nextSlide() {
  let currentSlide = $(".carousel-item.active");
  let formFields = currentSlide.find("[required]");
  let isValid = true;

  formFields.each(function () {
    if (!this.checkValidity()) {
      isValid = false;
      return false;
    }
  });

  if (isValid) {
    menuControl.carousel("next");
  }
}

function backSlide() {
  menuControl.carousel("prev");
}

let backSlideButton = document.querySelector(".backSlideButton");
backSlideButton.addEventListener("click", backSlide);

let nextSlideButton = document.querySelector(".nextSlideButton");

menuControl.on("slide.bs.carousel", function (event) {
  let currentSlide = event.to;
  let totalSlides = $("#myCarousel .carousel-item").length - 1;

  backSlideButton.disabled = currentSlide ? false : true;
  disable_slide('[data-slide="prev"]', currentSlide ? true : false);

  if (currentSlide === totalSlides) {
    nextSlideButton.textContent = "Criar Grupo";
    nextSlideButton.classList.add("sendGroupData");
    disable_slide('[data-slide="next"]', true);
  } else {
    nextSlideButton.textContent = "Próximo";
    nextSlideButton.classList.remove("sendGroupData");
    disable_slide('[data-slide="next"]', false);
  }
});

nextSlideButton.addEventListener("click", (event) => {
  nextSlide();
  let sendGroupButton = event.target.closest(".sendGroupData");

  if (sendGroupButton) {
    sendGroupButton.onclick = () => {
      document.querySelector(".closeCreateGroup").click();
      sendGroupButton.onclick = null;
      createGroup();
    };
  }
});

function createGroup() {
  let form = document.getElementById("formCreateGroup");
  let data = new FormData(form);

  fetch("/create_group/", {
    method: "POST",
    body: data,
    credentials: "same-origin",
  })
    .then((response) => response.json())
    .then((data) => {
      chat_list.insertBefore(
        createChatElement(...Object.values(data)),
        chat_list.children[0]
      );
    });

  form.reset();
  menuControl.carousel(0);
}

function disable_slide(slide, disabled) {
  menuControl.filter(slide).prop("disabled", disabled);
}
