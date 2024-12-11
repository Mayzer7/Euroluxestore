// Получаем элементы input и button
const inputField = document.getElementById("input-search");
const submitButton = document.getElementById("search-button");

// Функция для проверки ввода
function toggleButtonState() {
    if (inputField.value.trim() === "") {
        submitButton.disabled = true;  // Отключаем кнопку, если поле пустое
    } else {
        submitButton.disabled = false;  // Включаем кнопку, если есть текст
    }
}

// Слушаем событие input (когда пользователь вводит текст)
inputField.addEventListener("input", toggleButtonState);

// Начальная проверка при загрузке страницы
toggleButtonState();