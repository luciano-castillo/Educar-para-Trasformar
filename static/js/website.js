document.addEventListener(
    "DOMContentLoaded",
    () => {

        const carrusel = document.querySelector(
            "[data-carrusel]"
        );

        if (!carrusel) {
            return;
        }


        const slides = Array.from(
            carrusel.querySelectorAll(
                "[data-slide]"
            )
        );


        const indicadores = Array.from(
            carrusel.querySelectorAll(
                "[data-indicador]"
            )
        );


        const botonAnterior = (
            carrusel.querySelector(
                "[data-carrusel-anterior]"
            )
        );


        const botonSiguiente = (
            carrusel.querySelector(
                "[data-carrusel-siguiente]"
            )
        );


        let indiceActual = 0;

        let intervalo = null;


        function mostrarSlide(indice) {

            indiceActual = (
                indice + slides.length
            ) % slides.length;


            slides.forEach(
                (slide, indiceSlide) => {

                    slide.classList.toggle(
                        "web-slide-activo",
                        indiceSlide === indiceActual
                    );

                }
            );


            indicadores.forEach(
                (
                    indicador,
                    indiceIndicador
                ) => {

                    indicador.classList.toggle(
                        "web-indicador-activo",
                        indiceIndicador
                            === indiceActual
                    );

                }
            );

        }


        function siguienteSlide() {

            mostrarSlide(
                indiceActual + 1
            );

        }


        function anteriorSlide() {

            mostrarSlide(
                indiceActual - 1
            );

        }


        function iniciarAutomatico() {

            detenerAutomatico();

            intervalo = setInterval(
                siguienteSlide,
                3000
            );

        }


        function detenerAutomatico() {

            if (intervalo) {

                clearInterval(
                    intervalo
                );

                intervalo = null;

            }

        }


        if (botonSiguiente) {

            botonSiguiente.addEventListener(
                "click",
                () => {

                    siguienteSlide();
                    iniciarAutomatico();

                }
            );

        }


        if (botonAnterior) {

            botonAnterior.addEventListener(
                "click",
                () => {

                    anteriorSlide();
                    iniciarAutomatico();

                }
            );

        }


        indicadores.forEach(
            indicador => {

                indicador.addEventListener(
                    "click",
                    () => {

                        const indice = Number(
                            indicador.dataset.indicador
                        );

                        mostrarSlide(
                            indice
                        );

                        iniciarAutomatico();

                    }
                );

            }
        );


        carrusel.addEventListener(
            "mouseenter",
            detenerAutomatico
        );


        carrusel.addEventListener(
            "mouseleave",
            iniciarAutomatico
        );


        carrusel.addEventListener(
            "focusin",
            detenerAutomatico
        );


        carrusel.addEventListener(
            "focusout",
            iniciarAutomatico
        );


        mostrarSlide(0);

        iniciarAutomatico();

    }
);

// =========================================================
// MENÚ RESPONSIVE
// =========================================================

document.addEventListener(
    "DOMContentLoaded",
    () => {

        const botonMenu =
            document.querySelector(
                "[data-menu-toggle]"
            );

        const menu =
            document.querySelector(
                "[data-menu]"
            );


        if (!botonMenu || !menu) {
            return;
        }


        const cerrarMenu = () => {

            menu.classList.remove(
                "web-nav-abierto"
            );

            botonMenu.classList.remove(
                "web-menu-toggle-activo"
            );

            botonMenu.setAttribute(
                "aria-expanded",
                "false"
            );

            botonMenu.setAttribute(
                "aria-label",
                "Abrir menú de navegación"
            );
        };


        botonMenu.addEventListener(
            "click",
            () => {

                const abierto =
                    menu.classList.toggle(
                        "web-nav-abierto"
                    );


                botonMenu.classList.toggle(
                    "web-menu-toggle-activo",
                    abierto
                );


                botonMenu.setAttribute(
                    "aria-expanded",
                    abierto
                        ? "true"
                        : "false"
                );


                botonMenu.setAttribute(
                    "aria-label",
                    abierto
                        ? "Cerrar menú de navegación"
                        : "Abrir menú de navegación"
                );
            }
        );


        menu
            .querySelectorAll("a")
            .forEach(
                enlace => {

                    enlace.addEventListener(
                        "click",
                        cerrarMenu
                    );

                }
            );


        document.addEventListener(
            "keydown",
            evento => {

                if (
                    evento.key ===
                    "Escape"
                ) {

                    cerrarMenu();
                }
            }
        );


        window.addEventListener(
            "resize",
            () => {

                if (
                    window.innerWidth >
                    1050
                ) {

                    cerrarMenu();
                }
            }
        );

    }
);