// Filter functionality
document.addEventListener('DOMContentLoaded', function() {
  const filterBtns = document.querySelectorAll('.filter-btn');
  const jobRows = document.querySelectorAll('.job-row');
  const detailRows = document.querySelectorAll('.detail-row');
  const crRows = document.querySelectorAll('.cr-row');
  const regressionRows = document.querySelectorAll('.regression-row');

  // Track active filters per group
  const activeFilters = {};

  filterBtns.forEach(btn => {
    btn.addEventListener('click', function() {
      const group = this.dataset.group;
      const value = this.dataset.value;

      if (value === 'all') {
        // Deactivate all filters in this group
        document.querySelectorAll(`.filter-btn[data-group="${group}"]`).forEach(b => {
          b.classList.remove('active');
        });
        this.classList.add('active');
        delete activeFilters[group];
      } else {
        // Deactivate "all" button
        document.querySelector(`.filter-btn[data-group="${group}"][data-value="all"]`)?.classList.remove('active');

        // Toggle this filter
        if (this.classList.contains('active')) {
          this.classList.remove('active');
          if (activeFilters[group]) {
            activeFilters[group].delete(value);
            if (activeFilters[group].size === 0) {
              delete activeFilters[group];
              document.querySelector(`.filter-btn[data-group="${group}"][data-value="all"]`)?.classList.add('active');
            }
          }
        } else {
          this.classList.add('active');
          if (!activeFilters[group]) activeFilters[group] = new Set();
          activeFilters[group].add(value);
        }
      }

      applyFilters();
    });
  });

  function applyFilters() {
    // When filters are active, expand all to show filtered results
    const hasFilters = Object.keys(activeFilters).length > 0;
    if (hasFilters) {
      sectionsCollapsed.jobs = false;
      sectionsCollapsed.details = false;
      applyCollapse();
      const jobsBtn = document.getElementById('expand-jobs-btn');
      const detailsBtn = document.getElementById('expand-details-btn');
      if (jobsBtn) jobsBtn.textContent = 'Show top ' + INITIAL_VISIBLE + ' only';
      if (detailsBtn) detailsBtn.textContent = 'Show top ' + INITIAL_VISIBLE + ' only';
    }

    function isVisible(row) {
      for (const [group, values] of Object.entries(activeFilters)) {
        const rowValue = row.dataset[group];
        if (rowValue && !values.has(rowValue)) {
          return false;
        }
      }
      return true;
    }

    jobRows.forEach(row => {
      row.style.display = isVisible(row) ? '' : 'none';
    });

    detailRows.forEach(row => {
      row.style.display = isVisible(row) ? '' : 'none';
    });

    regressionRows.forEach(row => {
      row.style.display = isVisible(row) ? '' : 'none';
    });

    crRows.forEach(row => {
      row.style.display = isVisible(row) ? '' : 'none';
    });

    // Update counts
    const visibleCount = document.querySelectorAll('.job-row:not([style*="display: none"])').length;
    const countEl = document.getElementById('visible-count');
    if (countEl) countEl.textContent = visibleCount;
  }

  // Collapse rows beyond top 5 for jobs table and failure details
  const INITIAL_VISIBLE = 5;
  const sectionsCollapsed = { jobs: true, details: true, regressions: true, cr: true };

  function applyCollapse() {
    document.querySelectorAll('.job-row').forEach(row => {
      const idx = parseInt(row.dataset.rowIndex);
      if (sectionsCollapsed.jobs && idx > INITIAL_VISIBLE) {
        row.classList.add('collapsed-row');
      } else {
        row.classList.remove('collapsed-row');
      }
    });
    document.querySelectorAll('.detail-row').forEach(row => {
      const idx = parseInt(row.dataset.rowIndex);
      if (sectionsCollapsed.details && idx > INITIAL_VISIBLE) {
        row.classList.add('collapsed-row');
      } else {
        row.classList.remove('collapsed-row');
      }
    });
    document.querySelectorAll('.regression-row').forEach(row => {
      const idx = parseInt(row.dataset.rowIndex);
      if (sectionsCollapsed.regressions && idx > INITIAL_VISIBLE) {
        row.classList.add('collapsed-row');
      } else {
        row.classList.remove('collapsed-row');
      }
    });
    document.querySelectorAll('.cr-row').forEach(row => {
      const idx = parseInt(row.dataset.rowIndex);
      if (sectionsCollapsed.cr && idx > INITIAL_VISIBLE) {
        row.classList.add('collapsed-row');
      } else {
        row.classList.remove('collapsed-row');
      }
    });
  }

  // Apply initial collapse
  applyCollapse();

  // Toggle section expand/collapse (called from onclick)
  const sectionSelectors = { jobs: '.job-row', details: '.detail-row', regressions: '.regression-row', cr: '.cr-row' };
  const sectionLabels = { jobs: ' failing jobs', details: ' failure details', regressions: ' regressions', cr: ' component regressions' };

  window.expandSection = function(section) {
    sectionsCollapsed[section] = !sectionsCollapsed[section];
    applyCollapse();
    const btn = document.getElementById('expand-' + section + '-btn');
    if (btn) {
      const total = document.querySelectorAll(sectionSelectors[section] || '.job-row').length;
      btn.textContent = sectionsCollapsed[section]
        ? 'Show all ' + total + (sectionLabels[section] || '')
        : 'Show top ' + INITIAL_VISIBLE + ' only';
    }
  };

  // "View Details" links: expand both sections, open the target detail, scroll to it
  document.querySelectorAll('.detail-link').forEach(link => {
    link.addEventListener('click', function(e) {
      e.preventDefault();
      // Expand both sections so the target is visible
      sectionsCollapsed.jobs = false;
      sectionsCollapsed.details = false;
      applyCollapse();
      const jobsBtn = document.getElementById('expand-jobs-btn');
      const detailsBtn = document.getElementById('expand-details-btn');
      if (jobsBtn) jobsBtn.textContent = 'Show top ' + INITIAL_VISIBLE + ' only';
      if (detailsBtn) detailsBtn.textContent = 'Show top ' + INITIAL_VISIBLE + ' only';

      const targetId = this.getAttribute('href').substring(1);
      const detail = document.getElementById(targetId);
      if (detail) {
        detail.open = true;
        detail.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  // Column sorting for any table with sortable headers
  const sortableHeaders = document.querySelectorAll('th.sortable');
  sortableHeaders.forEach(th => {
    th.addEventListener('click', function() {
      const table = this.closest('table');
      if (!table) return;
      const tbody = table.querySelector('tbody');
      if (!tbody) return;
      const col = parseInt(this.dataset.col);
      const rows = Array.from(tbody.querySelectorAll('tr'));

      // Toggle sort direction — only clear siblings in the same table
      const isAsc = this.classList.contains('asc');
      table.querySelectorAll('th.sortable').forEach(h => { h.classList.remove('asc', 'desc'); });
      this.classList.add(isAsc ? 'desc' : 'asc');
      const dir = isAsc ? -1 : 1;

      rows.sort((a, b) => {
        const aText = (a.children[col]?.textContent || '').trim().toLowerCase();
        const bText = (b.children[col]?.textContent || '').trim().toLowerCase();
        // Try numeric comparison for columns like pass rates and runs
        const aNum = parseFloat(aText);
        const bNum = parseFloat(bText);
        if (!isNaN(aNum) && !isNaN(bNum)) {
          return (aNum - bNum) * dir;
        }
        return aText < bText ? -dir : aText > bText ? dir : 0;
      });

      rows.forEach(row => tbody.appendChild(row));
    });
  });

  // Copy command to clipboard
  window.copyCommand = function(btn) {
    var code = btn.closest('.cmd-copy-row').querySelector('code');
    if (!code) return;
    navigator.clipboard.writeText(code.textContent.trim()).then(function() {
      btn.textContent = 'Copied!';
      btn.classList.add('copied');
      setTimeout(function() {
        btn.textContent = 'Copy';
        btn.classList.remove('copied');
      }, 2000);
    });
  };

  // Draggable column resizers
  document.querySelectorAll('table').forEach(table => {
    const headers = table.querySelectorAll('th');

    // Freeze column widths to current auto-computed sizes, then switch to fixed layout
    function freezeLayout() {
      if (table.dataset.frozen) return;
      headers.forEach(h => { h.style.width = h.offsetWidth + 'px'; });
      table.style.tableLayout = 'fixed';
      table.classList.add('layout-frozen');
      table.dataset.frozen = '1';
    }

    headers.forEach(th => {
      const resizer = document.createElement('div');
      resizer.className = 'col-resizer';
      th.appendChild(resizer);

      let startX, startWidth;

      resizer.addEventListener('mousedown', function(e) {
        e.preventDefault();
        e.stopPropagation();
        freezeLayout();
        startX = e.pageX;
        startWidth = th.offsetWidth;
        resizer.classList.add('resizing');

        function onMouseMove(e) {
          th.style.width = (startWidth + e.pageX - startX) + 'px';
        }
        function onMouseUp() {
          resizer.classList.remove('resizing');
          document.removeEventListener('mousemove', onMouseMove);
          document.removeEventListener('mouseup', onMouseUp);
        }

        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mouseup', onMouseUp);
      });
    });
  });
});
