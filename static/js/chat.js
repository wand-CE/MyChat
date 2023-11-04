const chatbox = document.querySelector("#chat-content");
const messages = document.querySelector("#messages");

const notifySocket = new WebSocket(`ws://${window.location.host}/ws/notify/`);

notifySocket.onmessage = function (event) {
  var data = JSON.parse(event.data);
  if (data.type === "message_updated") {
    // Tratar a notificação de atualização de mensagem
    console.log("Mensagem atualizada para a conversa: " + data.chat_uuid);
    // Atualizar a interface do usuário, por exemplo, carregar as mensagens atualizadas da conversa
  }
};

let chatSocket;

function scrollToBottom() {
  chatbox.scrollTop = chatbox.scrollHeight;
}

scrollToBottom();
const csrftoken = JSON.parse(document.getElementById("csrf_token").textContent);
let current_user_id;

document.addEventListener("DOMContentLoaded", () =>
  document.getElementById("csrf_token").remove()
);

function claim_websocket(contact_id) {
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
        throw new error(response.status);
      }
    })
    .then((data_file) => {
      if (chatSocket) {
        chatSocket.close();
      }

      chatSocket = new WebSocket(
        `ws://${window.location.host}/ws/chat/${data_file["chat_uuid"]}/`
      );

      messages.innerHTML = "";

      chatSocket.onopen = (e) => {
        fetch("chat/get_old_messages/", {
          method: "POST",
          headers: { "X-CSRFToken": csrftoken },
          mode: "same-origin",
          body: JSON.stringify(data_file["chat_uuid"]),
        })
          .then((response) => {
            if (response.ok) {
              return response.json();
            }
            throw new Error(response.status);
          })
          .then((data) => {
            data["messages"].forEach((element) => {
              populate_messages(element[0], element[1]);
            });
          });
      };
      chatSocket.onclose = (e) => {
        console.log("fechou");
      };

      const sendButton = document.querySelector("#submit_button");

      document.querySelector("#my_input").onkeyup = function (e) {
        if (e.keyCode == 13) {
          e.preventDefault();
          sendButton.click();
        }
      };

      sendButton.onclick = function (e) {
        let messageInput = document.querySelector("#my_input").value;

        if (messageInput.length == 0) {
          alert("Escreva algo!");
        } else {
          chatSocket.send(
            JSON.stringify({
              message: messageInput,
              user_id: data_file["current_user_id"],
              chat_uuid: data_file["chat_uuid"],
            })
          );
        }
      };

      current_user_id = data_file["current_user_id"];

      chatSocket.onmessage = function (e) {
        const data = JSON.parse(e.data);
        populate_messages(data.user_id, data.message);
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
      claim_websocket(contact_id);
    }
  });

function populate_messages(user_id, message) {
  let div = document.createElement("div");
  let div_child = document.createElement("div");

  div_child.classList.add("p-2", "text-white", "rounded");
  div_child.innerHTML = message;

  div.appendChild(div_child);

  div.classList.add("d-flex", "mb-2");

  if (user_id === current_user_id) {
    div.classList.add("justify-content-end");
    div_child.classList.add("bg-primary");
  } else {
    div.classList.add("justify-content-start");
    div_child.classList.add("bg-secondary");
  }

  document.querySelector("#my_input").value = "";
  document.getElementById("sendMessage").className = "d-none";
  messages.appendChild(div);
  scrollToBottom();
}

//Muda a cor do contato selecionado
document.addEventListener("DOMContentLoaded", function () {
  let chatItems = document.querySelectorAll(".chat-item");
  chatItems.forEach((item) => {
    item.addEventListener("click", function () {
      chatItems.forEach((chat) => chat.classList.remove("active-chat"));
      item.classList.add("active-chat");
    });
  });
});

//temporario
const contacts = document.getElementById("contact_and_search");

const search_input = document.getElementById("search_input");
const searchResults = document.getElementById("temp_test");

// Simula a busca e exibe resultados temporariamente
search_input.addEventListener("input", () => {
  const query = search_input.value;
  if (query.trim() === "") {
    searchResults.style.display = "none";
    return;
  }
  fetch(`/search_page?searched=${search_input.value}`)
    .then((response) =>
      response.ok ? response.json() : new Error(response.status)
    )
    .then((data) => {
      const results = data.profiles;
      searchResults.innerHTML = "";

      if (results.length) {
        results.forEach((result) => {
          const element = document.createElement("a");

          element.classList.add(
            "list-group-item",
            "list-group-item-action",
            "d-flex",
            "align-items-center",
            "chat-item"
          );
          element.dataset.contact_id = result.id;

          let profile_photo = document.createElement("img");
          profile_photo.className = "mr-3 rounded-circle";
          profile_photo.src = result.photo;

          element.appendChild(profile_photo);
          element.innerHTML += result.name;

          searchResults.appendChild(element);
        });
      } else {
        const element = document.createElement("div");

        element.classList.add(
          "list-group-item",
          "list-group-item-action",
          "d-flex",
          "align-items-center"
        );

        element.innerHTML += "Usuário não encontrado";

        searchResults.appendChild(element);
      }
      searchResults.style.display = "block";
    });
});

document.addEventListener("click", (event) => {
  if (!searchResults.contains(event.target) && event.target !== search_input) {
    searchResults.style.display = "none";
  }
});
