class FileUploader {
  static file_upload_counter = 0;
  constructor(file, folder) {
    FileUploader.file_upload_counter += 1;
    this.file_upload_id = FileUploader.file_upload_counter;
    this.file = file;
    this.folder = "";
    if (folder) {
      this.folder = folder;
    }
    this.upload_queue_div = domHandler.getUploadQueueDiv();
    this.upload_queue_collapse_element =
      domHandler.getUploadQueueCollapseElemet();
  }

  async uploadFile() {
    // Add it to Upload Queue while it is being uploaded
    // This being  async function will ensure api calls will happen Synchronously 
    // Only then will it be removed from the Upload Queue
    // File Upload ID is used to identify the List Item HTML Elem in the Upload Queue Div
    this.addToFileQueueDisplay();
    const presigned_url_resp = await fileService.getPresignedUrlForUpload(
      this.file.name,
    );
    const object_key = await presigned_url_resp.object_key;
    await fileService.uploadFileUsingPresignedURL(
      presigned_url_resp.presigned_url,
      this.file,
    );
    const create_file_resp = await fileService.createFile(
      object_key,
      this.file.name.trim(),
      this.folder.trim(),
    );
    this.removeFromFileQueueDisplay();
    // We cannot refresh the browser after the file is added otherwise it will abort ongoing uploads to S3
    // That's why explicitily adding file object to the view. 
    // Once the page refreshes backend will render the same View
    addToFileListView(create_file_resp.id, this.file);
  }

  addToFileQueueDisplay() {
    const file_upload_item = document.createElement("li");
    file_upload_item.classList.add("list-group-item");
    file_upload_item.id = this.file_upload_id;
    file_upload_item.innerHTML = `<i class="far fa-file"></i><a href="#" class="ps-2"> ${(this.file.name)}</a>`;
    this.upload_queue_div.appendChild(file_upload_item);
    this.upload_queue_collapse_element.classList.add("show");
  }

  removeFromFileQueueDisplay() {
    const file_upload_item = document.getElementById(this.file_upload_id);
    file_upload_item.remove();
  }
}
