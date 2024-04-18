class FolderService {
  // This class is responsible for calling backend API for Folder Resource
  async createFolder(new_folder_name) {
    new_folder_name || throwError("Expected New Folder name is missing");
    const resp = await fetch("/drive/folders/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCSRFToken(),
      },
      body: JSON.stringify({
        folder_name: new_folder_name,
      }),
    });
    resp.status !== 200 && throwError("Create Folder request failed", resp);
    return resp;
  }

  async renameFolder(folder_id, folder_name) {
    (folder_id && folder_name) ||
      throwError("Expected Folder ID and Folder Name is missing");
    let resp = await fetch("/drive/folders/" + folder_id + "/", {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCSRFToken(),
      },
      body: JSON.stringify({
        folder_name,
      }),
    });
    resp.status !== 200 && throwError("Rename Folder request failed", resp);
    resp = await resp.json();
    return resp;
  }

  async deleteFolder(folder_id) {
    folder_id || throwError("Expected Folder ID is missing");
    console.log(folder_id);
    let resp = await fetch("/drive/folders/" + folder_id + "/", {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCSRFToken(),
      },
    });
    resp.status !== 200 && throwError("Delete Folder request failed", resp);
    resp = await resp.json();
    return resp;
  }
}
