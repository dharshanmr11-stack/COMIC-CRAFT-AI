document.addEventListener("DOMContentLoaded", () => {

    // -----------------------------------------
    // Running character animation
    // -----------------------------------------

    const characters = document.querySelectorAll(
        ".running-character"
    );

    characters.forEach((character, index) => {
        character.style.animationDelay =
            `${index * -4.5}s`;
    });


    // -----------------------------------------
    // Prompt character counter
    // -----------------------------------------

    const textarea =
        document.querySelector("#prompt");

    if (textarea) {

        const creatorBox =
            document.querySelector(".idea-input");

        const counter =
            document.createElement("small");

        counter.style.display = "block";
        counter.style.marginTop = "5px";
        counter.style.color = "#66739e";
        counter.style.fontSize = "11px";

        creatorBox.appendChild(counter);

        const updateCounter = () => {
            counter.textContent =
                `${textarea.value.length} / 2000`;
        };

        textarea.addEventListener(
            "input",
            updateCounter
        );

        updateCounter();
    }


    // -----------------------------------------
    // CREATE COMIC loading animation
    // -----------------------------------------

    const form =
        document.querySelector(".creator-box form");

    const button =
        document.querySelector(".generate-button");

    if (form && button) {

        form.addEventListener("submit", () => {

            // Prevent double click
            button.disabled = true;

            button.innerHTML =
                "🏃 Creating Comic...";

            button.style.opacity = "0.75";
            button.style.cursor = "wait";


            // ---------------------------------
            // Full screen loading overlay
            // ---------------------------------

            const loadingOverlay =
                document.createElement("div");

            loadingOverlay.id =
                "comic-loading-overlay";


            // ---------------------------------
            // Running track
            // ---------------------------------

            loadingOverlay.innerHTML = `

                <div class="comic-loading-scene">

                    <div class="running-track">

                        <div class="running-character">
                            🏃
                        </div>

                    </div>


                    <div class="comic-loader-content">

                        <div class="loader-title">
                            Creating Your Comic
                        </div>

                        <div class="loader-text">
                            AI is building your story...
                        </div>

                        <div class="loader-dots">

                            <span></span>
                            <span></span>
                            <span></span>

                        </div>

                    </div>

                </div>
            `;


            document.body.appendChild(
                loadingOverlay
            );
        });
    }


    // -----------------------------------------
    // Navigation active state
    // -----------------------------------------

    const navLinks =
        document.querySelectorAll(
            ".nav-links a"
        );

    navLinks.forEach((link) => {

        link.addEventListener("click", () => {

            navLinks.forEach((item) => {

                item.classList.remove(
                    "active"
                );

            });

            link.classList.add(
                "active"
            );
        });
    });


    // -----------------------------------------
    // Scroll reveal animation
    // -----------------------------------------

    const revealElements =
        document.querySelectorAll(
            ".feature-card, .about-card"
        );

    const revealObserver =
        new IntersectionObserver(
            (entries) => {

                entries.forEach((entry) => {

                    if (entry.isIntersecting) {

                        entry.target.style.opacity =
                            "1";

                        entry.target.style.transform =
                            "translateY(0)";
                    }

                });
            },
            {
                threshold: 0.15
            }
        );


    revealElements.forEach((element) => {

        element.style.opacity = "0";

        element.style.transform =
            "translateY(30px)";

        element.style.transition =
            "opacity 0.7s ease, transform 0.7s ease";

        revealObserver.observe(
            element
        );
    });


    // -----------------------------------------
    // Hero mouse movement
    // -----------------------------------------

    const hero =
        document.querySelector(
            ".hero-section"
        );

    const overlay =
        document.querySelector(
            ".hero-overlay"
        );

    if (hero && overlay) {

        hero.addEventListener(
            "mousemove",
            (event) => {

                const x =
                    (
                        event.clientX /
                        window.innerWidth -
                        0.5
                    ) * 20;

                const y =
                    (
                        event.clientY /
                        window.innerHeight -
                        0.5
                    ) * 20;

                overlay.style.transform =
                    `translate(${x}px, ${y}px)`;
            }
        );

        hero.addEventListener(
            "mouseleave",
            () => {

                overlay.style.transform =
                    "translate(0, 0)";
            }
        );
    }


    // -----------------------------------------
    // Console message
    // -----------------------------------------

    console.log(
        "%cComicCraft",
        "font-size:24px;font-weight:bold;color:#7c3aed;"
    );

    console.log(
        "AI Comic Story Creator initialized successfully."
    );

});