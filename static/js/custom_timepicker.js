document.addEventListener('DOMContentLoaded', function () {
    initCustomTimePickers();
});

function initCustomTimePickers() {
    const containers = document.querySelectorAll('.custom-timepicker-container');

    containers.forEach(container => {
        if (container.dataset.initialized) return;

        const input = container.querySelector('input.custom-timepicker-input');
        if (!input) return;

        // Create Dropdown
        const dropdown = document.createElement('div');
        dropdown.className = 'custom-timepicker-dropdown';

        // Header (Display Selected Time)
        const header = document.createElement('div');
        header.className = 'custom-timepicker-header';
        header.textContent = input.value || '--:--';
        dropdown.appendChild(header);

        // Body (Columns)
        const body = document.createElement('div');
        body.className = 'custom-timepicker-body';

        // Hours Column
        const hoursCol = document.createElement('div');
        hoursCol.className = 'custom-timepicker-column';
        for (let i = 0; i < 24; i++) {
            const val = String(i).padStart(2, '0');
            const item = document.createElement('div');
            item.className = 'custom-timepicker-item time-hour';
            item.textContent = val;
            item.dataset.value = val;
            item.onclick = (e) => selectTimeItem(e, container, 'hour');
            hoursCol.appendChild(item);
        }
        body.appendChild(hoursCol);

        // Minutes Column
        const minsCol = document.createElement('div');
        minsCol.className = 'custom-timepicker-column';
        for (let i = 0; i < 60; i++) {
            const val = String(i).padStart(2, '0');
            const item = document.createElement('div');
            item.className = 'custom-timepicker-item time-minute';
            item.textContent = val;
            item.dataset.value = val;
            item.onclick = (e) => selectTimeItem(e, container, 'minute');
            minsCol.appendChild(item);
        }
        body.appendChild(minsCol);

        dropdown.appendChild(body);
        container.appendChild(dropdown);

        // Events
        input.addEventListener('click', (e) => {
            e.stopPropagation();
            closeAllTimePickers();
            dropdown.classList.add('show');
            scrollToSelected(container);
        });

        // Initial Value Sync
        if (input.value) {
            updateSelectionVisuals(container, input.value);
        }

        container.dataset.initialized = 'true';
    });

    document.addEventListener('click', (e) => {
        if (!e.target.closest('.custom-timepicker-container')) {
            closeAllTimePickers();
        }
    });
}

function selectTimeItem(e, container, type) {
    e.stopPropagation();
    const input = container.querySelector('input.custom-timepicker-input');
    const header = container.querySelector('.custom-timepicker-header');

    // Toggle Visual Selection
    const column = e.target.closest('.custom-timepicker-column');
    column.querySelectorAll('.custom-timepicker-item').forEach(el => el.classList.remove('selected'));
    e.target.classList.add('selected');

    // Calculate New Value
    let currentVal = input.value || '00:00';
    let [h, m] = currentVal.includes(':') ? currentVal.split(':') : ['00', '00'];

    if (type === 'hour') {
        h = e.target.dataset.value;
    } else {
        m = e.target.dataset.value;
    }

    const newVal = `${h}:${m}`;
    input.value = newVal;
    header.textContent = newVal;

    // Trigger change event manually
    const event = new Event('change', { bubbles: true });
    input.dispatchEvent(event);
}

function updateSelectionVisuals(container, value) {
    if (!value || !value.includes(':')) return;
    const [h, m] = value.split(':');

    const hItem = container.querySelector(`.time-hour[data-value="${h}"]`);
    const mItem = container.querySelector(`.time-minute[data-value="${m}"]`);

    container.querySelectorAll('.custom-timepicker-item').forEach(e => e.classList.remove('selected'));

    if (hItem) hItem.classList.add('selected');
    if (mItem) mItem.classList.add('selected');

    const header = container.querySelector('.custom-timepicker-header');
    if (header) header.textContent = value;
}

function scrollToSelected(container) {
    const selected = container.querySelectorAll('.custom-timepicker-item.selected');
    selected.forEach(el => {
        el.scrollIntoView({ block: "center", behavior: "auto" });
    });
}

function closeAllTimePickers() {
    document.querySelectorAll('.custom-timepicker-dropdown').forEach(el => el.classList.remove('show'));
}
