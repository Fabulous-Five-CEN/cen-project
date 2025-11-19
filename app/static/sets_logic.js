const userSetsList      = document.getElementById('userSetsList');

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
                const cardCount = countCardsInSet(name);
                
                const card = document.createElement('div');
                card.className = 'card border-0 shadow-sm';

                const body = document.createElement('div');
                body.className = 'card-body py-2';

                body.innerHTML = `
                <div class="d-flex justify-content-between align-items-start">
                    <div class="flex-grow-1">
                    <div class="fw-semibold">${name}</div>
                    ${description ? `<div class="small text-muted mt-1">${description}</div>` : ''}
                    <div class="small text-muted mt-1">${cardCount} card${cardCount !== 1 ? 's' : ''}</div>
                    </div>
                    <div class="d-flex gap-2">
                    <button
                        class="btn btn-sm btn-outline-secondary"
                        data-action="editSet"
                        data-set-index="${index}">
                        Edit
                    </button>
                    <button
                        class="btn btn-sm btn-outline-primary"
                        data-action="viewSet"
                        data-set-name="${name}">
                        View
                    </button>
                    <button
                        class="btn btn-sm btn-outline-danger"
                        data-action="deleteSet"
                        data-set-name="${name}">
                        Delete
                    </button>
                    </div>
                </div>
                `;

            card.appendChild(body);
            userSetsList.appendChild(card);
            });
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
                    editSetIndex = parseInt(index);
                    const setObj = userSets[editSetIndex];
                    
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
                    activeSetFilter = name;          // remember which set we're showing
                    renderCards();                   // re-render All Cards using filter

                    window.location.href = 'cards.html';
                    return;
                }

                // DELETE: remove the set everywhere
                if (action === 'deleteSet') {
                    if (!window.confirm(
                    `Delete set "${name}"? This will remove it from cards but not delete the cards themselves.`
                    )) {
                    return;
                    }

                    // 1) Remove from userSets array + localStorage
                    userSets = userSets.filter(s => s.name !== name);
                    localStorage.setItem('userSets', JSON.stringify(userSets));

                    // 2) Remove from the "Add to set" dropdown in the Card modal
                    Array.from(window.setsEl.options).forEach(o => {
                    if (o.value === name) o.remove();
                    });

                    // 3) Remove from the Practice set dropdown
                    Array.from(window.practiceSetSelect.options).forEach(o => {
                    if (o.value === name) o.remove();
                    });

                    // 4) Remove this set tag from any cards that used it
                    cards = cards.map(card => {
                    const oldSets = Array.isArray(card.sets) ? card.sets : [];
                    const newSets = oldSets.filter(s => s !== name);
                    return { ...card, sets: newSets };
                    });
                    localStorage.setItem('cards', JSON.stringify(cards));

                    // 5) If we were viewing this set, clear the filter
                    if (activeSetFilter === name) {
                    activeSetFilter = null;
                    }

                    // 6) Re-render UI
                    renderUserSets();
                    renderCards();
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

                if (editSetIndex !== null) {
                // EDITING existing set
                const oldName = userSets[editSetIndex].name;
                
                // Update the set object
                userSets[editSetIndex] = { name, description };
                localStorage.setItem('userSets', JSON.stringify(userSets));
                
                // If name changed, update it everywhere
                if (oldName !== name) {
                    // Update in card modal dropdown
                    Array.from(window.setsEl.options).forEach(o => {
                    if (o.value === oldName) {
                        o.value = name;
                        o.text = name;
                    }
                    });
                    
                    // Update in practice dropdown
                    Array.from(window.practiceSetSelect.options).forEach(o => {
                    if (o.value === oldName) {
                        o.value = name;
                        o.text = name;
                    }
                    });
                    
                    // Update in all cards that reference this set
                    cards = cards.map(card => {
                    if (Array.isArray(card.sets)) {
                        return {
                        ...card,
                        sets: card.sets.map(s => s === oldName ? name : s)
                        };
                    }
                    return card;
                    });
                    localStorage.setItem('cards', JSON.stringify(cards));
                    
                    // Update active filter if it was showing this set
                    if (activeSetFilter === oldName) {
                    activeSetFilter = name;
                    }
                }
                
                editSetIndex = null;
                renderUserSets();
                renderCards();
                
                } else {
                // CREATING new set
                // 1) Add to selects so you can assign cards to this set
                addSetOption({ name, description });

                // 2) Persist the set
                if (!userSets.some(s => s.name === name)) {
                    userSets.push({ name, description });
                    localStorage.setItem('userSets', JSON.stringify(userSets));
                    renderUserSets(); // re-render My Sets list
                }
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
            editSetIndex = null;
            document.getElementById('setName').value = '';
            document.getElementById('setDesc').value = '';
            document.getElementById('setModalTitle').textContent = 'New Set';
            });
        });