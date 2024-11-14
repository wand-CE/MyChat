import {
    performSearch,
    addParticipantToContainer,
} from "./participantManager.js";
import {profileElement, csrftoken} from "./principalsFunctions.js";

const resultsContainer = $("#groupParticipants");
const currentGroupParticipants = $("#participants_group");
const searchParticipantsBar = $("#searchGroupParticipants");
const saveGroupButton = $("#saveGroupData");
let elementsOnselected = [];

export function populateGroupParticipants(participants) {
    elementsOnselected = [];
    currentGroupParticipants.empty();

    for (let i = 0; i < participants.names.length; i++) {
        let element = profileElement(
            participants.profiles_ids[i],
            participants.photos[i],
            participants.names[i]
        );

        let elementProfile = document.createElement("div");
        elementProfile.innerHTML = element;

        addParticipantToContainer(
            elementProfile.children[0],
            elementsOnselected,
            currentGroupParticipants,
            resultsContainer,
            searchParticipantsBar
        );
    }
}

resultsContainer.click((event) =>
    addParticipantToContainer(
        event.target,
        elementsOnselected,
        currentGroupParticipants,
        resultsContainer,
        searchParticipantsBar
    )
);

searchParticipantsBar.on("input", function () {
    const query = $(this).val();
    performSearch(
        query,
        resultsContainer,
        elementsOnselected,
        currentGroupParticipants
    );
});

currentGroupParticipants.on("click", ".remove-participant", (event) => {
    const parent = event.target.closest(".list-group-item");
    if (parent) {
        let index = elementsOnselected.indexOf(parent.dataset.profileid);
        elementsOnselected.splice(index, 1);
        parent.remove();
    }
});

saveGroupButton.on("click", (event) => {
    let groupMenu = document.querySelector(".group-menu");
    let chat_uuid = groupMenu.dataset.chat_uuid;
    fetch("/group/modify/", {
        method: "POST",
        headers: {"X-CSRFToken": csrftoken},
        credentials: "same-origin",
        body: JSON.stringify({
            chat_uuid: chat_uuid,
            listProfiles: elementsOnselected,
        }),
    });

    event.target.closest(".modal").querySelector(".close").click();
});
