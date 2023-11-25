import { searchUsers } from "./principalsFunctions.js";
import { profileElement } from "./principalsFunctions.js";

// this function makes a search and show the elements on page
export function performSearch(
  query,
  container,
  list_elements,
  divSelectedParticipants
) {
  if (query.trim() === "") {
    container.empty();
    divSelectedParticipants.css({ display: "block" });
  } else {
    divSelectedParticipants.css({ display: "none" });
    searchUsers(query)
      .then((response) => response.json())
      .then((data) => {
        container.empty();
        data.profiles.forEach((result) => {
          if (!list_elements.includes(`${result.profile_id}`)) {
            container.append(
              profileElement(result.profile_id, result.photo, result.name)
            );
          }
        });
      });
  }
}

// this function add the element to the container
export function addParticipantToContainer(
  element,
  listParticipantsTosend,
  selectedParticipants,
  container,
  currentInput
) {
  const profile_id = element.dataset.profileid;

  if (!listParticipantsTosend.includes(profile_id)) {
    element.classList.remove("btn");
    element.innerHTML +=
      '<i class="btn ms-auto bi bi-trash text-danger small remove-participant" style="font-size: x-large"></i>';
    selectedParticipants.append(element);
    listParticipantsTosend.push(profile_id);
  }

  selectedParticipants.css({ display: "block" });
  container.empty();
  currentInput.val("");
}
