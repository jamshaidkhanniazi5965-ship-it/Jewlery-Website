/* Germani Jewellery — site behaviour */
(function () {
  "use strict";

  var header = document.querySelector(".site-header");
  var body = document.body;

  /* Header shrink on scroll */
  function onScroll() {
    if (header) header.classList.toggle("is-scrolled", window.scrollY > 40);
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* Mobile navigation */
  var toggle = document.querySelector(".nav-toggle");
  if (toggle && header) {
    toggle.addEventListener("click", function () {
      var open = !body.classList.contains("nav-open");
      document.documentElement.style.setProperty("--nav-top", header.getBoundingClientRect().bottom + "px");
      body.classList.toggle("nav-open", open);
      toggle.setAttribute("aria-expanded", String(open));
      body.style.overflow = open ? "hidden" : "";
    });
    document.querySelectorAll(".main-nav a").forEach(function (a) {
      a.addEventListener("click", function () {
        body.classList.remove("nav-open");
        toggle.setAttribute("aria-expanded", "false");
        body.style.overflow = "";
      });
    });
  }

  /* Reveal on scroll */
  var reveals = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add("is-in"); io.unobserve(e.target); }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add("is-in"); });
  }

  /* Collections: filter */
  var pieces = Array.prototype.slice.call(document.querySelectorAll(".piece"));
  var filterBtns = document.querySelectorAll(".filters button");

  function applyFilter(cat) {
    filterBtns.forEach(function (b) { b.setAttribute("aria-pressed", String(b.dataset.filter === cat)); });
    pieces.forEach(function (p) {
      p.hidden = !(cat === "all" || p.dataset.cat.split(" ").indexOf(cat) !== -1);
    });
  }
  if (filterBtns.length) {
    filterBtns.forEach(function (b) {
      b.addEventListener("click", function () {
        applyFilter(b.dataset.filter);
        history.replaceState(null, "", b.dataset.filter === "all" ? location.pathname : "#" + b.dataset.filter);
      });
    });
    var isFilter = function (h) { return Array.prototype.some.call(filterBtns, function (b) { return b.dataset.filter === h; }); };
    var initial = location.hash.replace("#", "");
    applyFilter(isFilter(initial) ? initial : "all");
    /* in-page links such as #rings filter the grid and scroll back to it */
    window.addEventListener("hashchange", function () {
      var h = location.hash.replace("#", "");
      if (!isFilter(h)) return;
      applyFilter(h);
      var f = document.querySelector(".filters"), hd = document.querySelector(".site-header");
      window.scrollTo({ top: f.getBoundingClientRect().top + window.scrollY - (hd ? hd.offsetHeight : 0) - 16, behavior: "smooth" });
    });
  }

  /* Collections: lightbox */
  var lb = document.querySelector(".lightbox");
  if (lb && pieces.length) {
    var lbImg = lb.querySelector(".lightbox__media img");
    var lbMedia = lb.querySelector(".lightbox__media");
    var lbName = lb.querySelector(".lightbox__name");
    var lbDesc = lb.querySelector(".lightbox__desc");
    var lbCat = lb.querySelector(".lightbox__cat");
    var lbEnquire = lb.querySelector(".lightbox__enquire");
    var current = 0;
    var lastFocus = null;

    function visible() { return pieces.filter(function (p) { return !p.hidden; }); }

    function show(piece) {
      var img = piece.querySelector("img");
      lbImg.src = img.src;
      lbImg.alt = img.alt;
      lbMedia.classList.toggle("is-studio", piece.querySelector(".piece__img--studio") !== null);
      lbName.textContent = piece.querySelector(".piece__name").textContent;
      lbDesc.textContent = piece.querySelector(".piece__desc").textContent;
      lbCat.textContent = piece.dataset.label || "";
      lbEnquire.href = "contact.html?piece=" + encodeURIComponent(lbName.textContent) + "#appointment";
    }

    function open(piece) {
      lastFocus = document.activeElement;
      current = visible().indexOf(piece);
      show(piece);
      lb.classList.add("is-open");
      lb.setAttribute("aria-hidden", "false");
      body.style.overflow = "hidden";
      lb.querySelector(".lightbox__close").focus();
    }

    function close() {
      lb.classList.remove("is-open");
      lb.setAttribute("aria-hidden", "true");
      body.style.overflow = "";
      if (lastFocus) lastFocus.focus();
    }

    function step(dir) {
      var list = visible();
      current = (current + dir + list.length) % list.length;
      show(list[current]);
    }

    pieces.forEach(function (p) {
      p.setAttribute("tabindex", "0");
      p.setAttribute("role", "button");
      p.addEventListener("click", function () { open(p); });
      p.addEventListener("keydown", function (e) {
        if (e.key === "Enter" || e.key === " ") { e.preventDefault(); open(p); }
      });
    });
    lb.querySelector(".lightbox__close").addEventListener("click", close);
    lb.querySelector(".lightbox__nav--prev").addEventListener("click", function () { step(-1); });
    lb.querySelector(".lightbox__nav--next").addEventListener("click", function () { step(1); });
    document.addEventListener("keydown", function (e) {
      if (!lb.classList.contains("is-open")) return;
      if (e.key === "Escape") close();
      if (e.key === "ArrowLeft") step(-1);
      if (e.key === "ArrowRight") step(1);
    });
  }

  /* Contact: prefill piece + Netlify form submit */
  var form = document.querySelector(".form");
  if (form) {
    var piece = new URLSearchParams(location.search).get("piece");
    if (piece) {
      var pieceField = form.querySelector("[name=piece]");
      if (pieceField) pieceField.value = piece;
      var interest = form.querySelector("[name=interest]");
      if (interest && /academy/i.test(piece)) interest.value = "Germani Jewellery Academy";
    }
    form.addEventListener("submit", function (e) {
      if (!window.fetch) return;
      e.preventDefault();
      var data = new URLSearchParams(new FormData(form)).toString();
      var btn = form.querySelector("button[type=submit]");
      btn.disabled = true;
      fetch("/", { method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded" }, body: data })
        .then(function (r) {
          if (!r.ok) throw new Error(r.status);
          form.hidden = true;
          document.querySelector(".form-success").classList.add("is-visible");
        })
        .catch(function () {
          btn.disabled = false;
          alert("Sorry, your request could not be sent. Please call or email us directly.");
        });
    });
  }

  /* Footer year */
  var y = document.querySelector("[data-year]");
  if (y) y.textContent = new Date().getFullYear();
})();
