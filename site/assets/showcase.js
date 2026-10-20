/* Slideshows (arrows, dots, keyboard, swipe), current-skin highlight, copy button. No dependencies. */
(function () {
  "use strict";
  var shows = [].slice.call(document.querySelectorAll(".show"));

  shows.forEach(function (show) {
    var slides = [].slice.call(show.querySelectorAll(".slide"));
    var dots = [].slice.call(show.querySelectorAll(".dot"));
    var count = show.querySelector(".show-count");
    var text = show.querySelector(".show-text");
    var frame = show.querySelector(".show-frame");
    var i = 0, n = slides.length;

    function go(k) {
      k = (k + n) % n;
      if (k === i) return;
      slides[i].classList.remove("is-active"); slides[i].setAttribute("aria-hidden", "true");
      dots[i].classList.remove("is-active"); dots[i].removeAttribute("aria-current");
      i = k;
      slides[i].classList.add("is-active"); slides[i].removeAttribute("aria-hidden");
      dots[i].classList.add("is-active"); dots[i].setAttribute("aria-current", "true");
      count.textContent = (i + 1) + " / " + n;
      text.textContent = slides[i].getAttribute("data-caption");
      // warm the next image so the following click is instant
      var nx = slides[(i + 1) % n].querySelector("img");
      if (nx && nx.loading === "lazy") nx.loading = "eager";
    }
    show._go = function (d) { go(i + d); };

    show.querySelector(".prev").addEventListener("click", function () { go(i - 1); });
    show.querySelector(".next").addEventListener("click", function () { go(i + 1); });
    dots.forEach(function (d, k) { d.addEventListener("click", function () { go(k); }); });

    // swipe (touch and pen; mouse drags are ignored so text selection elsewhere is unaffected)
    var x0 = null, y0 = 0;
    frame.addEventListener("pointerdown", function (e) { if (e.pointerType !== "mouse") { x0 = e.clientX; y0 = e.clientY; } });
    frame.addEventListener("pointerup", function (e) {
      if (x0 === null) return;
      var dx = e.clientX - x0, dy = e.clientY - y0; x0 = null;
      if (Math.abs(dx) > 40 && Math.abs(dx) > Math.abs(dy) * 1.2) go(i + (dx < 0 ? 1 : -1));
    });
    frame.addEventListener("pointercancel", function () { x0 = null; });
  });

  // Left / Right drive the slideshow that has focus, or otherwise the one most in view.
  function showInView() {
    var best = null, bestArea = 0, vh = window.innerHeight;
    shows.forEach(function (s) {
      var r = s.querySelector(".show-frame").getBoundingClientRect();
      var vis = Math.max(0, Math.min(r.bottom, vh) - Math.max(r.top, 0));
      if (vis > bestArea) { bestArea = vis; best = s; }
    });
    return bestArea > 120 ? best : null;
  }
  document.addEventListener("keydown", function (e) {
    if (e.key !== "ArrowLeft" && e.key !== "ArrowRight") return;
    if (e.altKey || e.ctrlKey || e.metaKey) return;
    var t = e.target;
    if (t && (t.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName))) return;
    var s = (t && t.closest && t.closest(".show")) || showInView();
    if (!s) return;
    e.preventDefault();
    s._go(e.key === "ArrowRight" ? 1 : -1);
  });

  // highlight the skin in view in the top bar
  var links = {};
  [].slice.call(document.querySelectorAll(".top-nav a")).forEach(function (a) { links[a.hash.slice(1)] = a; });
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        var a = links[en.target.id];
        if (!a) return;
        if (en.isIntersecting) {
          Object.keys(links).forEach(function (k) { links[k].classList.remove("is-current"); });
          a.classList.add("is-current");
          var nav = a.closest(".top-nav");
          if (nav) nav.scrollTo({ left: a.offsetLeft - 40, behavior: "auto" });
        }
      });
    }, { rootMargin: "-45% 0px -50% 0px" });
    [].slice.call(document.querySelectorAll(".skin")).forEach(function (s) { io.observe(s); });
  }

  // copy the repository address
  [].slice.call(document.querySelectorAll(".copy")).forEach(function (b) {
    b.addEventListener("click", function () {
      var v = b.getAttribute("data-copy");
      var done = function () { b.textContent = "Copied"; setTimeout(function () { b.textContent = "Copy"; }, 1800); };
      if (navigator.clipboard && window.isSecureContext) navigator.clipboard.writeText(v).then(done, function () {});
      else {
        var ta = document.createElement("textarea"); ta.value = v; document.body.appendChild(ta); ta.select();
        try { document.execCommand("copy"); done(); } catch (err) {} document.body.removeChild(ta);
      }
    });
  });
})();
