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
        "list-group-item list-group-item-action d-flex align-items-center chat-item ml-3 bg-transparent";
    element.dataset.chat_id = `uuid:${chatUuid}`;
    element.innerHTML = `<img class="mr-3 rounded-circle" src="${photo}"/>
                          <div class="messagePreview m-2">
                            <div class="chat_name h6">${name}</div>
                            <div class="last_message">${message}</div>
                          </div>`;
    return element;
}

export function profileElement(id, photo, name) {
    return `<div data-profileid=${id} class="my-2 btn border-top list-group-item list-group-item-action d-flex align-items-center ml-3">
              <img class='m-2 rounded-circle' src="${photo}" alt="" height="40">
              ${name}
              </div>`;
}

export function searchUsers(userToSearch) {
    return fetch(`/search_page?profiles=${userToSearch}`);
}
