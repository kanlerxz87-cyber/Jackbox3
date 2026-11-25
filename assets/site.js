/* Jackbox3 public site enhancements.
   No network requests. No cookies, localStorage or sessionStorage.
   Nothing here transmits or persists adviser input. */
(function () {
  'use strict';
  document.documentElement.classList.add('js');

  // Suggestion review path: purely in-memory, implements nothing.
  document.querySelectorAll('.suggestion-choice').forEach(function (sel) {
    sel.addEventListener('change', function () {
      var row = sel.closest('tr');
      if (!row) return;
      var cell = row.querySelector('td:last-child');
      if (!cell) return;
      var note = cell.querySelector('.review-note');
      if (!note) {
        note = document.createElement('span');
        note.className = 'review-note';
        cell.appendChild(note);
      }
      var label = sel.options[sel.selectedIndex].text;
      note.textContent = ' ' + sel.dataset.sid + ': ' + label +
        ' (client-side only; no change implemented; log it in COORDINATION.md first).';
    });
  });

  // Make external source links open safely (defence in depth).
  document.querySelectorAll('a[href^="https://"]').forEach(function (a) {
    if (!a.getAttribute('rel')) a.setAttribute('rel', 'noopener noreferrer');
    if (!a.getAttribute('target')) a.setAttribute('target', '_blank');
  });
}());
