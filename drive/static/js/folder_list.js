// const csrf_token = document.getElementsByName('csrfmiddlewaretoken')[0].value;
// TODO: Make sure to remove all the console.logs
//TODO: Make sure this one is correct
function getCSRFToken() {
  const csrfCookie = document.cookie.match(/csrftoken=([^ ;]+)/);
  return csrfCookie ? csrfCookie[1] : '';
} 

const csrf_token = getCSRFToken('csrftoken'); //TODO: This is not the right way to do CSRF firgure it out 
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

file_upload_input = document.getElementById('file-upload')

var file = ""; //TODO: how to not use var here ? if we use let it will give issue in getting upload url as in reader.onload file will be null 
var folder = "";
file_upload_input.addEventListener('change' ,(e) => {
  file = file_upload_input.files[0]
  folder = document.getElementById('current_folder_id').innerText
  console.log(file)
  reader.readAsDataURL(file)
  // window.location.reload();
  //TODO: Handle Error
})

const reader = new FileReader();
reader.onload = (e) => {
  console.log(reader)
  console.log(file)
  const resp = fetch('/drive/files/upload-url?file_name='+encodeURIComponent(file.name), { // TODO: Check if file exists
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrf_token, 
    },
  });

  resp.then((resp) => {
    resp.json().then((resp) => {
        const  upload_resp = fetch(resp.presigned_url, {
          method: 'PUT',
          body: file,
          headers: {
            'Content-Type': 'application/octet-stream',
          }
        })
        object_key = resp.object_key
        upload_resp.then((resp) => {
        
          // window.location.reload()
          // TODO: firsst check the response 
          const create_file_resp = fetch('/drive/files/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': csrf_token,  
            },
            body: JSON.stringify({
              "object_key": object_key,
              "file_name": file.name,
              "folder": folder

            })
          })
          create_file_resp.then((create_file_resp) => {
            create_file_resp.json().then((create_file_resp) => {
              console.log(create_file_resp)
              window.location.reload()
            })
          })
          resp.json().then(resp => {
            console.log(resp)
            // TODO: Add upload progress UI 
          })
        })
    })
  })
  // TODO: Maybe use async await here ?
};


// TODO: Add option for double click instead of single click ?
document.querySelectorAll('.file-item')
.forEach((item) => {
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
})


// TODO: convert this into higher order function

// TODO: This shouldn't be empty find a better way to do this
let selected_file_id = ""

document.querySelectorAll('.rename-file-modal-trigger')
.forEach((item) => {
    item.addEventListener('click', (e) => {
    // selected_file_id = e.target.parent.getAttribute('data-file-id')
    selected_file_id = item.parentElement.getAttribute('data-file-id')
    selected_folder_name = item.parentElement.getAttribute('data-file-name')
    // TODO: Add Autofocus
    document.getElementById('rename-file-input').value = selected_folder_name
  })

})

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


document.querySelectorAll('.delete-file-modal-trigger')
.forEach((item) => {
    item.addEventListener('click', (e) => {
    // selected_file_id = e.target.parent.getAttribute('data-file-id')
    selected_file_id = item.parentElement.getAttribute('data-file-id')
    selected_folder_name = item.parentElement.getAttribute('data-file-name')
    document.getElementById('delete-file-name-display').innerText = `"${selected_folder_name}"`
  })
})



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


