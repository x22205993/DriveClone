class DomHandler {
    constructor() {
       this.create_folder_button = this.getById('create-folder')
       this.file_upload_input = this.getById('file-upload')
       this.curent_folder_elem = this.getById('current-folder-id')
       this.upload_queue_div = this.getById('upload-queue')
       this.upload_queue_collapse_elem = this.getById('collapse-1')
       this.file_items_list_elem = this.getById('file-items')
       this.item_card_template = this.getById('item-card-template')
       this.error_alert_div = this.getById('error-alert')
       this.error_alert_message_div = this.getById('error-alert-message')
       this.hide_error_alert_button = this.getById('hide-data-alert')
       this.delete_folder_modal_triggers = this.getAll('.delete-folder-modal-trigger')
       this.rename_folder_modal_triggers = this.getAll('.rename-folder-modal-trigger')
       this.delete_file_modal_triggers = this.getAll('.delete-file-modal-trigger')
       this.rename_file_modal_triggers = this.getAll('.rename-file-modal-trigger')
       this.file_item_links = this.getAll('.file-item-link')
       this.all_validations_models = document.querySelectorAll('.validate-modal')
    }
 
    getById(id) {
     return document.getElementById(id)
    }
 
    getAll(selector) {
       return document.querySelectorAll(selector)
    }
 
    getNewFolderDialogInput() {
       return this.getById('new-folder-name')
    }
 
    getCreateFolderButton() {
       return this.create_folder_button
    } 
 
    getFileUploadInput() {
       return this.file_upload_input
    }
 
    getCurrentFolderElem() {
       return this.curent_folder_elem
    }
 
    getUploadQueueDiv() {
       return this.upload_queue_div 
    }
 
    getUploadQueueCollapseElemet() {
       return this.upload_queue_collapse_elem
    }
 
    getFileItemsListElem() {
       return this.file_items_list_elem
    }
 
    getItemCardTemplate() {
       return this.item_card_template
    }
 
    getItemLinkFromItemCard(item_card) {
       return item_card.querySelector('.file-item-link')
    }
 
    getRenameFileModalTriggerFromItemCard(item_card) {
       return item_card.querySelector('.rename-file-modal-trigger')    
    }
 
    getDeleteFileModalTriggerFromItemCard(item_card) {
       return item_card.querySelector('.delete-file-modal-trigger')
    }  
 
    getAllFileItemLinks() {
       return this.file_item_links
    }
 
    getAllRenameFileModalTriggers() {
       return this.rename_file_modal_triggers
    }
 
   getAllDeleteFileModalTriggers() {
     return this.delete_file_modal_triggers
   }
 
    getRenameModalFileNameInput() {
       return this.getById('rename-file-input')
    }
    
    getDeleteModalFileNameDisplay() {
       return this.getById('delete-file-name-display')
    }
 
    getRenameModalFolderNameInput() {
       return this.getById('rename-folder-input')
    }
 
    getAllRenameFolderModalTriggers() {
       return this.rename_folder_modal_triggers
    }
 
    getAllDeleteFolderModalTriggers() {
       return this.delete_folder_modal_triggers
    }
 
   getDeleteModalFolderNameDisplay() {
     return this.getById('delete-folder-name-display')
   }

   getDeleteModalContentWarningElem() {
    return this.getById('folder-has-content-warning')
   }
 
    getDataForFileElem(file_item_elem) {
        return file_item_elem.closest('[data-file-id]').dataset
    }

    getDataForFolderElem(folder_item_elem) {
        return folder_item_elem.closest('[data-folder-id]').dataset
    }

    getErrorAlertDiv() {
        return this.error_alert_div
    }

    getErrorAlertMessageDiv() {
        return this.error_alert_message_div
    }

    getHideErrorAlertButton() {
        return this.hide_error_alert_button
    }

    getCurrentModal() {
        return document.querySelector('.modal.show')
    }

    getCurrentModalBackdrop() {
        return document.querySelector('.modal-backdrop')
    }

    getCurrentModalButton() {
        return this.getCurrentModal().querySelector('.modal-ok-btn')
    }

    getCurrentModalErrorBox() {
        return this.getCurrentModal().querySelector('.modal-error-box')
    }
    getCurrentModalInput() {
        return this.getCurrentModal().querySelector('.modal-input')
    }

    getAllValidationModals() {
        return this.all_validations_models
    }
 }
 