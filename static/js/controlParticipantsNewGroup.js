import {
  performSearch,
  addParticipantToContainer,
} from "./participantManager.js";

const resultsContainer = $("#createGroupParticipants");
export const selectedParticipants = $("#id_participants");
const searchParticipantsBar = $("#searchParticipants");
export const elementsOnselected = [];

resultsContainer.click((event) =>
  addParticipantToContainer(
    event.target,
    elementsOnselected,
    selectedParticipants,
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
    selectedParticipants
  );
});

selectedParticipants.on("click", ".remove-participant", (event) => {
  const parent = event.target.closest(".list-group-item");
  if (parent) {
    let index = elementsOnselected.indexOf(parent.dataset.profileid);
    elementsOnselected.splice(index, 1);
    parent.remove();
  }
});
