/* ═══════════════════════════════════════════════════════════════
   Groupe La Certitude — main.js
═══════════════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {

  // ── AOS Init ──────────────────────────────────────────────
  AOS.init({
    duration: 700,
    easing: 'ease-out-cubic',
    once: true,
    offset: 60,
  });

  // ── Navbar scroll effect ──────────────────────────────────
  const nav = document.getElementById('mainNav');
  if (nav) {
    const onScroll = () => {
      nav.classList.toggle('scrolled', window.scrollY > 40);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  // ── Mobile menu ───────────────────────────────────────────
  const hamburger   = document.getElementById('hamburger');
  const mobileMenu  = document.getElementById('mobileMenu');
  const menuClose   = document.getElementById('menuClose');

  const openMenu  = () => { mobileMenu?.classList.add('open'); document.body.style.overflow = 'hidden'; };
  const closeMenu = () => { mobileMenu?.classList.remove('open'); document.body.style.overflow = ''; };

  hamburger?.addEventListener('click', openMenu);
  menuClose?.addEventListener('click', closeMenu);
  mobileMenu?.addEventListener('click', e => { if (e.target === mobileMenu) closeMenu(); });

  // close on link click
  mobileMenu?.querySelectorAll('a').forEach(a => a.addEventListener('click', closeMenu));

  // ── Countdown to deadline (22 June 2026) ─────────────────
  const countdownEls = {
    jours:   document.getElementById('cd-jours'),
    heures:  document.getElementById('cd-heures'),
    minutes: document.getElementById('cd-minutes'),
    secondes:document.getElementById('cd-secondes'),
  };

  if (Object.values(countdownEls).some(Boolean)) {
    const deadline = new Date('2026-06-22T23:59:59');

    const updateCountdown = () => {
      const diff = deadline - Date.now();
      if (diff <= 0) {
        Object.values(countdownEls).forEach(el => { if (el) el.textContent = '00'; });
        return;
      }
      const d = Math.floor(diff / 86400000);
      const h = Math.floor((diff % 86400000) / 3600000);
      const m = Math.floor((diff % 3600000) / 60000);
      const s = Math.floor((diff % 60000) / 1000);

      const pad = n => String(n).padStart(2, '0');
      if (countdownEls.jours)    countdownEls.jours.textContent    = pad(d);
      if (countdownEls.heures)   countdownEls.heures.textContent   = pad(h);
      if (countdownEls.minutes)  countdownEls.minutes.textContent  = pad(m);
      if (countdownEls.secondes) countdownEls.secondes.textContent = pad(s);
    };

    updateCountdown();
    setInterval(updateCountdown, 1000);
  }

  // ── Animated number counters ──────────────────────────────
  const animateCounter = (el) => {
    const target = parseInt(el.dataset.target, 10);
    const duration = 2000;
    const step = target / (duration / 16);
    let current = 0;
    const suffix = el.dataset.suffix || '';

    const timer = setInterval(() => {
      current = Math.min(current + step, target);
      el.textContent = Math.floor(current) + suffix;
      if (current >= target) clearInterval(timer);
    }, 16);
  };

  // Trigger counters when visible
  const counterEls = document.querySelectorAll('[data-counter]');
  if (counterEls.length) {
    const obs = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          animateCounter(entry.target);
          obs.unobserve(entry.target);
        }
      });
    }, { threshold: 0.5 });
    counterEls.forEach(el => obs.observe(el));
  }

  // ── Gallery filter ────────────────────────────────────────
  const filterBtns  = document.querySelectorAll('.lc-filter-btn');
  const galleryItems = document.querySelectorAll('.lc-gallery-item');

  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const cat = btn.dataset.filter;
      galleryItems.forEach(item => {
        const show = cat === 'all' || item.dataset.category === cat;
        item.style.display = show ? '' : 'none';
        if (show) item.style.animation = 'fadeIn 0.4s ease';
      });
    });
  });

  // ── Lightbox ──────────────────────────────────────────────
  const lightbox     = document.getElementById('lightbox');
  const lightboxImg  = document.getElementById('lightboxImg');

  document.querySelectorAll('.lc-gallery-item[data-src]').forEach(item => {
    item.addEventListener('click', () => {
      if (lightbox && lightboxImg) {
        lightboxImg.src = item.dataset.src;
        lightboxImg.alt = item.dataset.caption || '';
        lightbox.classList.add('open');
        document.body.style.overflow = 'hidden';
      }
    });
  });

  document.getElementById('lightboxClose')?.addEventListener('click', () => {
    lightbox?.classList.remove('open');
    document.body.style.overflow = '';
  });

  lightbox?.addEventListener('click', e => {
    if (e.target === lightbox) {
      lightbox.classList.remove('open');
      document.body.style.overflow = '';
    }
  });

  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && lightbox?.classList.contains('open')) {
      lightbox.classList.remove('open');
      document.body.style.overflow = '';
    }
  });

  // ── Active nav link ───────────────────────────────────────
  const currentPath = window.location.pathname;
  document.querySelectorAll('.lc-nav__link').forEach(link => {
    if (link.getAttribute('href') === currentPath) {
      link.classList.add('active');
    }
  });

  // ── Smooth anchor scroll ──────────────────────────────────
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', e => {
      const target = document.querySelector(a.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  // ── Form auto-format phone ────────────────────────────────
  document.querySelectorAll('input[type="tel"]').forEach(input => {
    input.addEventListener('input', () => {
      input.value = input.value.replace(/[^\d\s\+\-]/g, '');
    });
  });

});

// FadeIn animation
const style = document.createElement('style');
style.textContent = `
  @keyframes fadeIn {
    from { opacity: 0; transform: scale(0.96); }
    to   { opacity: 1; transform: scale(1); }
  }
`;
document.head.appendChild(style);
