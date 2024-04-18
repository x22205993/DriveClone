const folderService = new FolderService();
const fileService = new FileService();
const domHandler = new DomHandler();

let selected_file_id = "";
let selected_folder_id = "";

function getCSRFToken() {
  return document.cookie
    .split(";")
    .filter((elem) => elem.trim().startsWith("csrftoken="))[0]
    .split("=")[1];
}

function throwError(error, resp) {
  throw new Error(error, resp);
}

function showError(error_msg) {
  domHandler.getErrorAlertDiv().classList.remove("d-none");
  domHandler.getErrorAlertMessageDiv().innerText = error_msg;
}

function closeCurrentModal() {
  const current_modal = domHandler.getCurrentModal();
  const current_modal_backdrop = domHandler.getCurrentModalBackdrop();
  current_modal.classList.remove("show");
  current_modal_backdrop.classList.remove("show");
}

// Validation of File Name and Folder Name input in the Rename File, Rename Folder and New Folder Modal
/* eslint-disable no-unused-vars */
function validateItemName(e) {
  const button = domHandler.getCurrentModalButton();
  const input = domHandler.getCurrentModalInput();
  const error_div = domHandler.getCurrentModalErrorBox();
  const oldValue = input.dataset.oldValue;
  const inputValue = e.srcElement.value;
  const re = /^[a-zA-Z0-9_\-. ]*$/;
  input.classList.remove("is-invalid");
  error_div.innerText = "";
  if (!re.test(inputValue)) {
    button.disabled = true;
    input.classList.add("is-invalid");
    error_div.innerText =
      "Invalid Characters only letters, digits, _ - allowed";
    return;
  }
  if (inputValue === "") {
    button.disabled = true;
    input.classList.add("is-invalid");
    error_div.innerText = "Field is required";
    return;
  }
  // If the value is not changed we don't need to actually call API to update the name
  if (oldValue != null && inputValue === oldValue) {
    button.disabled = true;
    return;
  }
  button.disabled = false;
}

  // We cannot refresh the browser after the file is added otherwise it will abort ongoing uploads to S3
  // That's why explicitily adding file object to the view. 
  // Once the page refreshes backend will render the same View
/* eslint-disable no-unused-vars */
function addToFileListView(file_id, file) {
  const item_card = domHandler.getItemCardTemplate().content.cloneNode(true);
  const file_item_link = domHandler.getItemLinkFromItemCard(item_card);
  item_card.firstElementChild.dataset.fileId = file_id;
  item_card.firstElementChild.dataset.fileName = file.name;
  file_item_link.innerText = file.name;
  addRenameEventToItem(
    domHandler.getRenameFileModalTriggerFromItemCard(item_card),
  );
  addDeleteEventToItem(
    domHandler.getDeleteFileModalTriggerFromItemCard(item_card),
  );
  addDownloadEventToItem(file_item_link);
  domHandler.getFileItemsListElem().appendChild(item_card);
}

function addDownloadEventToItems() {
  domHandler
    .getAllFileItemLinks()
    .forEach((item) => addDownloadEventToItem(item));
}

function addDownloadEventToItem(item) {
  item.addEventListener("click", (e) => {
    const file_id = domHandler.getDataForFileElem(item).fileId;
    fileService
      .getPresignedUrlForDownload(file_id)
      .then((resp) => {
        window.location.href = resp.presigned_url;
      })
      .catch(() => {
        showError("File Download Failed");
      });
  });
}

function addRenameEventsToItems() {
  domHandler
    .getAllRenameFileModalTriggers()
    .forEach((item) => addRenameEventToItem(item));
}

function addRenameEventToItem(item) {
  item.addEventListener("click", (e) => {
    const data_attrs = domHandler.getDataForFileElem(item);
    selected_file_id = data_attrs.fileId;
    selected_file_name = data_attrs.fileName;
    domHandler.getRenameModalFileNameInput().value = selected_file_name;
    domHandler.getRenameModalFileNameInput().dataset.oldValue =
      selected_file_name;
  });
}

/* eslint-disable no-unused-vars */
function renameFile() {
  const file_name = domHandler.getRenameModalFileNameInput().value;
  fileService
    .updateFileName(selected_file_id, file_name)
    .then((resp) => {
      window.location.reload();
    })
    .catch(() => {
      closeCurrentModal();
      showError("File Rename Failed");
    });
}

function addDeleteEventToItems() {
  domHandler
    .getAllDeleteFileModalTriggers()
    .forEach((item) => addDeleteEventToItem(item));
}

function addDeleteEventToItem(item) {
  item.addEventListener("click", (e) => {
    const data_attrs = domHandler.getDataForFileElem(item);
    selected_file_id = data_attrs.fileId;
    selected_file_name = data_attrs.fileName;
    domHandler.getDeleteModalFileNameDisplay().innerText = `"${selected_file_name}"`;
  });
}

/* eslint-disable no-unused-vars */
function deleteFile() {
  fileService
    .deleteFile(selected_file_id)
    .then((resp) => {
      window.location.reload();
    })
    .catch(() => {
      closeCurrentModal();
      showError("Delete File Failed");
    });
}

function renameFolder() {
  const folder_name = domHandler.getRenameModalFolderNameInput().value;
  folderService
    .renameFolder(selected_folder_id, folder_name)
    .then((resp) => {
      window.location.reload();
    })
    .catch(() => {
      closeCurrentModal();
      showError("Rename Folder Failed");
    });
}

function deleteFolder() {
  folderService
    .deleteFolder(selected_folder_id)
    .then((resp) => {
      window.location.reload();
    })
    .catch(() => {
      closeCurrentModal();
      showError("Delete Folder Failed");
    });
}

// Add event listeners 
// To download file on click 
// Call rename function when the Rename button  in the rename modal is clicked
// Call delete function when the Delete button in the Delete modal is clicked
addDownloadEventToItems();
addRenameEventsToItems();
addDeleteEventToItems();

domHandler.getCreateFolderButton().addEventListener("click", (e) => {
  const new_folder_name = domHandler.getNewFolderDialogInput().value;
  folderService
    .createFolder(new_folder_name)
    .then((resp) => {
      window.location.reload();
    })
    .catch((resp) => {
      showError("Create Folder Failed");
    });
});

// Whenever file is selected in file menu this event is called which then invokes upload process
domHandler.getFileUploadInput().addEventListener("change", (e) => {
  const folder = domHandler.getCurrentFolderElem().innerText;
  const file = domHandler.getFileUploadInput().files[0];
  const file_uploader = new FileUploader(file, folder);
  file_uploader
    .uploadFile()
    .then(() => {})
    .catch(() => {
      showError("Upload File Failed");
    });
  domHandler.getFileUploadInput().value = "";
});

// We need to store the ID of the Selcted Folder or File whenever we open a modal for deletion or rename 
domHandler.getAllRenameFolderModalTriggers().forEach((item) => {
  item.addEventListener("click", (e) => {
    const data_attrs = domHandler.getDataForFolderElem(item);
    selected_folder_id = data_attrs.folderId;
    selected_folder_name = data_attrs.folderName;
    domHandler.getRenameModalFolderNameInput().value = selected_folder_name;
    domHandler.getRenameModalFolderNameInput().dataset.oldValue =
      selected_folder_name;
  });
});

domHandler.getAllDeleteFolderModalTriggers().forEach((item) => {
  item.addEventListener("click", (e) => {
    const data_attrs = domHandler.getDataForFolderElem(item);
    selected_folder_id = data_attrs.folderId;
    selected_folder_name = data_attrs.folderName;
    const folder_is_empty = data_attrs.folderIsEmpty;
    domHandler.getDeleteModalFolderNameDisplay().innerText = `"${selected_folder_name}"`;
    if (!parseInt(folder_is_empty)) {
      domHandler.getDeleteModalContentWarningElem().innerText =
        "The folder contains files. ";
    }
  });
});

// Cross Button Impleentation of the Error Alert 
domHandler.getHideErrorAlertButton().addEventListener("click", (evt) => {
  domHandler.getErrorAlertDiv().classList.add("d-none");
});

// Always reset vaidations when modal closes
domHandler.getAllValidationModals().forEach((modal) => [
  modal.addEventListener("hide.bs.modal", () => {
    const input = domHandler.getCurrentModalInput();
    const error_div = domHandler.getCurrentModalErrorBox();
    input.value = "";
    input.classList.remove("is-invalid");
    error_div.innerText = "";
  }),
]);
