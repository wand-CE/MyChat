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
