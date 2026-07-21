document.addEventListener("DOMContentLoaded", () => {
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const yearNode = document.querySelector("[data-current-year]");
  if (yearNode) {
    yearNode.textContent = String(new Date().getFullYear());
  }

  /* Sticky header — shrink once the page scrolls */
  const header = document.querySelector(".site-header");
  if (header) {
    const onScroll = () => {
      header.classList.toggle("is-scrolled", window.scrollY > 24);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  /* Mobile nav drawer */
  const navToggle = document.querySelector("[data-nav-toggle]");
  const nav = document.querySelector(".nav");
  if (navToggle && nav) {
    const setOpen = (open) => {
      nav.classList.toggle("is-open", open);
      navToggle.setAttribute("aria-expanded", String(open));
      navToggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
      document.body.style.overflow = open ? "hidden" : "";
    };
    navToggle.addEventListener("click", () => setOpen(!nav.classList.contains("is-open")));
    nav.addEventListener("click", (e) => {
      if (e.target.closest("a")) setOpen(false);
    });
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && nav.classList.contains("is-open")) {
        setOpen(false);
        navToggle.focus();
      }
    });
  }

  /* Scroll fade-up reveal */
  const revealNodes = document.querySelectorAll(".reveal");
  if (revealNodes.length && !reducedMotion && "IntersectionObserver" in window) {
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            io.unobserve(entry.target);
          }
        });
      },
      { rootMargin: "0px 0px -8% 0px", threshold: 0.1 }
    );
    revealNodes.forEach((node) => io.observe(node));
  } else {
    revealNodes.forEach((node) => node.classList.add("is-visible"));
  }

  /* Contact form — success message + inline validation */
  const thanksEl = document.querySelector("[data-contact-thanks]");
  if (thanksEl && new URLSearchParams(window.location.search).get("sent") === "1") {
    thanksEl.hidden = false;
    const form = document.querySelector(".contact-form");
    if (form) form.hidden = true;
  }

  document.querySelectorAll("form[data-validate]").forEach((form) => {
    const fields = Array.from(form.querySelectorAll(".field"));

    const validateField = (field) => {
      const control = field.querySelector("input, select, textarea");
      if (!control || !control.willValidate) return true;
      const valid = control.checkValidity();
      field.classList.toggle("is-invalid", !valid);
      control.setAttribute("aria-invalid", String(!valid));
      return valid;
    };

    fields.forEach((field) => {
      const control = field.querySelector("input, select, textarea");
      if (!control) return;
      control.addEventListener("blur", () => validateField(field));
      control.addEventListener("input", () => {
        if (field.classList.contains("is-invalid")) validateField(field);
      });
    });

    form.addEventListener("submit", (e) => {
      const allValid = fields.map(validateField).every(Boolean);
      if (!allValid) {
        e.preventDefault();
        const firstInvalid = form.querySelector(".field.is-invalid input, .field.is-invalid select, .field.is-invalid textarea");
        if (firstInvalid) firstInvalid.focus();
      }
    });
  });

  /* Lightbox — gallery and project detail imagery */
  const lightboxTargets = Array.from(document.querySelectorAll("[data-lightbox]"));
  if (lightboxTargets.length) {
    const lightbox = document.createElement("div");
    lightbox.className = "lightbox";
    lightbox.setAttribute("role", "dialog");
    lightbox.setAttribute("aria-modal", "true");
    lightbox.setAttribute("aria-label", "Image viewer");
    lightbox.innerHTML = [
      '<button class="lightbox__close" type="button" aria-label="Close viewer">&times;</button>',
      '<button class="lightbox__nav lightbox__nav--prev" type="button" aria-label="Previous image">&lsaquo;</button>',
      '<img class="lightbox__img" alt="">',
      '<button class="lightbox__nav lightbox__nav--next" type="button" aria-label="Next image">&rsaquo;</button>',
      '<div class="lightbox__caption"></div>'
    ].join("");
    document.body.appendChild(lightbox);

    const imgEl = lightbox.querySelector(".lightbox__img");
    const captionEl = lightbox.querySelector(".lightbox__caption");
    const closeBtn = lightbox.querySelector(".lightbox__close");
    let current = -1;
    let lastFocus = null;

    const sourceFor = (target) => {
      const img = target.querySelector("img");
      if (img) return { src: img.currentSrc || img.src, alt: img.alt || "" };
      const bg = getComputedStyle(target).backgroundImage.match(/url\(["']?(.+?)["']?\)/);
      return { src: bg ? bg[1] : "", alt: target.getAttribute("aria-label") || "" };
    };

    const show = (index) => {
      current = (index + lightboxTargets.length) % lightboxTargets.length;
      const { src, alt } = sourceFor(lightboxTargets[current]);
      imgEl.src = src;
      imgEl.alt = alt;
      captionEl.textContent = alt;
    };

    const open = (index) => {
      lastFocus = document.activeElement;
      show(index);
      lightbox.classList.add("is-open");
      document.body.style.overflow = "hidden";
      closeBtn.focus();
    };

    const close = () => {
      lightbox.classList.remove("is-open");
      document.body.style.overflow = "";
      if (lastFocus) lastFocus.focus();
    };

    lightboxTargets.forEach((target, index) => {
      target.addEventListener("click", () => open(index));
      if (target.tagName !== "BUTTON" && target.tagName !== "A") {
        target.setAttribute("tabindex", "0");
        target.setAttribute("role", "button");
        target.addEventListener("keydown", (e) => {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            open(index);
          }
        });
      }
    });

    closeBtn.addEventListener("click", close);
    lightbox.querySelector(".lightbox__nav--prev").addEventListener("click", () => show(current - 1));
    lightbox.querySelector(".lightbox__nav--next").addEventListener("click", () => show(current + 1));
    lightbox.addEventListener("click", (e) => {
      if (e.target === lightbox) close();
    });
    document.addEventListener("keydown", (e) => {
      if (!lightbox.classList.contains("is-open")) return;
      if (e.key === "Escape") close();
      if (e.key === "ArrowLeft") show(current - 1);
      if (e.key === "ArrowRight") show(current + 1);
    });
  }

  /* Testimonials slideshow */
  document.querySelectorAll("[data-slideshow]").forEach((root) => {
    const slides = Array.from(root.querySelectorAll("[data-slide]"));
    const dots = Array.from(root.querySelectorAll("[data-slide-dot]"));
    const prevBtn = root.querySelector("[data-slide-prev]");
    const nextBtn = root.querySelector("[data-slide-next]");
    if (slides.length < 2) return;

    const autoplayMs = Number(root.dataset.autoplayMs) || 8000;
    let index = slides.findIndex((s) => s.classList.contains("is-active"));
    if (index < 0) index = 0;
    let timer = null;

    const show = (next) => {
      const target = ((next % slides.length) + slides.length) % slides.length;
      if (target === index) return;
      slides[index].classList.remove("is-active");
      slides[target].classList.add("is-active");
      if (dots[index]) {
        dots[index].classList.remove("is-active");
        dots[index].setAttribute("aria-selected", "false");
      }
      if (dots[target]) {
        dots[target].classList.add("is-active");
        dots[target].setAttribute("aria-selected", "true");
      }
      index = target;
    };

    const stop = () => {
      if (timer) {
        window.clearInterval(timer);
        timer = null;
      }
    };
    const start = () => {
      stop();
      timer = window.setInterval(() => show(index + 1), autoplayMs);
    };
    const restart = () => { stop(); start(); };

    if (prevBtn) prevBtn.addEventListener("click", () => { show(index - 1); restart(); });
    if (nextBtn) nextBtn.addEventListener("click", () => { show(index + 1); restart(); });
    dots.forEach((dot) => {
      dot.addEventListener("click", () => {
        show(Number(dot.dataset.slideDot));
        restart();
      });
    });

    root.addEventListener("mouseenter", stop);
    root.addEventListener("mouseleave", start);
    root.addEventListener("focusin", stop);
    root.addEventListener("focusout", start);

    if (!reducedMotion) start();
  });
});
