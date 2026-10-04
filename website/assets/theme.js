(() => {
  const system = window.matchMedia('(prefers-color-scheme: dark)');
  let preference = 'auto';
  try { preference = localStorage.getItem('rishe-workshop-theme') || 'auto'; } catch {}
  if (!['auto', 'light', 'dark'].includes(preference)) preference = 'auto';
  const apply = () => {
    document.documentElement.dataset.theme = preference === 'auto' ? (system.matches ? 'dark' : 'light') : preference;
    document.querySelectorAll('[data-theme]').forEach(button => {
      if (button.tagName === 'BUTTON') button.setAttribute('aria-pressed', String(button.dataset.theme === preference));
    });
  };
  apply();
  system.addEventListener('change', apply);
  document.addEventListener('DOMContentLoaded', () => {
    document.querySelector('.themes').hidden = false;
    document.querySelectorAll('button[data-theme]').forEach(button => button.addEventListener('click', () => {
      preference = button.dataset.theme;
      try { localStorage.setItem('rishe-workshop-theme', preference); } catch {}
      apply();
    }));
    apply();
  });
})();
