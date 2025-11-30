const userSetsList      = document.getElementById('userSetsList');
// Load sets from script tag
const userSetsScript = document.getElementById('sets-data');
let userSets = userSetsScript ? JSON.parse(userSetsScript.textContent) : [];

        // PRODUCTION: inject a set name into both selects
        function addSetOption(setObj) {
            const name = typeof setObj === 'string' ? setObj : setObj.name;
            if (!name) return;

            // Add to Add-Card modal's select
            if (window.setsEl) {
                let exists = Array.from(window.setsEl.options).some(o => o.value === name);
                if (!exists) {
                    const opt = new Option(name, name);
                    window.setsEl.appendChild(opt);
                }
            }

            // Add to Practice select
            if (window.practiceSetSelect) {
                let exists = Array.from(window.practiceSetSelect.options).some(o => o.value === name);
                if (!exists) {
                    const opt2 = new Option(name, name);
                    window.practiceSetSelect.appendChild(opt2);
                }
            }
        }

        // Count cards in a specific set
        function countCardsInSet(setName) {
            return cards.filter(card => 
            Array.isArray(card.sets) && card.sets.includes(setName)
            ).length;
        }

        // PRODUCTION: render the list of sets on the "My Sets" tab
        // Show user-created sets on My Sets tab, with View + Delete buttons
        function renderUserSets() {
            if (!userSetsList) return;

            const emptyState = document.getElementById('emptySetsMessage');

            userSetsList.innerHTML = '';

            if (!userSets.length) {
                // No sets → show empty message
                if (emptyState) emptyState.classList.remove('d-none');
                return;
            }

            // We have sets → hide empty message
            if (emptyState) emptyState.classList.add('d-none');

            userSets.forEach((setObj, index) => {
                const name = setObj.name;
                const description = setObj.description || '';
                const cardCount = setObj.card_count || 0;
                
                const card = document.createElement('div');
                card.className = 'card border-0 shadow-sm';

                const body = document.createElement('div');
                body.className = 'card-body py-2';

                body.innerHTML = `
                <div class="d-flex justify-content-between align-items-center">
                    <div class="flex-grow-1">
                    <div class="fw-semibold">${name}</div>
                    ${description ? `<div class="small text-muted mt-1">${description}</div>` : ''}
                    <div class="small text-muted mt-1">${cardCount} card${cardCount !== 1 ? 's' : ''}</div>
                    </div>
                    <div class="d-flex gap-2">
                <button
                    class="btn btn-sm btn-secondary rounded-pill btn-fixed-width"
                    data-action="editSet"
                    data-set-id="${setObj.id}">
                    Edit
                </button>
                <button
                    class="btn btn-sm btn-primary rounded-pill btn-fixed-width"
                    data-action="viewSet"
                    data-set-id="${setObj.id}">
                    View
                </button>
                <button
                    class="btn btn-sm btn-danger rounded-pill btn-fixed-width"
                    data-action="deleteSet"
                    data-set-id="${setObj.id}">
                    Delete
                </button>

                    </div>
                </div>
                `;

            card.appendChild(body);
            userSetsList.appendChild(card);
            });

            document.getElementById("setsCount").textContent = `(${userSets.length} set${userSets.length === 1 ? '' : 's'})`;
        }

        // PRODUCTION: Handle clicks on the My Sets list (View + Delete + Edit)
        if (userSetsList) {
            userSetsList.addEventListener('click', (e) => {
                const action = e.target.dataset.action;
                const name   = e.target.dataset.setName;
                const index  = e.target.dataset.setIndex;
                
                if (!action) return;

                // EDIT: open modal with existing name and description
            if (action === 'editSet') {
                const setId = parseInt(e.target.dataset.setId);
                const setObj = userSets.find(s => s.id === setId);
                editSetId = setId;

                document.getElementById('setName').value = setObj.name;
                document.getElementById('setDesc').value = setObj.description || '';
                document.getElementById('setModalTitle').textContent = 'Edit Set';

                const modalEl = document.getElementById('setEditModal');
                const modal = new bootstrap.Modal(modalEl);
                modal.show();
                return;
            }

                // VIEW: jump to All Cards and filter by this set
                if (action === 'viewSet') {
                    const setId = parseInt(e.target.dataset.setId);
                    if (!setId) return;

                    window.location.href = `/sets/view/${setId}`;
                    return;
                }
                    
                // DELETE: remove the set everywhere
                if (action === 'deleteSet') {
                    // show popup module
                    const setObj = userSets.find(s => s.id === parseInt(e.target.dataset.setId));
                    if (!setObj) return;

                    const deleteModalEl = document.getElementById('deleteConfirmModal');
                    const deleteModal = new bootstrap.Modal(deleteModalEl);
                    deleteModal.show();

                    const confirmBtn = document.getElementById('confirmDeleteBtn');

                    // Remove previous click handlers to avoid stacking
                    confirmBtn.replaceWith(confirmBtn.cloneNode(true));
                    const newConfirmBtn = document.getElementById('confirmDeleteBtn');

                    newConfirmBtn.addEventListener('click', () => {
                        fetch(`/sets/delete/${setObj.id}`, {
                            method: 'DELETE'
                        })
                        .then(res => res.json())
                        .then(resp => {
                            // Remove from in-memory list
                            userSets = userSets.filter(s => s.id !== setObj.id);
                            renderUserSets();
                            deleteModal.hide();
                        });
                    });
                }


            });
        }

        const setForm = document.getElementById('setForm')
        
        // PRODUCTION: handle New Set form submit (creates real set names)
        if (setForm) {
            setForm.addEventListener('submit', (e) => {
                e.preventDefault();

                const nameInput = document.getElementById('setName');
                const descInput = document.getElementById('setDesc');

                const name = nameInput.value.trim();
                const description = descInput.value.trim();
                
                if (!name) return;

        if (editSetId) {
            // EDIT SET USING API
            fetch(`/sets/edit/${editSetId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, description })
            })
            .then(res => res.json())
            .then(updated => {
                // Replace the updated set in our local memory
                const idx = userSets.findIndex(s => s.id === editSetId);
                if (idx !== -1) userSets[idx] = updated.set;

                renderUserSets();
            });
        } else {
            // CREATE NEW SET USING API
            fetch('/sets/new', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, description })
            })
            .then(res => res.json())
            .then(resp => {
                // Prepend new set to the top of the list
                userSets.unshift(resp.set);
                renderUserSets();
            });
        }


                // 3) Clear + close modal
                nameInput.value = '';
                descInput.value = '';

                const modalEl = document.getElementById('setEditModal');
                const modal = bootstrap.Modal.getInstance(modalEl) || new bootstrap.Modal(modalEl);
                modal.hide();
            });
        }

        // When opening set modal via "New Set +" button, clear editSetIndex
        const setModalTrigger = document.querySelectorAll('[data-bs-target="#setEditModal"]');
        
        setModalTrigger.forEach(btn => {
            btn.addEventListener('click', () => {
            editSetId = null;
            document.getElementById('setName').value = '';
            document.getElementById('setDesc').value = '';
            document.getElementById('setModalTitle').textContent = 'New Set';
            });
        });