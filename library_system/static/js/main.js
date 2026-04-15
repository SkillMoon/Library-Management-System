document.addEventListener('DOMContentLoaded', function() {
  const btnToggle = document.getElementById('menu-toggle');
  const sidebar   = document.getElementById('sidebar');

  if (btnToggle && sidebar) {
    btnToggle.addEventListener('click', function() {
      sidebar.classList.toggle('collapsed');
    });
  }
});
