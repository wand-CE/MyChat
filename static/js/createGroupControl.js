import { createChatElement, chat_list } from "./principalsFunctions.js";
import {
  elementsOnselected,
  selectedParticipants,
} from "./controlParticipantsNewGroup.js";

let menuControl = $("#myCarouselNewGroup");

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

  if (currentSlide.hasClass("participants-item")) {
    let groupParticipants = currentSlide.find("#id_participants")[0].children;
    if (!groupParticipants.length) {
      isValid = false;
      return false;
    }
  }

  if (isValid) {
    menuControl.carousel("next");
  }
}

function backSlide() {
  menuControl.carousel("prev");
  nextSlideButton.onclick = null;
}

let backSlideButton = document.querySelector(".backSlideButton");
let nextSlideButton = document.querySelector(".nextSlideButton");

backSlideButton.addEventListener("click", backSlide);

menuControl.on("slide.bs.carousel", function (event) {
  let currentSlide = event.to;
  let totalSlides = $("#myCarouselNewGroup .carousel-item").length - 1;

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
  data.append("participants", elementsOnselected);

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
  selectedParticipants.empty();
  form.reset();
  menuControl.carousel(0);
}

function disable_slide(slide, disabled) {
  menuControl.filter(slide).prop("disabled", disabled);
}
