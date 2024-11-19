import {
    createChatElement,
    chat_list,
    searchUsers,
    csrftoken,
} from "./principalsFunctions.js";

import {populateGroupParticipants} from "./controlParticipantsGroup.js";

const chatMessages = document.querySelector("#chat-content");
const messages = document.querySelector("#messages");

const status_user = document.getElementById("status");
const chat_and_search = document.getElementById("chat_and_search");

const current_chat = document.getElementById("current_chat");
const current_chat_name = current_chat.querySelector("#current_chat_name");
const current_chat_img = current_chat.querySelector("#chat-profile-image");

const current_user_id = parseInt(document.getElementById("profile_id").dataset.profile_id);

const current_profile_name = document.getElementById("profile_id").dataset.currentprofile;

document.getElementById("profile_id").remove();

const notifySocket = new WebSocket(`ws://${window.location.host}/ws/notify/${current_user_id}`);

notifySocket.onmessage = function (event) {
    let data = JSON.parse(event.data);
    if (data.type === "notify_user") {
        let chatProfile = parseInt(data.sender.id) === current_user_id ? data.recipient : data.sender;
        let element = document.querySelector(`[data-chat_id="uuid:${data.chat.uuid}"]`);

        if (!element) {
            if (data.chat.is_group) {
                let chat = data.chat;
                element = createChatElement(
                    chat.uuid,
                    chat.photo,
                    chat.name,
                    data.message
                );
            } else {
                element = createChatElement(
                    data.chat.uuid,
                    chatProfile.photo,
                    chatProfile.name,
                    data.message
                );
            }
        }

        chat_list.insertBefore(element, chat_list.children[0]);

        if (
            !element.className.includes("active-chat") &&
            !element.querySelector("span.notification")
        ) {
            element.innerHTML += '<span class="notification"></span>';
        }

        element.querySelector(".last_message").innerHTML = `<strong>${
            chatProfile.name === current_profile_name ? "Você" : chatProfile.name
        }: </strong>${data.message}`;
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

function claim_websocket(chat_data, chatItem) {
    fetch("/return_chat/", {
        method: "POST",
        headers: {"X-CSRFToken": csrftoken},
        mode: "same-origin",
        body: JSON.stringify({chat_data: chat_data}),
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

            chatItem.dataset.chat_id = `uuid:${data_file["chat_uuid"]}`;

            messages.innerHTML = "";

            chatSocket.onopen = (e) => {
                fetch("chat/get_old_messages/", {
                    method: "POST",
                    headers: {"X-CSRFToken": csrftoken},
                    mode: "same-origin",
                    body: JSON.stringify({
                        chat_uuid: data_file["chat_uuid"],
                        is_group: data_file["is_group"],
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
                        let group_participants = document.querySelector("#groupElements");

                        data.messages.forEach((element) => {
                            populate_messages(element.concat(data.is_group));
                        });

                        if (!data.is_group) {
                            document.querySelector(".online_status").style.display =
                                data.friend_status === "Online" ? "flex" : "none";
                            status_user.innerHTML = data.friend_status;
                            group_participants.style.display = "none";

                            status_user.style.display = "flex";
                            document.querySelector(".group-menu").style.display = "none";
                        } else {
                            let children = group_participants.parentElement.children;

                            Array.from(children).forEach((child) => {
                                child.style.display = "none";
                            });

                            let groupMenu = document.querySelector(".group-menu");
                            groupMenu.dataset.chat_uuid = data_file["chat_uuid"];
                            groupMenu.style.display = "flex";

                            group_participants.textContent = data.participants.names;
                            group_participants.style.display = "flex";

                            let participants = data.participants;

                            populateGroupParticipants(participants);
                        }
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

                if (messageInput.length === 0) {
                    alert("Escreva algo!");
                } else {
                    chatSocket.send(
                        JSON.stringify({
                            message: messageInput,
                            user_id: current_user_id,
                            is_group: data_file["is_group"],
                            chat_uuid: data_file["chat_uuid"],
                        })
                    );
                }
            };

            chatSocket.onmessage = function (e) {
                const data = JSON.parse(e.data);
                if (data.type === "send_message") {
                    const active_chat = document.querySelector(".active-chat");
                    if (data.user.id === current_user_id) {
                        active_chat.querySelector(".last_message").innerHTML = data.message;
                    }
                    chat_list.insertBefore(active_chat, chat_list.children[0]);

                    populate_messages([
                        data.user,
                        data.is_read,
                        data.message,
                        data.message_time,
                        data.is_group,
                    ]);
                } else if (data.type === "mark_message_read_on_page") {
                    if (data.owner_of_message === current_user_id) {
                        chatMessages.querySelectorAll(".bi-check").forEach((item) => {
                            item.classList.remove("bi-check");
                            item.classList.add("bi-check-all");
                        });
                    }
                }
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

    let chatItem = event.target.closest(".chat-item");


    if (chatItem) {
        document.getElementById("sendMessage").className = "d-none";
        document.getElementById("chat-header").style.display = "flex";


        let active_chat = document.querySelector(".active-chat");
        let chatData = chatItem.dataset.chat_id;

        if (chatItem.closest("#divResults")) {
            let elementInList = chat_list.querySelector(`[data-chat_id='${chatData}']`);
            if (!elementInList) {
                chat_list.appendChild(chatItem);
            } else {
                chatItem = elementInList;
            }
            search_input.value = "";
            chat_list.style.display = "block";
        }

        divResults.innerHTML = "";

        if (active_chat) {
            // the return stop the function case chatItem is already selected
            if (chatData === active_chat.dataset.chat_id) return;
            active_chat.classList.remove("active-chat");
        }

        let notification = chatItem.querySelector("span.notification");
        if (notification) notification.remove(); // remove notification signal case it have

        chatItem.classList.add("active-chat");
        claim_websocket(chatData, chatItem);

        // this is temp while theres no group chats
        notifySocket.send(
            JSON.stringify({
                chat_uuid: chatData,
            })
        );

        current_chat_img.src = chatItem.querySelector("img").src;
        current_chat_name.innerHTML = chatItem.querySelector(".chat_name").innerHTML;
        current_chat.classList.remove("d-none");
        current_chat.classList.add("d-flex");
    }
});

function populate_messages([user, is_read, message, message_time, is_group]) {
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

    let div_parent = document.createElement("div");
    let div_child = document.createElement("div");

    const spanMessage = document.createElement('span');

    div_child.className = "p-2 text-white rounded d-flex flex-column";


    div_child.style.minWidth = "60px";
    div_parent.classList.add("d-flex", "mb-2");

    spanMessage.classList.add('mr-4');
    spanMessage.style.fontSize = '14px';
    spanMessage.style.overflowWrap = 'break-word';

    spanMessage.textContent = message;

    if (user.id === current_user_id) {
        const spanTime = document.createElement('span');

        spanTime.classList.add('ml-auto', 'time');
        spanTime.style.fontSize = '11px';
        spanTime.textContent = time[1];

        spanMessage.appendChild(spanTime);

        div_parent.classList.add("justify-content-end");
        div_child.classList.add("bg-primary");


        let check = document.createElement("i");
        check.className = `bi bi-check${is_read ? "-all" : ""}`;
        check.style.fontSize = "large";

        spanTime.appendChild(check);
        div_child.appendChild(spanMessage);
        div_child.appendChild(spanTime);

    } else {
        div_child.innerHTML = is_group ? `<strong>${user.name}</strong>` : "";
        div_parent.classList.add("justify-content-start");
        div_child.classList.add("bg-secondary");

        div_child.appendChild(spanMessage);

        div_child.innerHTML += `<span class="ml-auto" style='font-size:11px'>${time[1]}</span>`;
    }

    div_parent.appendChild(div_child);
    messages.appendChild(div_parent);

    scrollToBottom();
}

const search_input = document.getElementById("search_input");
const divResults = document.getElementById("divResults");

search_input.addEventListener("input", () => {
    const query = search_input.value;
    if (query.trim() === "") {
        chat_list.style.display = "block";
        chat_and_search.removeChild(divResults);
        return;
    }
    chat_list.style.display = "none";
    chat_and_search.appendChild(divResults);

    searchUsers(search_input.value)
        .then((response) => response.ok ? response.json() : new Error(response.status))
        .then((data) => {
            const results = data.profiles;
            divResults.innerHTML = "";

            const element = document.createElement("div");
            element.className = "list-group-item list-group-item-action d-flex align-items-center"
            if (results.length) {
                results.forEach((result) => {
                    element.classList.add("chat-item");
                    element.dataset.chat_id = result.uuid;
                    element.dataset.bsDismiss = "offcanvas";

                    let profile_photo = document.createElement("img");
                    profile_photo.className = "mr-3 rounded-circle";
                    profile_photo.src = result.photo;

                    element.appendChild(profile_photo);
                    element.innerHTML += `<div class="messagePreview m-2">
                                            <div class="chat_name h6">${result.name}</div><div class="last_message"></div>
                                          </div>`;
                });
            } else {
                element.innerHTML += "Usuário não encontrado";
            }
            divResults.appendChild(element);
        });
});
