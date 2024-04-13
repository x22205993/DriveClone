class FileService {
    async getPresignedUrlForUpload(file_name) {
        file_name || throwError("Expected File Name is missing")
        let resp = await fetch('/drive/files/upload-url?file_name='+encodeURIComponent(file_name), { // TODO: Check if file exists
            method: 'GET',
            headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrf_token, 
            },
        })
        resp.status != 200 && throwError("Get Upload URL request failed", resp)
        resp = await resp.json()
        return resp
    }
  
    async getPresignedUrlForDownload(file_id) {
        file_id || throwError("Expected File ID is missing")
        let resp = await fetch('/drive/files/'+file_id+'/download-url/')
        resp.status != 200 && throwError("Get Download URL request failed", resp)
        resp = await resp.json()
        return resp
    }
  
    async uploadFileUsingPresignedURL(presigned_url, file) {
        (presigned_url && file) || throwError("Expected Upload URL is missing")
        let resp = await fetch(presigned_url, {
            method: 'PUT',
            body: file,
            headers: {
            'Content-Type': 'application/octet-stream',
            }
        }) 
        resp.status != 200 && throwError("Upload File request failed", resp)
        return resp
    }
  
    async createFile(object_key, file_name, folder_id) {
        (object_key && file_name ) || throwError("Expected Object Key, File Name is missing")
        console.log("CREATE FILED" , object_key, file_name, folder_id)
        let resp = await fetch('/drive/files/', {
            method: 'POST',
            headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrf_token,  
            },
            body: JSON.stringify({
            "object_key": object_key,
            "file_name": file_name,
            "folder_id": folder_id
            })
        })
        resp.status != 200 && throwError("Create File request failed", resp)
        resp = await resp.json()
        return resp
    }
  
    async updateFileName(file_id, file_name) {
        (file_id && file_name) || throwError("Expected File ID, File Name is missing")
        let resp = await fetch(
            '/drive/files/'+file_id+'/', {
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
        resp.status != 200 && throwError("Update File Name request failed", resp)
        resp = await resp.json()
        return resp
    }
  
    async deleteFile(file_id) {
        file_id || throwError("Expected File ID is missing")
        let resp = await fetch(
            '/drive/files/'+file_id+'/', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrf_token, 
            }
            }
        )
        resp.status != 200 && throwError("Delete File request failed", resp)
        resp = await resp.json()
        return resp
    }
  }
  