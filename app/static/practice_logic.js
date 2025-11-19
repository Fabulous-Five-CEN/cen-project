window.practiceSetSelect = document.getElementById('practiceSet');

    /* =========================================================
    F) PRACTICE LOGIC (PRODUCTION, uses real cards/sets)
    ========================================================= */

    const practiceCardEl   = document.getElementById('practiceCard');
    const progressPill     = document.getElementById('progressPill');
    const statusPill       = document.getElementById('statusPill');
    const answerReveal     = document.getElementById('answerReveal');
    const answerRevealText = document.getElementById('answerRevealText');
    const flipBtn          = document.getElementById('flipBtn');
    const resetBtn         = document.getElementById('resetBtn');
    const shuffleBtn       = document.getElementById('shuffleBtn');
    const nextBtn          = document.getElementById('nextBtn');
    const prevBtn          = document.getElementById('prevBtn');
    const showAnswerBtn    = document.getElementById('showAnswerBtn');
    const gotItBtn         = document.getElementById('gotItBtn');
    const learningBtn      = document.getElementById('learningBtn');

    let practiceDeck   = [];   // PRODUCTION: subset of cards[] plus _idx
    let currentIndex   = 0;
    let flipped        = false;
    const statusByCard = {};   // PRODUCTION: per-card "gotit"/"learning" labels

    // PRODUCTION: build deck from cards[] based on chosen set
    function buildPracticeDeck() {
      const choice = window.practiceSetSelect.value;

      // Add original index so we can key statusByCard
      let all = cards.map((card, idx) => ({ ...card, _idx: idx }));

      if (choice !== 'all') {
        all = all.filter(c => Array.isArray(c.sets) && c.sets.includes(choice));
      }

      practiceDeck = all;
      currentIndex = 0;
      flipped      = false;
      resetAnswerReveal();
    }

    // PRODUCTION: fill the big practice card with current entry
    function renderPracticeCard() {
      if (!practiceDeck.length) {
        // Edge case: no cards in this set
        document.getElementById('frontLabel').textContent = 'Spanish';
        document.getElementById('backLabel').textContent  = 'English';
        document.getElementById('frontText').textContent  = 'No cards in this set yet';
        document.getElementById('backText').textContent   = '';
        practiceCardEl.classList.remove('flipped');
        progressPill.textContent = '0 / 0';
        statusPill.classList.add('d-none');
        statusPill.textContent = '';
        return;
      }

      const sideES = document.querySelector('input[name="startSide"]:checked').value === 'es';
      const entry  = practiceDeck[currentIndex];
      const card   = entry;

      const frontLabel = sideES ? 'Spanish' : 'English';
      const backLabel  = sideES ? 'English' : 'Spanish';
      const frontText  = sideES ? card.es : card.en;
      const backText   = sideES ? card.en : card.es;

      document.getElementById('frontLabel').textContent = frontLabel;
      document.getElementById('backLabel').textContent  = backLabel;
      document.getElementById('frontText').textContent  = frontText;
      document.getElementById('backText').textContent   = backText;

      practiceCardEl.classList.toggle('flipped', flipped);

      progressPill.textContent = `Card ${currentIndex + 1} / ${practiceDeck.length}`;

      // Show "Got it" / "Still learning" pill
      const st = statusByCard[entry._idx];
      if (!st) {
        statusPill.classList.add('d-none');
        statusPill.textContent = '';
      } else {
        statusPill.classList.remove('d-none');
        if (st === 'gotit') {
          statusPill.textContent = 'Got it';
          statusPill.className = 'badge rounded-pill text-bg-success';
        } else {
          statusPill.textContent = 'Still learning';
          statusPill.className = 'badge rounded-pill text-bg-warning';
        }
      }
    }

    function resetAnswerReveal() {
      answerReveal.classList.remove('open');
      answerRevealText.textContent = '';
      showAnswerBtn.textContent = 'Show Answer';
    }

    // PRODUCTION: flip via button
    if (flipBtn) {
      flipBtn.onclick = () => {
        flipped = !flipped;
        renderPracticeCard();
      };
    }

    // PRODUCTION: flip by clicking card
    if (practiceCardEl) {
      practiceCardEl.onclick = () => {
        flipped = !flipped;
        renderPracticeCard();
      };
    }

    // PRODUCTION: reveal the "start side" text as smaller answer
    if (showAnswerBtn) {
      showAnswerBtn.addEventListener('click', () => {
        if (!practiceDeck.length) return;

        const sideES = document.querySelector('input[name="startSide"]:checked').value === 'es';
        const entry  = practiceDeck[currentIndex];
        const card   = entry;

        // Show the answer text (which is the opposite side from what's shown)
        answerRevealText.textContent = sideES ? card.en : card.es;

        answerReveal.classList.toggle('open');
        showAnswerBtn.textContent = answerReveal.classList.contains('open')
          ? 'Hide Answer'
          : 'Show Answer';
      });
    }

    // PRODUCTION: mark card as got it / still learning (in-memory only)
    function setStatus(status) {
      if (!practiceDeck.length) return;
      const entry = practiceDeck[currentIndex];
      statusByCard[entry._idx] = status;
      renderPracticeCard();
    }

    if (gotItBtn)
      gotItBtn.addEventListener('click',    () => setStatus('gotit'));
    if (learningBtn)
      learningBtn.addEventListener('click', () => setStatus('learning'));

    // PRODUCTION: next / previous navigation
    if (nextBtn) {
      nextBtn.onclick = () => {
        if (!practiceDeck.length) return;
        flipped = false;
        currentIndex = (currentIndex + 1) % practiceDeck.length;
        resetAnswerReveal();
        renderPracticeCard();
      };
    }

    if (prevBtn) {
      prevBtn.onclick = () => {
        if (!practiceDeck.length) return;
        flipped = false;
        currentIndex = (currentIndex - 1 + practiceDeck.length) % practiceDeck.length;
        resetAnswerReveal();
        renderPracticeCard();
      };
    }

    // PRODUCTION: reset clears progress + statuses
    if (resetBtn) {
      resetBtn.onclick = () => {
        if (!practiceDeck.length) return;
        currentIndex = 0;
        flipped      = false;
        Object.keys(statusByCard).forEach(k => delete statusByCard[k]); // clear Got it / Still learning
        resetAnswerReveal();
        renderPracticeCard();
      };
    }

    // PRODUCTION: shuffle deck in-place
    if (shuffleBtn) {
      shuffleBtn.onclick = () => {
        if (!practiceDeck.length) return;
        for (let i = practiceDeck.length - 1; i > 0; i--) {
          const j = Math.floor(Math.random() * (i + 1));
          [practiceDeck[i], practiceDeck[j]] = [practiceDeck[j], practiceDeck[i]];
        }
        currentIndex = 0;
        flipped = false;
        resetAnswerReveal();
        renderPracticeCard();
      };
    }

    // PRODUCTION: switching start side re-renders card
    const switchRenderTrigger = document.querySelectorAll('input[name="startSide"]');

    switchRenderTrigger.forEach(r => {
      r.addEventListener('change', () => {
        flipped = false;
        resetAnswerReveal();
        renderPracticeCard();
      });
    });

    // PRODUCTION: when Practice modal is triggered, build deck from real cards
    const practiceModalTrigger = document.querySelector('[data-bs-target="#practiceModal"]');

    if (practiceModalTrigger) {
      practiceModalTrigger.addEventListener('click', () => {
        buildPracticeDeck();
        renderPracticeCard();
      });
    }

    /* =========================================================
     I) SWIPE HANDLING (PRODUCTION, but optional UX)
     ========================================================= */

    let startX = 0;
    let currentX = 0;
    let isDragging = false;
    const swipeThreshold = 60;

    function handleStart(e) {
      isDragging = true;
      startX = e.touches ? e.touches[0].clientX : e.clientX;
      currentX = startX;
    }

    function handleMove(e) {
      if (!isDragging) return;
      currentX = e.touches ? e.touches[0].clientX : e.clientX;
      const delta = currentX - startX;
      practiceCardEl.style.transform = `translateX(${delta}px)`;
    }
    
    function handleEnd() {
      if (!isDragging) return;
      isDragging = false;
      const delta = currentX - startX;

      if (delta < -swipeThreshold) {
        // swipe left → next
        practiceCardEl.style.transition = "transform .25s ease";
        practiceCardEl.style.transform = "translateX(-400px)";
        setTimeout(() => {
          document.getElementById("nextBtn").click();
          practiceCardEl.style.transition = "none";
          practiceCardEl.style.transform = "translateX(400px)";
          setTimeout(() => {
            practiceCardEl.style.transition = "transform .25s ease";
            practiceCardEl.style.transform = "translateX(0)";
          }, 20);
        }, 200);
        return;
      }

      if (delta > swipeThreshold) {
        // swipe right → previous
        practiceCardEl.style.transition = "transform .25s ease";
        practiceCardEl.style.transform = "translateX(400px)";
        setTimeout(() => {
          document.getElementById("prevBtn").click();
          practiceCardEl.style.transition = "none";
          practiceCardEl.style.transform = "translateX(-400px)";
          setTimeout(() => {
            practiceCardEl.style.transition = "transform .25s ease";
            practiceCardEl.style.transform = "translateX(0)";
          }, 20);
        }, 200);
        return;
      }

      // not far enough → snap back
      practiceCardEl.style.transition = "transform .2s ease";
      practiceCardEl.style.transform = "translateX(0)";
    }

    if (practiceCardEl) {
      practiceCardEl.addEventListener("mousedown", handleStart);
      practiceCardEl.addEventListener("mousemove", handleMove);
      practiceCardEl.addEventListener("mouseup", handleEnd);
      practiceCardEl.addEventListener("mouseleave", handleEnd);

      practiceCardEl.addEventListener("touchstart", handleStart);
      practiceCardEl.addEventListener("touchmove", handleMove);
      practiceCardEl.addEventListener("touchend", handleEnd);
    }

    // CLEAR FILTER: when user clicks "Clear filter", show all cards again
    const clearFilterBtn = document.getElementById('clearSetFilter');

    if (clearFilterBtn) {
      clearFilterBtn?.addEventListener('click', () => {
        activeSetFilter = null;   // remove filter
        renderCards();            // re-render all cards

        // Switch back to All Cards tab (optional but nice)
        const allCardsLink = document.getElementById('cards-page');
        if (allCardsLink) {
          allCardsLink.click();
        }
      });
    }