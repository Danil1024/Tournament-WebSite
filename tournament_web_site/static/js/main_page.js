// Получаем элементы
var modal = document.getElementById("myModal");
var btn = document.getElementById("buttonLogReg");
var span = document.getElementsByClassName("close")[0];

// Открываем модальное окно при клике на кнопку
btn.onclick = function () {
  modal.style.display = "block";
};

// Закрываем модальное окно при клике на кнопку "x"
span.onclick = function () {
  modal.style.display = "none";
};

// Закрываем модальное окно при клике вне его
window.onclick = function (event) {
  if (event.target == modal) {
    modal.style.display = "none";
  }
};
const loginBtn = document.getElementById("loginBtn");
const registerBtn = document.getElementById("registerBtn");
const loginForm = document.getElementById("loginForm");
const registerForm = document.getElementById("registerForm");

function login() {
  loginForm.style.display = "flex";
  registerForm.style.display = "none";
  loginBtn.classList.add("active");
  registerBtn.classList.remove("active");
}

function register() {
  loginForm.style.display = "none";
  registerForm.style.display = "flex";
  registerBtn.classList.add("active");
  loginBtn.classList.remove("active");
}
