// ============================================
// Event Registration Platform — UI Script
// Handles: dropdown menus (Messages / Notifications /
// Profile), the right-side Customize panel, and the
// live theme toggles inside it.
// No jQuery / Bootstrap JS needed — plain JavaScript only.
// ============================================

document.addEventListener('DOMContentLoaded', function () {

  // ---------- 1. Dropdown menus ----------
  var toggles = document.querySelectorAll('[data-toggle="dropdown"]');

  toggles.forEach(function (toggle) {
    toggle.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();

      var menu = this.nextElementSibling;
      var alreadyOpen = menu.classList.contains('show');

      // close every other open dropdown first
      document.querySelectorAll('.dropdown-menu.show').forEach(function (m) {
        m.classList.remove('show');
      });

      if (!alreadyOpen) {
        menu.classList.add('show');
      }
    });
  });

  // clicking anywhere outside closes any open dropdown
  document.addEventListener('click', function () {
    document.querySelectorAll('.dropdown-menu.show').forEach(function (m) {
      m.classList.remove('show');
    });
  });


  // ---------- 2. Customize panel (slide in from the right) ----------
  var panelToggle = document.querySelector('[data-widget="control-sidebar"]');
  var panel = document.getElementById('customizePanel');
  var overlay = document.getElementById('customizeOverlay');

  function openPanel() {
    panel.classList.add('open');
    overlay.classList.add('show');
  }
  function closePanel() {
    panel.classList.remove('open');
    overlay.classList.remove('show');
  }

  if (panelToggle && panel) {
    panelToggle.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();
      if (panel.classList.contains('open')) {
        closePanel();
      } else {
        openPanel();
      }
    });
  }
  if (overlay) {
    overlay.addEventListener('click', closePanel);
  }


  // ---------- 3. Layout & text-size checkboxes ----------
  // Each checkbox id maps to a class added/removed on <body>.
  // CSS rules for these classes live in static/css/style.css
  var toggleMap = {
    navbarBorder: 'no-navbar-border',
    bodySmall: 'text-sm',
    navbarSmall: 'navbar-text-sm',
    sidebarCompact: 'sidebar-compact',
    brandSmall: 'brand-text-sm'
  };

  Object.keys(toggleMap).forEach(function (id) {
    var box = document.getElementById(id);
    if (!box) return;
    var className = toggleMap[id];

    // match the class to whatever the checkbox starts as
    document.body.classList.toggle(className, box.checked);

    box.addEventListener('change', function () {
      document.body.classList.toggle(className, box.checked);
    });
  });


  // ---------- 4. Color swatches (Navbar / Accent / Sidebar / Brand) ----------
  var root = document.documentElement;
  var sidebar = document.querySelector('.sidebar');

  document.querySelectorAll('.theme-swatch').forEach(function (swatch) {
    swatch.addEventListener('click', function () {
      var panelName = this.dataset.panel;
      var value = this.dataset.value;

      if (panelName === 'navbar') {
        if (value === 'gradient') {
          root.style.setProperty('--topbar-color-1', '#6a11cb');
          root.style.setProperty('--topbar-color-2', '#2575fc');
        } else {
          root.style.setProperty('--topbar-color-1', value);
          root.style.setProperty('--topbar-color-2', value);
        }
      }

      if (panelName === 'accent') {
        root.style.setProperty('--accent-color', value);
      }

      if (panelName === 'sidebar' && sidebar) {
        sidebar.classList.toggle('sidebar-light', value === 'light');
      }

      if (panelName === 'brand') {
        root.style.setProperty('--brand-color', value);
      }
    });
  });

});
