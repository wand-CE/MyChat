export const csrftoken = JSON.parse(
  document.getElementById("csrf_token").textContent
);

document.addEventListener("DOMContentLoaded", () =>
  document.getElementById("csrf_token").remove()
);

export const chat_list = document.getElementById("chat-list");

export function createChatElement(chatUuid, photo, name, message = "") {
  let element = document.createElement("div");

  element.className =
    "list-group-item list-group-item-action d-flex align-items-center chat-item";
  element.dataset.chat_id = `uuid:${chatUuid}`;
  element.innerHTML = `<img class="mr-3 rounded-circle" src="${photo}"/>
                          <div class="messagePreview">
                            <div class="chat_name h6">${name}</div>
                            <div class="last_message">${message}</div>
                          </div>`;
  return element;
}

export function profileElement(id, photo, name) {
  return `<div data-profileid=${id} class="btn list-group-item list-group-item-action d-flex align-items-center">
              <img class='mr-2 rounded-circle' src="${photo}" alt="" height="40">
              ${name}
              </div>`;
}

export function searchUsers(userToSearch) {
  return fetch(`/search_page?searched=${userToSearch}`);
}
