document.addEventListener("DOMContentLoaded", () => {
  const yearNode = document.querySelector("[data-current-year]");
  if (yearNode) {
    yearNode.textContent = String(new Date().getFullYear());
  }

  const thanksEl = document.querySelector("[data-contact-thanks]");
  if (thanksEl && new URLSearchParams(window.location.search).get("sent") === "1") {
    thanksEl.hidden = false;
    const form = document.querySelector(".contact-form");
    if (form) form.hidden = true;
  }

  document.querySelectorAll("[data-slideshow]").forEach((root) => {
    const slides = Array.from(root.querySelectorAll("[data-slide]"));
    const dots = Array.from(root.querySelectorAll("[data-slide-dot]"));
    const prevBtn = root.querySelector("[data-slide-prev]");
    const nextBtn = root.querySelector("[data-slide-next]");
    if (slides.length < 2) return;

    const autoplayMs = Number(root.dataset.autoplayMs) || 7000;
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

    const start = () => {
      stop();
      timer = window.setInterval(() => show(index + 1), autoplayMs);
    };
    const stop = () => {
      if (timer) {
        window.clearInterval(timer);
        timer = null;
      }
    };
    const restart = () => { stop(); start(); };

    if (prevBtn) prevBtn.addEventListener("click", () => { show(index - 1); restart(); });
    if (nextBtn) nextBtn.addEventListener("click", () => { show(index + 1); restart(); });
    dots.forEach((dot) => {
      dot.addEventListener("click", () => {
        const target = Number(dot.dataset.slideDot);
        show(target);
        restart();
      });
    });

    root.addEventListener("mouseenter", stop);
    root.addEventListener("mouseleave", start);
    root.addEventListener("focusin", stop);
    root.addEventListener("focusout", start);

    if (!window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      start();
    }
  });
});
