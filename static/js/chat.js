const chatMessages = document.querySelector("#chat-content");
const messages = document.querySelector("#messages");

const status_user = document.getElementById("status");

//temporario
const chat_and_search = document.getElementById("chat_and_search");

const chat_list = document.getElementById("chat-list");

const current_chat = document.getElementById("current_chat");
const current_chat_name = current_chat.querySelector("#current_chat_name");
const current_chat_img = current_chat.querySelector("img");

const current_user_id = parseInt(
  document.getElementById("profile_id").dataset.profile_id
);

document.getElementById("profile_id").remove();

const notifySocket = new WebSocket(
  `ws://${window.location.host}/ws/notify/${current_user_id}`
);

notifySocket.onmessage = function (event) {
  var data = JSON.parse(event.data);
  if (data.type === "notify_user") {
    const element = document.querySelector(`[data-chat_id="${data.user_id}"]`);

    chat_and_search.insertBefore(element, chat_and_search.children[1]);

    if (
      !element.className.includes("active-chat") &&
      !element.querySelector("span.notification")
    ) {
      element.innerHTML += '<span class="notification"></span>';
      console.log("Mensagem atualizada para a conversa: " + data.chat_uuid);
    }

    element.querySelector(".last_message").innerHTML = data.message;
  } else if (data.type === "change_friend_status") {
    document.querySelector(".online_status").style.display =
      data.status === "Online" ? "flex" : "none";
    status_user.innerHTML = data.status;
  }
};

let chatSocket;

function scrollToBottom() {
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

scrollToBottom();
const csrftoken = JSON.parse(document.getElementById("csrf_token").textContent);

document.addEventListener("DOMContentLoaded", () =>
  document.getElementById("csrf_token").remove()
);

function claim_websocket(chat_id) {
  fetch("/return_chat/", {
    method: "POST",
    headers: { "X-CSRFToken": csrftoken },
    mode: "same-origin",
    body: JSON.stringify({ chat_id: chat_id }),
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
          body: JSON.stringify({
            chat_uuid: data_file["chat_uuid"],
            current_user_id: current_user_id,
          }),
        })
          .then((response) => {
            if (response.ok) {
              return response.json();
            }
            throw new Error(response.status);
          })
          .then((data) => {
            document.querySelector(".online_status").style.display =
              data.friend_status === "Online" ? "flex" : "none";
            status_user.innerHTML = data.friend_status;

            data.messages.forEach((element) => {
              populate_messages(element);
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

      sendButton.onclick = () => {
        const messageInput = document.querySelector("#my_input").value;
        document.querySelector("#my_input").value = "";

        if (messageInput.length == 0) {
          alert("Escreva algo!");
        } else {
          chatSocket.send(
            JSON.stringify({
              message: messageInput,
              user_id: current_user_id,
              chat_uuid: data_file["chat_uuid"],
            })
          );
        }
      };

      chatSocket.onmessage = function (e) {
        const data = JSON.parse(e.data);
        const active_chat = document.querySelector(".active-chat");
        if (data.user_id == current_user_id) {
          active_chat.querySelector(".last_message").innerHTML = data.message;
        }
        chat_and_search.insertBefore(active_chat, chat_and_search.children[1]);

        populate_messages([data.user_id, data.message, data.message_time]);
      };
    })
    .catch((error) => {
      console.log("erro interno");
    });
}

let date = new Date();
let todaysDate = `${date.getDate()}${date.getMonth() + 1}${date.getFullYear()}`;

let lastDate = 0;

chat_and_search.addEventListener("click", (event) => {
  lastDate = 0;

  const chatItem = event.target.closest(".chat-item");

  if (chatItem) {
    claim_websocket(chatItem.dataset.chat_id);
    current_chat_img.src = chatItem.querySelector("img").src;
    current_chat_name.innerHTML =
      chatItem.querySelector(".chat_name").innerHTML;
    current_chat.classList.remove("d-none");
    current_chat.classList.add("d-flex");
  }
});

function populate_messages([user_id, message, message_time]) {
  const time = message_time.split("|"); //split the message in date and hour
  const date = parseInt(time[0].replaceAll("/", "")); //transform to date to Int

  if (date > lastDate) {
    lastDate = date;
    let dateDiv = document.createElement("div");
    dateDiv.className = "d-flex m-2 justify-content-center";

    dateDiv.innerHTML = `<div class='px-2 bg-dark text-light rounded'>
      ${date === parseInt(todaysDate) ? "Hoje" : time[0]} </div>`;
    messages.appendChild(dateDiv);
  }

  let div = document.createElement("div");
  let div_child = document.createElement("div");

  div_child.classList.add(
    "p-2",
    "text-white",
    "rounded",
    "d-flex",
    "flex-column"
  );

  div_child.style.minWidth = "60px";

  div_child.innerHTML = `<span class="mr-4" style='font-size:14px'>${message}</span>
                         <span class="ml-auto" style='font-size:11px'>${time[1]}</span>`;
  div.appendChild(div_child);

  div.classList.add("d-flex", "mb-2");
  if (user_id === current_user_id) {
    div.classList.add("justify-content-end");
    div_child.classList.add("bg-primary");
  } else {
    div.classList.add("justify-content-start");
    div_child.classList.add("bg-secondary");
  }

  document.getElementById("sendMessage").className = "d-none";
  messages.appendChild(div);
  scrollToBottom();
}

//change the color of selected chat
document.addEventListener("DOMContentLoaded", function () {
  let chatItems = document.querySelectorAll(".chat-item");
  chatItems.forEach((item) => {
    item.addEventListener("click", function () {
      chatItems.forEach((chat) => chat.classList.remove("active-chat"));
      if (item.innerHTML.includes('class="notification"')) {
        item.childNodes;
      }
      let notification = item.querySelector("span.notification");

      notification ? notification.remove() : "";

      item.classList.add("active-chat");
      //temporario enquanto só aceitam conversas privadas
      notifySocket.send(
        JSON.stringify({
          friend_id: parseInt(
            document.querySelector(".active-chat").dataset.chat_id
          ),
        })
      );
    });
  });
});

const search_input = document.getElementById("search_input");
const divResults = document.createElement("div");

search_input.addEventListener("input", () => {
  const query = search_input.value;
  if (query.trim() === "") {
    chat_list.style.display = "block";
    chat_and_search.removeChild(divResults);
    return;
  }
  chat_list.style.display = "none";
  chat_and_search.appendChild(divResults);

  fetch(`/search_page?searched=${search_input.value}`)
    .then((response) =>
      response.ok ? response.json() : new Error(response.status)
    )
    .then((data) => {
      const results = data.profiles;
      divResults.innerHTML = "";

      if (results.length) {
        results.forEach((result) => {
          const element = document.createElement("div");

          element.classList.add(
            "list-group-item",
            "list-group-item-action",
            "d-flex",
            "align-items-center",
            "chat-item"
          );
          element.dataset.chat_id = result.id;

          let profile_photo = document.createElement("img");
          profile_photo.className = "mr-3 rounded-circle";
          profile_photo.src = result.photo;

          element.appendChild(profile_photo);
          element.innerHTML += `<div class="messagePreview">
          <div class="chat_name h6">${result.name}</div>
          </div>`;

          divResults.appendChild(element);
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

        divResults.appendChild(element);
      }
    });
});
