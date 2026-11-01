// L'adresse n'apparaît pas en clair dans le HTML : elle est reconstituée au chargement.
function revealMail() {
  document.querySelectorAll("a.js-mail").forEach(function (a) {
    var rev = function (s) { return s.split("").reverse().join(""); };
    var addr = rev(a.dataset.u) + "\u0040" + rev(a.dataset.d);
    a.href = "mai" + "lto:" + addr;
    if (a.dataset.text) a.textContent = addr;
  });
}
document.addEventListener("DOMContentLoaded", revealMail);
