// This is the main JavaScript file for your portfolio.
// We will add animations and interactive features here.

document.addEventListener("DOMContentLoaded", (event) => {
    console.log("Portfolio site is loaded and ready for animations!");

    // Example: Add a class to a project card on hover
    const projectCards = document.querySelectorAll(".project-card");
    projectCards.forEach((card) => {
        card.addEventListener("mouseenter", () => {
            card.classList.add("hovered");
        });
        card.addEventListener("mouseleave", () => {
            card.classList.remove("hovered");
        });
    });
});
// ===== Footer Local Time Updater =====
(function updateLocalTime() {
    function pad(n) {
        return (n < 10 ? "0" : "") + n;
    }

    function showTime() {
        const el = document.getElementById("local-time");
        if (!el) return;

        const now = new Date();
        const hours = now.getHours();
        const minutes = pad(now.getMinutes());
        const isPM = hours >= 12;
        const hour12 = ((hours + 11) % 12) + 1;

        let tz = "LOCAL";
        try {
            const tzFull =
                Intl.DateTimeFormat().resolvedOptions().timeZone || "";
            tz = tzFull.split("/").pop().replace("_", " ") || "LOCAL";
        } catch (e) {}

        el.textContent = `${pad(hour12)}:${minutes} ${isPM ? "PM" : "AM"} ${tz}`;
    }

    showTime();
    setInterval(showTime, 60000);
})();
// ===== Smooth Scrolling + Scroll Animations =====
(function () {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

    // Smooth scrolling (Lenis)
    const lenis = new Lenis({
        duration: 1.1,
        smooth: true,
        smoothWheel: true,
    });

    function raf(time) {
        lenis.raf(time);
        ScrollTrigger.update();
        requestAnimationFrame(raf);
    }
    requestAnimationFrame(raf);

    // GSAP Scroll Animations
    gsap.registerPlugin(ScrollTrigger);

    gsap.utils.toArray(".animate-fade").forEach((el) => {
        gsap.fromTo(
            el,
            { opacity: 0, y: 24 },
            {
                opacity: 1,
                y: 0,
                duration: 0.9,
                ease: "power3.out",
                scrollTrigger: {
                    trigger: el,
                    start: "top 85%",
                },
            },
        );
    });
})();

// NAVBAR: hide on scroll down, show on scroll up
(function () {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

    const header = document.querySelector("header");
    if (!header) return;

    let lastY = window.scrollY || 0;
    let ticking = false;
    const THROTTLE_MS = 50;
    const UP_THRESHOLD = 10; // px of upward movement to reveal

    function onScroll() {
        const y = window.scrollY || 0;
        if (!ticking) {
            window.setTimeout(() => {
                const delta = y - lastY;

                if (delta > 5 && y > 100) {
                    // scrolling down
                    header.classList.add("nav-hidden");
                    header.classList.remove("nav-solid");
                } else if (delta < -UP_THRESHOLD) {
                    // scrolling up
                    header.classList.remove("nav-hidden");
                    header.classList.add("nav-solid");
                } else if (y <= 20) {
                    // near top
                    header.classList.remove("nav-hidden");
                    header.classList.remove("nav-solid");
                }

                lastY = y;
                ticking = false;
            }, THROTTLE_MS);
            ticking = true;
        }
    }

    window.addEventListener("scroll", onScroll, { passive: true });
})();

// ---------- PAGE LOADER (2s) with smart handling of anchors ----------
(function () {
    const loader = document.getElementById("page-loader");
    if (!loader) return;

    const DEFAULT_MS = 1000; // 2 seconds
    const REDUCED_MS = 600;
    const prefersReduced = window.matchMedia(
        "(prefers-reduced-motion: reduce)",
    ).matches;
    const showMs = prefersReduced ? REDUCED_MS : DEFAULT_MS;

    // show for initial load, then hide
    loader.classList.remove("hidden");
    setTimeout(() => loader.classList.add("hidden"), showMs);

    // helper: smooth scroll to hash on same page
    function smoothScrollToHash(hash) {
        try {
            const target = document.querySelector(hash);
            if (!target) return;
            if (window.lenis && typeof window.lenis.scrollTo === "function") {
                lenis.scrollTo(target, { offset: 0, duration: 0.9 });
            } else {
                target.scrollIntoView({ behavior: "smooth" });
            }
        } catch (e) {
            /* ignore */
        }
    }

    document.addEventListener(
        "click",
        (e) => {
            const a = e.target.closest("a");
            if (!a) return;

            const href = a.getAttribute("href") || "";
            // ignore special / external cases
            if (href.startsWith("mailto:") || href.startsWith("tel:")) return;
            if (a.target === "_blank" || a.hasAttribute("download")) return;

            // Absolute URL object for robust checks
            let dest;
            try {
                dest = new URL(a.href, location.href);
            } catch (err) {
                // malformed href — ignore
                return;
            }

            // external origin => do nothing
            if (dest.origin !== location.origin) return;

            // Same-page navigation (pathnames equal):
            if (dest.pathname === location.pathname) {
                // if it's only an anchor/hash on same page -> smooth scroll (no overlay)
                if (dest.hash) {
                    e.preventDefault();
                    smoothScrollToHash(dest.hash);
                    return;
                }
                // same page, no hash -> let browser handle (no overlay)
                return;
            }

            // Internal navigation to a different path on same origin -> show loader then navigate
            e.preventDefault();
            loader.classList.remove("hidden");
            setTimeout(() => {
                window.location.href = dest.href;
            }, showMs);
        },
        { passive: false },
    );
})();

// HERO MARQUEE: make viewport size equal to one item so only one name is visible
(function () {
    if (
        window.matchMedia &&
        window.matchMedia("(prefers-reduced-motion: reduce)").matches
    ) {
        // if reduced motion is preferred, stop here
        return;
    }

    function setupMarquee() {
        document.querySelectorAll(".marquee-viewport").forEach((viewport) => {
            const track = viewport.querySelector(".marquee-track");
            const item = viewport.querySelector(".marquee-item");
            if (!track || !item) return;

            // measure the item width including padding/border
            const itemWidth = Math.ceil(item.getBoundingClientRect().width);

            // set viewport width to item width so only one item is visible
            viewport.style.width = itemWidth + "px";

            // set duration proportionally so speed feels consistent across screen sizes
            // lower divisor = faster; 40 gives a comfortable slow scroll
            const duration = Math.max(8, Math.round(itemWidth / 40)); // seconds (min 8s)
            track.style.setProperty("--marquee-duration", duration + "s");
        });
    }

    // run on load and on resize (debounced)
    window.addEventListener("load", setupMarquee);
    let resizeTO;
    window.addEventListener("resize", function () {
        clearTimeout(resizeTO);
        resizeTO = setTimeout(setupMarquee, 120);
    });
})();

// FOOTER: add class when footer enters viewport for smooth transition
(function () {
    const footer = document.querySelector(".site-footer");
    if (!footer || !("IntersectionObserver" in window)) return;

    const io = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    footer.classList.add("footer-visible");
                } else {
                    footer.classList.remove("footer-visible");
                }
            });
        },
        {
            root: null,
            threshold: 0.08, // when ~8% of footer is visible, toggle class
        },
    );

    io.observe(footer);
})();
