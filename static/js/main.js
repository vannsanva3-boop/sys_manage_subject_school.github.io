document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.querySelector('.sidebar-toggle');
  const sidebar = document.querySelector('.app-sidebar');
  const scrim = document.querySelector('.sidebar-scrim');
  const mobileQuery = window.matchMedia('(max-width: 767px)');

  const closeMobileNav = () => {
    document.body.classList.remove('mobile-nav-open');
    document.body.style.removeProperty('overflow');
    toggle?.setAttribute('aria-expanded', 'false');
  };
  toggle?.addEventListener('click', () => {
    if (mobileQuery.matches) {
      const open = document.body.classList.toggle('mobile-nav-open');
      toggle.setAttribute('aria-expanded', String(open));
      document.body.style.overflow = open ? 'hidden' : '';
    } else {
      const collapsed = document.body.classList.toggle('sidebar-collapsed');
      toggle.setAttribute('aria-expanded', String(!collapsed));
      try { localStorage.setItem('attendance-sidebar-collapsed', String(collapsed)); } catch (_) { /* Storage can be disabled. */ }
    }
  });
  try {
    if (!mobileQuery.matches && localStorage.getItem('attendance-sidebar-collapsed') === 'true') {
      document.body.classList.add('sidebar-collapsed');
      toggle?.setAttribute('aria-expanded', 'false');
    }
  } catch (_) { /* Storage can be disabled. */ }
  scrim?.addEventListener('click', closeMobileNav);
  sidebar?.querySelectorAll('a').forEach(link => link.addEventListener('click', closeMobileNav));
  document.addEventListener('keydown', event => { if (event.key === 'Escape') closeMobileNav(); });
  mobileQuery.addEventListener?.('change', event => { if (!event.matches) closeMobileNav(); });

  document.querySelectorAll('form[data-confirm]').forEach(form => {
    form.addEventListener('submit', event => {
      if (!window.confirm(form.dataset.confirm)) event.preventDefault();
    });
  });

  document.querySelector('#student-modal')?.addEventListener('show.bs.modal', event => {
    const trigger = event.relatedTarget;
    const form = document.querySelector('#student-form');
    if (!form) return;
    const edit = trigger?.dataset.mode === 'edit';
    const code = document.querySelector('#modal-student-code');
    const name = document.querySelector('#modal-student-name');
    const gender = document.querySelector('#modal-student-gender');
    const classId = document.querySelector('#modal-student-class');
    const title = document.querySelector('#student-modal-title');
    const submit = document.querySelector('#student-submit');
    if (edit) {
      form.action = trigger.dataset.action;
      code.value = trigger.dataset.code || '';
      name.value = trigger.dataset.name || '';
      gender.value = trigger.dataset.gender || '';
      classId.value = trigger.dataset.class || '';
      title.textContent = 'Edit student';
      submit.innerHTML = '<i class="bi bi-check2"></i> Save changes';
    } else {
      form.reset();
      form.action = form.dataset.createAction;
      title.textContent = 'Add student';
      submit.innerHTML = '<i class="bi bi-check2"></i> Add Student';
    }
  });

  document.querySelector('#class-modal')?.addEventListener('show.bs.modal', event => {
    const trigger = event.relatedTarget;
    const form = document.querySelector('#class-form');
    const name = document.querySelector('#modal-class-name');
    const title = document.querySelector('#class-modal-title');
    const submit = document.querySelector('#class-submit');
    if (!form || !name) return;
    if (trigger?.dataset.mode === 'edit') {
      form.action = trigger.dataset.action;
      name.value = trigger.dataset.name || '';
      title.textContent = 'Edit class';
      submit.innerHTML = '<i class="bi bi-check2"></i> Save changes';
    } else {
      form.reset();
      form.action = form.dataset.createAction;
      title.textContent = 'Add class';
      submit.innerHTML = '<i class="bi bi-check2"></i> Add Class';
    }
  });

  const rosterSearch = document.querySelector('#roster-search');
  const rosterRows = [...document.querySelectorAll('.roster-row')];
  rosterSearch?.addEventListener('input', () => {
    const term = rosterSearch.value.trim().toLocaleLowerCase();
    let visible = 0;
    rosterRows.forEach(row => {
      const match = row.dataset.search.includes(term);
      row.hidden = !match;
      if (match) visible += 1;
    });
    const empty = document.querySelector('#no-search-results');
    if (empty) empty.hidden = visible !== 0;
  });

  const attendanceForm = document.querySelector('#attendance-form');
  if (!attendanceForm) return;
  const roster = JSON.parse(attendanceForm.dataset.roster || '[]');
  const radioInputs = [...attendanceForm.querySelectorAll('input[type="radio"]')];
  const updateSummary = () => {
    const values = roster.map(id => attendanceForm.querySelector(`input[name="status-${id}"]:checked`)?.value);
    ['Present', 'Permission', 'Absent'].forEach(status => {
      const node = document.querySelector(`#count-${status.toLowerCase()}`);
      if (node) node.textContent = String(values.filter(value => value === status).length);
    });
  };
  radioInputs.forEach(input => input.addEventListener('change', updateSummary));
  updateSummary();
  attendanceForm.addEventListener('submit', event => {
    const records = {};
    const error = document.querySelector('#attendance-error');
    for (const id of roster) {
      const selected = attendanceForm.querySelector(`input[name="status-${id}"]:checked`);
      if (!selected) {
        event.preventDefault();
        if (error) error.hidden = false;
        attendanceForm.querySelector(`input[name="status-${id}"]`)?.focus();
        return;
      }
      records[id] = selected.value;
    }
    if (error) error.hidden = true;
    document.querySelector('#records-input').value = JSON.stringify(records);
    const button = attendanceForm.querySelector('.save-button');
    if (button) {
      button.disabled = true;
      button.innerHTML = '<span class="spinner-border spinner-border-sm" aria-hidden="true"></span> Saving...';
    }
  });
});
