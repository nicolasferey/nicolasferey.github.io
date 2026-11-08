// Compléments d'accessibilité aux composants du thème : noms accessibles manquants.
document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll("nav.md-nav[aria-labelledby]").forEach(function (nav) {
    // Sous-menus des pages d'index : le libellé référencé est vide, on reprend le titre de la rubrique.
    var label = document.getElementById(nav.getAttribute("aria-labelledby"));
    var link = nav.parentElement.querySelector(".md-nav__link");
    if (label && !label.textContent.trim() && link) {
      nav.setAttribute("aria-label", link.textContent.trim());
      nav.removeAttribute("aria-labelledby");
    }
  });
});
