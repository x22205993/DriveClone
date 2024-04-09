function getCSRFToken() {
  return document.cookie.split(';').filter(elem => elem.startsWith('csrftoken='))[0].split('=')[1]
} 

const csrf_token = getCSRFToken();
document.getElementById('create-folder').addEventListener('click' ,(e) => {
    const new_folder_name = document.getElementById('new-folder-name').value;
    console.log(new_folder_name) //TODO: Remove all console log stmts
    const resp = fetch('/drive/folders/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrf_token, 
      },
      body: JSON.stringify({
        "folder_name": new_folder_name
      }),
    });
    resp.then(()=> window.location.reload())
    //TODO: Handle Error
})

let file_upload_input = document.getElementById('file-upload')


file_upload_input.addEventListener('change' ,(e) => {
  const folder = document.getElementById('current_folder_id').innerText
  const file = file_upload_input.files[0]
  const file_uploader = new FileUploader(file, folder)
  file_uploader.uploadFile()
  file_upload_input.value = ""
})

// TODO: Move this to another file infact rename this js file and refactor the content
class FileUploader {
  static file_upload_counter = 0;
  constructor(file, folder) {
    FileUploader.file_upload_counter += 1
    this.file_upload_id = FileUploader.file_upload_counter
    this.file = file
    this.folder = folder
  }

  //TODO: Handle Error
  async uploadFile() {
    console.log(this.file.name)
    addToFileQueueDisplay(this.file_upload_id, this.file.name)
    let presigned_url_resp = await fetch('/drive/files/upload-url?file_name='+encodeURIComponent(this.file.name), { // TODO: Check if file exists
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrf_token, 
      },
    });
    presigned_url_resp = await presigned_url_resp.json()
    let object_key = await presigned_url_resp.object_key
    let upload_resp = await fetch(presigned_url_resp.presigned_url, {
      method: 'PUT',
      body: this.file,
      headers: {
        'Content-Type': 'application/octet-stream',
      }
    })
    console.log(this.file.name, this.file_upload_id)
    
    let create_file_resp = await fetch('/drive/files/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrf_token,  
      },
      body: JSON.stringify({
        "object_key": object_key,
        "file_name": this.file.name,
        "folder": this.folder
      })
    })
    create_file_resp = await create_file_resp.json()
    console.log(create_file_resp)
    let file_id = create_file_resp.id 
    console.log(this.file.name, this.file_upload_id)
    removeFromFileQueueDisplay(this.file_upload_id)
    addToFileListView(file_id, this.file) //TODO: Check if the file actually ha beend created before adding it to the list
  }

}

const upload_queue_div = document.getElementById('upload-queue')
function addToFileQueueDisplay(file_upload_id, file_name) {
    const file_info_div = document.createElement('div')
    file_info_div.id = file_upload_id
    file_info_div.innerText = `${file_name}`
    upload_queue_div.appendChild(file_info_div)
}


function removeFromFileQueueDisplay(file_upload_id) {
  file_info_div = document.getElementById(file_upload_id) //TODO: Check for file 
  file_info_div.remove() // TODO: Is removing element a good way of doing this
}

function addToFileListView(file_id, file) {
  let file_items_list = document.getElementById('file-items')
  let file_item_node = document.createElement('li')
  file_item_node.dataset.fileId = file_id
  file_item_node.dataset.fileName = file.name
  //TODO: Move this somehere else 
  file_item_node.innerHTML = `
  <a role="button" class="file-item pe-auto" data-file-id="${file_id}"> ${file.name} </a> 
  <button class="btn btn-primary rename-file-modal-trigger" type="button" data-bs-target="#modal-2" data-bs-toggle="modal">Rename</button>
  <button class="btn btn-primary delete-file-modal-trigger" type="button" data-bs-target="#modal-3" data-bs-toggle="modal">Delete</button>`
  let file_item_rename_btn = file_item_node.querySelector('.rename-file-modal-trigger')
  let file_item_delete_btn = file_item_node.querySelector('.delete-file-modal-trigger')
  let file_item_link = file_item_node.querySelector('.file-item')
  addRenameEventToItem(file_item_rename_btn)
  addDeleteEventToItem(file_item_delete_btn)
  addDownloadEventToItem(file_item_link)
  file_items_list.appendChild(file_item_node)
}

// TODO: Add option for double click instead of single click ?
function addDownloadEventToItems() {
document.querySelectorAll('.file-item').forEach(item => addDownloadEventToItem(item))
}

function addDownloadEventToItem(item) {
  item.addEventListener('click', (e) => {
    const file_id = item.getAttribute('data-file-id')
    const resp = fetch(
      '/drive/files/'+file_id+'/download-url/', {
        method: 'GET'
      }
    )
    resp.then((resp) => {
      resp.json().then((resp) => {
        // TODO: IS this safe to do ?
        window.location.href = resp.presigned_url
      })
    })
  })
}

addDownloadEventToItems()

// TODO: convert this into higher order function
// TODO: This shouldn't be empty find a better way to do this
let selected_file_id = ""

function addRenameEventsToItems() {
  document.querySelectorAll('.rename-file-modal-trigger').forEach(item => addRenameEventToItem(item))
}

function addRenameEventToItem(item) {
  item.addEventListener('click', (e) => {
    // selected_file_id = e.target.parent.getAttribute('data-file-id')
    selected_file_id = item.parentElement.getAttribute('data-file-id')
    selected_folder_name = item.parentElement.getAttribute('data-file-name')
    // TODO: Add Autofocus
    document.getElementById('rename-file-input').value = selected_folder_name
  })
}

addRenameEventsToItems() 

function rename_file() {
  const file_name = document.getElementById('rename-file-input').value
  console.log(selected_file_id)
  const resp = fetch(
    '/drive/files/'+selected_file_id+'/', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrf_token, 
      },
      body: JSON.stringify({
        "file_name": file_name
      })
    }
  )
  resp.then((resp) => {
    resp.json().then((resp) => {
        console.log(resp)
        window.location.reload()
    })
  })
}

function addDeleteEventToItems() {
  document.querySelectorAll('.delete-file-modal-trigger').forEach(item => addDeleteEventToItem(item))
}

function addDeleteEventToItem(item) {
  item.addEventListener('click', (e) => {
    // selected_file_id = e.target.parent.getAttribute('data-file-id')
    selected_file_id = item.parentElement.getAttribute('data-file-id')
    selected_folder_name = item.parentElement.getAttribute('data-file-name')
    document.getElementById('delete-file-name-display').innerText = `"${selected_folder_name}"`
  })
}

addDeleteEventToItems() //TODO: Move global code to one place


function delete_file() {
  // TODO: find a better way to get selected_file_id
 console.log("delete file called")
 console.log(selected_file_id)
 const resp = fetch(
   '/drive/files/'+selected_file_id+'/', {
     method: 'DELETE',
     headers: {
       'Content-Type': 'application/json',
       'X-CSRFToken': csrf_token, 
     }
   }
 )
 resp.then((resp) => {
   resp.json().then((resp) => {
       console.log(resp)
       window.location.reload()
   })
 })

}

let selected_folder_id = ""

document.querySelectorAll('.rename-folder-modal-trigger')
.forEach((item) => {
    item.addEventListener('click', (e) => {
    // selected_folder_id = e.target.parent.getAttribute('data-folder-id')
    selected_folder_id = item.parentElement.getAttribute('data-folder-id')
    selected_folder_name = item.parentElement.getAttribute('data-folder-name')
    // TODO: Add Autofocus
    document.getElementById('rename-folder-input').value = selected_folder_name
  })

})

function rename_folder() {
  const folder_name = document.getElementById('rename-folder-input').value
  console.log(selected_folder_id)
  const resp = fetch(
    '/drive/folders/'+selected_folder_id+'/', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrf_token, 
      },
      body: JSON.stringify({
        "folder_name": folder_name
      })
    }
  )
  resp.then((resp) => {
    resp.json().then((resp) => {
        console.log(resp)
        window.location.reload()
    })
  })
}


document.querySelectorAll('.delete-folder-modal-trigger')
.forEach((item) => {
    item.addEventListener('click', (e) => {
    // selected_file_id = e.target.parent.getAttribute('data-file-id')
    selected_folder_id = item.parentElement.getAttribute('data-folder-id')
    selected_folder_name = item.parentElement.getAttribute('data-folder-name')
    folder_is_empty = item.parentElement.getAttribute('data-folder-is-emtpy')
    document.getElementById('delete-folder-name-display').innerText = `"${selected_folder_name}"`
    if (!parseInt(folder_is_empty)) {
      document.getElementById('folder-has-content-warning').innerText = "The folder contains files. "
    }
  })
})

function delete_folder() {
  // TODO: find a better way to get selected_folder_id
 console.log("delete folder called")
 console.log(selected_folder_id)
 const resp = fetch(
   '/drive/folders/'+selected_folder_id+'/', {
     method: 'DELETE',
     headers: {
       'Content-Type': 'application/json',
       'X-CSRFToken': csrf_token, 
     }
   }
 )
 resp.then((resp) => {
   resp.json().then((resp) => {
       console.log(resp)
       window.location.reload()
   })
 })
}