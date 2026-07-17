/* Pasadena Country Garden School — main.js
   Announcement bar dismissal · mobile nav · scroll reveals · gallery lightbox
   No dependencies. Everything degrades gracefully without JS. */

(function () {
  "use strict";

  /* --- Announcement bar ---------------------------------------------------
     Dismissal is remembered per message text, so when the client edits the
     announcement everyone sees the new one again. */
  var announce = document.querySelector("[data-announce]");
  if (announce) {
    var msg = announce.querySelector("p");
    var key = "pcgs-announce:" + (msg ? msg.textContent.trim().slice(0, 60) : "default");
    try {
      if (localStorage.getItem(key) === "dismissed") announce.hidden = true;
    } catch (e) { /* private mode — just show it */ }

    var closeBtn = announce.querySelector("[data-announce-close]");
    if (closeBtn) {
      closeBtn.addEventListener("click", function () {
        announce.hidden = true;
        try { localStorage.setItem(key, "dismissed"); } catch (e) {}
      });
    }
  }

  /* --- Mobile navigation --------------------------------------------------- */
  var toggle = document.querySelector("[data-nav-toggle]");
  var nav = document.querySelector("[data-nav]");
  if (toggle && nav) {
    var setNav = function (open) {
      toggle.setAttribute("aria-expanded", String(open));
      nav.dataset.open = String(open);
      toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    };
    toggle.addEventListener("click", function () {
      setNav(toggle.getAttribute("aria-expanded") !== "true");
    });
    nav.addEventListener("click", function (e) {
      if (e.target.closest("a")) setNav(false);
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && toggle.getAttribute("aria-expanded") === "true") {
        setNav(false);
        toggle.focus();
      }
    });
  }

  /* --- Scroll reveals ------------------------------------------------------ */
  var reveals = document.querySelectorAll("[data-reveal]");
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reveals.length && !reduced && "IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          io.unobserve(entry.target);
        }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.05 });
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add("is-visible"); });
  }

  /* --- Gallery lightbox ----------------------------------------------------
     The grid shows 600px square thumbnails. A tile carrying data-full points at
     the full-size uncropped photo, which is loaded on demand — cloning the
     thumbnail would just upscale a crop. Falls back to cloning whatever the
     tile holds (e.g. a placeholder) when there's no data-full. */
  var lightbox = document.querySelector("[data-lightbox]");
  if (lightbox) {
    var body = lightbox.querySelector("[data-lightbox-body]");
    var caption = lightbox.querySelector("[data-lightbox-caption]");
    var opener = null;

    document.querySelectorAll("[data-lightbox-open]").forEach(function (tile) {
      tile.addEventListener("click", function () {
        opener = tile;
        var text = tile.dataset.caption || "";
        body.innerHTML = "";

        if (tile.dataset.full) {
          var full = new Image();
          full.src = tile.dataset.full;
          full.alt = text;
          body.appendChild(full);
        } else {
          var media = tile.querySelector("img, .ph");
          if (media) body.appendChild(media.cloneNode(true));
        }

        caption.textContent = text;
        if (typeof lightbox.showModal === "function") lightbox.showModal();
      });
    });

    lightbox.querySelector("[data-lightbox-close]").addEventListener("click", function () {
      lightbox.close();
    });
    lightbox.addEventListener("click", function (e) {
      if (e.target === lightbox) lightbox.close();
    });
    lightbox.addEventListener("close", function () {
      if (opener) opener.focus();
    });
  }

  /* The contact form was removed deliberately: it handed off via mailto: to an
     inbox that isn't monitored for enquiries, so a parent could send a tour
     request that nobody ever read. The phone is the real channel. */

  /* --- Footer year --------------------------------------------------------- */
  var year = document.querySelector("[data-year]");
  if (year) year.textContent = new Date().getFullYear();
})();
