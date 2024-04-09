describe('Testing Drive Core Functionality', () => {
    beforeEach(() => {
        cy.visit('http://localhost:9900/drive/login/')
        cy.get('[data-cy="username"]').type("user1")
        cy.get('[data-cy="password"]').type("XBtgPGU9")
        cy.get('[data-cy="login-btn"]').click()
      })

    it('Add New Folder', () => {
        cy.get('[data-cy="new-folder-btn"]').click()
        cy.get('[data-cy="new-folder-input"]').should('be.visible')
        cy.wait(1000)
        cy.get('[data-cy="new-folder-cancel-btn"]').click()
        cy.get('[data-cy="new-folder-input"]').should('not.be.visible')
        cy.get('[data-cy="new-folder-btn"]').click()
        cy.get('[data-cy="new-folder-input"]').type("Folder-1")
        cy.get('[data-cy="new-folder-create-btn"').click()
        cy.get('[data-folder-name="Folder-1"]').should('exist')
    })

    it('Rename Folder', () => {
        cy.get('[data-folder-name="Folder-1"] > [data-cy="folder-rename"').first().click()
        cy.wait(1000)
        cy.get('[data-cy="folder-rename-input"]').filter(":visible").first().clear().type('Folder-2')
        cy.get('[data-cy="rename-folder-update-btn"]').filter(":visible").first().click()
        cy.wait(1000)
        cy.get('[data-folder-name="Folder-2"]').should('exist')
    })
    it('Delete Folder', () => {
        cy.get('[data-folder-name="Folder-2"]').should('exist')
        cy.get('[data-folder-name="Folder-2"]').get('[data-cy="folder-delete"').first().click()
        cy.wait(1000)
        cy.get('[data-cy="delete-yes"]').filter(":visible").first().click()
        cy.wait(1000)
        cy.get('[data-folder-name="Folder-2"]').should('not.exist')
    })
})
