// Icônes de contact dans l'en-tête, à gauche du bouton de mode sombre : courriel + liens du pied de page.
document.addEventListener("DOMContentLoaded", function () {
  var option = document.querySelector(".md-header__option");
  var social = document.querySelector(".md-footer .md-social");
  if (!option || !social) return;
  var box = document.createElement("div");
  box.className = "header-icons";
  var mail = document.createElement("a");
  mail.className = "js-mail md-social__link";
  mail.href = "#";
  mail.title = "Courriel";
  mail.setAttribute("aria-label", "Courriel");
  mail.dataset.u = "yeref.salocin";
  mail.dataset.d = "rf.yalcas-sirap-etisrevinu";
  mail.innerHTML = '<span class="twemoji"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--! Font Awesome Free 7.1.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free (Icons: CC BY 4.0, Fonts: SIL OFL 1.1, Code: MIT License) Copyright 2025 Fonticons, Inc.--><path d="M48 64C21.5 64 0 85.5 0 112c0 15.1 7.1 29.3 19.2 38.4l208 156a48 48 0 0 0 57.6 0l208-156c12.1-9.1 19.2-23.3 19.2-38.4 0-26.5-21.5-48-48-48zM0 196v188c0 35.3 28.7 64 64 64h384c35.3 0 64-28.7 64-64V196L313.6 344.8c-34.1 25.6-81.1 25.6-115.2 0z"/></svg></span>';
  box.appendChild(mail);
  social.querySelectorAll("a").forEach(function (a) {
    var c = a.cloneNode(true);
    c.setAttribute("aria-label", a.title);
    box.appendChild(c);
  });
  option.parentNode.insertBefore(box, option);
  if (typeof revealMail === "function") revealMail();
});
