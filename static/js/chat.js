const chatbox = document.querySelector("#chat-content");

function scrollToBottom() {
  chatbox.scrollTop = chatbox.scrollHeight;
}

scrollToBottom();
const csrftoken = JSON.parse(document.getElementById("csrf_token").textContent);

document.addEventListener("DOMContentLoaded", () =>
  document.getElementById("csrf_token").remove()
);

function claim_websocket(contact_id, csrftoken) {
  fetch("/return_chat/", {
    method: "POST",
    headers: { "X-CSRFToken": csrftoken },
    mode: "same-origin",
    body: JSON.stringify({ contact_id: contact_id }),
  })
    .then((response) => {
      if (response.ok) {
        return response.json();
      } else {
        throw new error(response.error);
      }
    })
    .then((data) => {
      const chatSocket = new WebSocket(
        "ws://" + window.location.host + "/ws/chat/" + data["chat_uuid"] + "/"
      );
      console.log(chatSocket);

      chatSocket.onopen = (e) => {};
      chatSocket.onclose = (e) => {};

      const sendButton = document.querySelector("#submit_button");

      document.querySelector("#my_input").onkeyup = function (e) {
        if (e.keyCode == 13) {
          e.preventDefault();
          sendButton.click();
        }
      };

      sendButton.onclick = function (e) {
        var messageInput = document.querySelector("#my_input").value;

        if (messageInput.length == 0) {
          alert("Escreva algo!");
        } else {
          chatSocket.send(
            JSON.stringify({
              message: messageInput,
              user_id: data["current_user_id"],
              chat_uuid: data["chat_uuid"],
            })
          );
        }
      };

      chatSocket.onmessage = function (e) {
        const data = JSON.parse(e.data);
        var div = document.createElement("div");
        var div_child = document.createElement("div");

        div_child.classList.add("p-2", "text-white", "rounded");
        div_child.innerHTML = "<b>" + data.user_id + "</b> : " + data.message;

        div.appendChild(div_child);

        div.classList.add("d-flex", "mb-2");

        if (data.username === "{{ request.user.username }}") {
          div.classList.add("justify-content-end");
          div_child.classList.add("bg-primary");
        } else {
          div.classList.add("justify-content-start");
          div_child.classList.add("bg-secondary");
        }

        const messagesContent = document.querySelector("#chat-content");

        document.querySelector("#my_input").value = "";
        document.getElementById("sendMessage").className = "d-none";
        messagesContent.appendChild(div);
        scrollToBottom();
      };
    })
    .catch((error) => {
      console.log("erro interno");
    });
}

document
  .querySelector("#contact_and_search")
  .addEventListener("click", (event) => {
    if (
      event.target.classList.contains("chat-item") ||
      event.target.parentElement.classList.contains("chat-item")
    ) {
      const contact_id = event.target.dataset.contact_id
        ? event.target.dataset.contact_id
        : event.target.parentElement.dataset.contact_id;
      claim_websocket(contact_id, csrftoken);
    }
  });
