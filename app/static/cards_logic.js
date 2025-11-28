/* =========================================================
    B) DOM REFS (PRODUCTION)
    ========================================================= */

    window.cardsGrid         = document.getElementById('cardsGrid');
    window.notesEl           = document.getElementById('notes');
    window.setsEl            = document.getElementById('cardSets');
    const activeSetIndicator = document.getElementById('activeSetIndicator');
    const activeSetLabel     = document.getElementById('activeSetLabel');
    const clearSetFilterBtn  = document.getElementById('clearSetFilter');

    /* =========================================================
     C) SETS HELPERS (PRODUCTION, but counts still TODO)
     ========================================================= */
    // PRODUCTION: read which sets were checked for a card
    function getSelectedSets() {
      return Array.from(window.setsEl.options)
      .filter(o => o.selected && o.value)
      .map(o => o.value);
    }

    // PRODUCTION: pre-select sets for Edit Card
    function setSelectedSets(values = []) {
      Array.from(window.setsEl.options).forEach(o => {
        o.selected = values.includes(o.value);
      });
    }

    /* =========================================================
    D) ALL CARDS GRID (PRODUCTION)
    ========================================================= */

    function renderCards() {
      if (!window.cardsGrid) {
        return;
      }

      window.cardsGrid.innerHTML = '';

      // Start with all cards, but keep their original index
      let list = cards.map((card, idx) => ({ card, idx }));

      // If a set filter is active, keep only cards in that set
      if (activeSetFilter) {
        list = list.filter(entry =>
          Array.isArray(entry.card.sets) &&
          entry.card.sets.includes(activeSetFilter)
        );
      }

      /* -----------------------------------------
        SHOW OR HIDE THE "ACTIVE SET" BANNER
        ----------------------------------------- */
      if (activeSetFilter) {
        activeSetIndicator.classList.remove('d-none');
        activeSetLabel.textContent = activeSetFilter;
      } else {
        activeSetIndicator.classList.add('d-none');
        activeSetLabel.textContent = '';
      }

      // Render whatever is in the list (filtered or not)
      list.forEach(({ card, idx }) => {
        const col = document.createElement('div');
        col.className = 'col-12 col-sm-6 col-md-4 col-lg-3';

        const wrapper = document.createElement('div');
        wrapper.className = 'card h-100';
        wrapper.dataset.index = idx;

        const body = document.createElement('div');
        body.className = 'card-body';

        const esLbl = document.createElement('div');
        esLbl.className = 'small text-muted';
        esLbl.textContent = 'Spanish';

        const esH = document.createElement('h5');
        esH.className = 'card-title mb-1';
        esH.textContent = card.es;

        const enLbl = document.createElement('div');
        enLbl.className = 'small text-muted';
        enLbl.textContent = 'English';

        const enP = document.createElement('p');
        enP.className = 'card-text mb-2';
        enP.textContent = card.en;

        body.append(esLbl, esH, enLbl, enP);

        // Optional notes
        if (card.notes) {
          const notesP = document.createElement('p');
          notesP.className = 'text-muted small mb-2';
          notesP.textContent = card.notes;
          body.appendChild(notesP);
        }

        // Badges (sets)
        if (card.sets?.length) {
          const badges = document.createElement('div');
          badges.className = 'd-flex flex-wrap gap-1 mb-2';
          card.sets.forEach(s => {
            const b = document.createElement('span');
            b.className = 'badge text-bg-light';
            b.textContent = s;
            badges.appendChild(b);
          });
          body.appendChild(badges);
        }

        const btnColumn = document.createElement('div');
        btnColumn.className = 'd-flex flex-column gap-1';
        btnColumn.style.cssText = 'position:absolute; top:8px; right:8px;';

        // Edit button
        const edit = document.createElement('button');
        edit.className = 'btn btn-sm btn-outline-primary rounded-circle';
        edit.dataset.action = 'editCard';
        edit.style.cssText = 'width:30px; height:30px; padding:0;';
        edit.innerHTML = '<i class="fa-solid fa-pencil"></i>';

        // Assign to sets button
        const assignSets = document.createElement('button');
        assignSets.className = 'btn btn-sm btn-outline-success rounded-circle';
        assignSets.dataset.action = 'assignSets';
        assignSets.style.cssText = 'width:30px; height:30px; padding:0;';
        assignSets.innerHTML = '<i class="fa-solid fa-layer-group"></i>'; 

        // Delete button
        const del = document.createElement('button');
        del.className = 'btn btn-sm btn-outline-danger rounded-circle';
        del.dataset.action = 'deleteCard';
        del.style.cssText = 'width:30px; height:30px; padding:0;';
        del.innerHTML = '<i class="fa-solid fa-trash-can"></i>';

        btnColumn.append(edit, assignSets, del);

        wrapper.appendChild(btnColumn)

        wrapper.appendChild(body);
        col.appendChild(wrapper);
        window.cardsGrid.appendChild(col);
      });
    }

    /* =========================================================
    E) ADD / EDIT CARD MODAL LIFECYCLE (PRODUCTION)
    ========================================================= */

    // When you open the card modal from any "+ Add Card" button, treat it as "new card"
    const cardModalTrigger = document.querySelectorAll('[data-bs-target="#setEditModal"]');
    
    cardModalTrigger.forEach(btn => {
      btn.addEventListener('click', () => { editIndex = null; });
    });

    const cardModalEl = document.getElementById('cardModal');

    if (cardModalEl) {
      cardModalEl.addEventListener('show.bs.modal', () => {
        if (editIndex === null) {
          // New card → clear form
          const form = document.getElementById('cardForm');
          form.reset();
          window.notesEl.value = '';
          Array.from(window.setsEl.options).forEach(o => { o.selected = false; });
          window.setsEl.selectedIndex = -1;
        }
      });

      cardModalEl.addEventListener('hidden.bs.modal', () => {
        // Always clear set selection when modal closes
        Array.from(window.setsEl.options).forEach(o => { o.selected = false; });
        window.setsEl.selectedIndex = -1;
      });
    }

    const cardForm = document.getElementById('cardForm');

    // PRODUCTION: create or update a card
    if (cardForm) {
      cardForm.addEventListener('submit', (e) => {
        e.preventDefault();

        const es    = document.getElementById('esText').value.trim();
        const en    = document.getElementById('enText').value.trim();
        const notes = window.notesEl.value.trim();
        const sets  = getSelectedSets();

        if (!es || !en) return;

        if (editIndex !== null) {
          // Update existing card
          cards[editIndex] = { ...cards[editIndex], es, en, notes, sets };
          editIndex = null;
        } else {
          // New card at top
          cards.unshift({ es, en, notes, sets });
        }

        localStorage.setItem('cards', JSON.stringify(cards));
        renderCards();

        const m = document.getElementById('cardModal');
        (bootstrap.Modal.getInstance(m) || new bootstrap.Modal(m)).hide();

        new bootstrap.Toast(document.getElementById('appToast')).show();

        e.target.reset();
        setSelectedSets([]);
      });
    }

    // PRODUCTION: handle Edit/Delete clicks in All Cards grid
    if (window.cardsGrid) {
      window.cardsGrid.addEventListener('click', (e) => {
            if (e.target.dataset.action === 'deleteCard') {
              const idx = e.target.closest('[data-index]').dataset.index;
              cards.splice(idx, 1);
              localStorage.setItem('cards', JSON.stringify(cards));
              renderCards();
            }

            if (e.target.dataset.action === 'editCard') {
              const idx = Number(e.target.closest('[data-index]').dataset.index);
              editIndex = idx;

              // Load card into modal fields
              document.getElementById('esText').value = cards[idx].es || '';
              document.getElementById('enText').value = cards[idx].en || '';
              window.notesEl.value = cards[idx].notes || '';
              setSelectedSets(cards[idx].sets || []);

              const modal = new bootstrap.Modal(document.getElementById('cardModal'));
              modal.show();
            }
          });
    }
    

    /* =========================================================
    G) SEARCH FILTER (PRODUCTION)
    ========================================================= */

    const searchInput = document.getElementById('searchCards');
    if (searchInput) {
      searchInput.addEventListener('input', () => {
        const term = searchInput.value.toLowerCase();
        document.querySelectorAll('#cardsGrid .card').forEach(card => {
          const text = card.textContent.toLowerCase();
          card.parentElement.style.display = text.includes(term) ? '' : 'none';
        });
      });
    }