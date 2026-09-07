let currentMode = "simple";


const simplePanel = document.getElementById("simplePanel");
const complexPanel = document.getElementById("complexPanel");

const simpleModeButton =
    document.getElementById("simpleModeButton");

const complexModeButton =
    document.getElementById("complexModeButton");


const normalInput =
    document.getElementById("normalInput");

const normalResult =
    document.getElementById("normalResult");

const normalError =
    document.getElementById("normalError");

const normalAngle =
    document.getElementById("normalAngle");


const complexInput =
    document.getElementById("complexInput");

const complexResult =
    document.getElementById("complexResult");

const complexError =
    document.getElementById("complexError");

const complexAngle =
    document.getElementById("complexAngle");


const complexOperation =
    document.getElementById("complexOperation");

const complexVariable =
    document.getElementById("complexVariable");

const derivativeOrder =
    document.getElementById("derivativeOrder");

const orderControl =
    document.getElementById("orderControl");

const algebraTool =
    document.getElementById("algebraTool");

const matrixOperation =
    document.getElementById("matrixOperation");

const statisticsOperation =
    document.getElementById("statisticsOperation");


const variableControl =
    document.getElementById("variableControl");

const algebraControl =
    document.getElementById("algebraControl");

const matrixControl =
    document.getElementById("matrixControl");

const statisticsControl =
    document.getElementById("statisticsControl");


const expressionExample =
    document.getElementById("expressionExample");


const simpleEquals =
    document.getElementById("simpleEquals");

const complexEquals =
    document.getElementById("complexEquals");

const complexCalculate =
    document.getElementById("complexCalculate");


function switchMode(mode) {

    currentMode = mode;

    if (mode === "simple") {

        simplePanel.classList.remove("hidden");
        complexPanel.classList.add("hidden");

        simpleModeButton.classList.add("active");
        complexModeButton.classList.remove("active");

        normalInput.focus();

    } else {

        simplePanel.classList.add("hidden");
        complexPanel.classList.remove("hidden");

        simpleModeButton.classList.remove("active");
        complexModeButton.classList.add("active");

        complexInput.focus();

        updateOperationUI();
        updateExpressionExample();
    }
}


simpleModeButton.addEventListener(
    "click",
    () => switchMode("simple")
);

complexModeButton.addEventListener(
    "click",
    () => switchMode("complex")
);


function insertAtCursor(input, value) {

    const start = input.selectionStart;
    const end = input.selectionEnd;

    const before = input.value.substring(0, start);
    const after = input.value.substring(end);

    input.value = before + value + after;

    const cursorPosition = start + value.length;

    input.setSelectionRange(
        cursorPosition,
        cursorPosition
    );

    input.focus();
}


function deleteAtCursor(input) {

    const start = input.selectionStart;
    const end = input.selectionEnd;

    if (start !== end) {

        input.value =
            input.value.substring(0, start) +
            input.value.substring(end);

        input.setSelectionRange(start, start);

    } else if (start > 0) {

        input.value =
            input.value.substring(0, start - 1) +
            input.value.substring(start);

        input.setSelectionRange(
            start - 1,
            start - 1
        );
    }

    input.focus();
}


document
    .querySelectorAll("[data-normal]")
    .forEach(button => {

        button.addEventListener("click", () => {

            insertAtCursor(
                normalInput,
                button.dataset.normal
            );

            normalError.textContent = "";
        });
    });


document
    .querySelectorAll("[data-complex]")
    .forEach(button => {

        button.addEventListener("click", () => {

            insertAtCursor(
                complexInput,
                button.dataset.complex
            );

            complexError.textContent = "";

            updateExpressionExample();
        });
    });


document
    .getElementById("simpleAC")
    .addEventListener("click", () => {

        normalInput.value = "";
        normalResult.textContent = "0";
        normalError.textContent = "";
    });


document
    .getElementById("simpleDEL")
    .addEventListener("click", () => {

        deleteAtCursor(normalInput);

        normalError.textContent = "";
    });


document
    .getElementById("complexAC")
    .addEventListener("click", () => {

        complexInput.value = "";
        complexResult.textContent = "0";
        complexError.textContent = "";

        updateExpressionExample();
    });


document
    .getElementById("complexDEL")
    .addEventListener("click", () => {

        deleteAtCursor(complexInput);

        complexError.textContent = "";

        updateExpressionExample();
    });


async function calculateSimple() {

    const expression =
        normalInput.value.trim();

    if (!expression) {
        return;
    }

    normalError.textContent = "";

    try {

        const response = await fetch("/api/normal", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                expression: expression,

                angle_mode:
                    normalAngle.value

            })
        });


        const data = await response.json();


        if (!response.ok) {
            throw new Error(
                data.error || "Calculation error."
            );
        }


        normalResult.textContent =
            data.result;

    } catch (error) {

        normalError.textContent =
            error.message;
    }
}


async function calculateComplexExpression() {

    const expression =
        complexInput.value.trim();

    if (!expression) {
        return;
    }

    complexError.textContent = "";

    try {

        const response = await fetch("/api/normal", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                expression: expression,

                angle_mode:
                    complexAngle.value

            })
        });


        const data = await response.json();


        if (!response.ok) {
            throw new Error(
                data.error || "Calculation error."
            );
        }


        complexResult.textContent =
            data.result;

    } catch (error) {

        complexError.textContent =
            error.message;
    }
}


async function calculateComplex() {

    const expression =
        complexInput.value.trim();

    if (!expression) {
        return;
    }

    complexError.textContent = "";

    try {

        const response = await fetch("/api/complex", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                operation:
                    complexOperation.value,

                expression:
                    expression,

                variable:
                    complexVariable.value,

                order:
                    Number(derivativeOrder.value),

                tool:
                    algebraTool.value,

                matrix_operation:
                    matrixOperation.value,

                statistics_operation:
                    statisticsOperation.value,

                angle_mode:
                    complexAngle.value
            })
        });


        const data = await response.json();


        if (!response.ok) {
            throw new Error(
                data.error || "Calculation error."
            );
        }


        if (Array.isArray(data.result)) {

            complexResult.textContent =
                data.result.join(", ");

        } else {

            complexResult.textContent =
                data.result;
        }

    } catch (error) {

        complexError.textContent =
            error.message;
    }
}


simpleEquals.addEventListener(
    "click",
    calculateSimple
);


complexEquals.addEventListener(
    "click",
    calculateComplexExpression
);


complexCalculate.addEventListener(
    "click",
    calculateComplex
);


function updateOperationUI() {

    const operation =
        complexOperation.value;


    variableControl.classList.add("hidden");
    orderControl.classList.add("hidden");
    algebraControl.classList.add("hidden");
    matrixControl.classList.add("hidden");
    statisticsControl.classList.add("hidden");


    if (
        operation === "derivative" ||
        operation === "integral" ||
        operation === "solve"
    ) {

        variableControl.classList.remove("hidden");
    }


    if (
        operation === "derivative" ||
        operation === "integral"
    ) {

        orderControl.classList.remove("hidden");
    }


    if (operation === "algebra") {

        algebraControl.classList.remove("hidden");
    }


    if (operation === "matrix") {

        matrixControl.classList.remove("hidden");
    }


    if (operation === "statistics") {

        statisticsControl.classList.remove("hidden");
    }


    updateExpressionExample();
}


function updateExpressionExample() {

    if (!expressionExample) {
        return;
    }


    if (complexInput.value.trim() !== "") {

        expressionExample.textContent = "";

        return;
    }


    const examples = {

        derivative:
            "Example: x^3 + 2*x",

        integral:
            "Example: x^2 + 3*x",

        solve:
            "Example: x^2 + 2*x - 3 = 0",

        algebra:
            "Example: (x + 1)^2",

        matrix:
            "Example: 1,2;3,4",

        statistics:
            "Example: 10,20,30,40"
    };


    expressionExample.textContent =
        examples[complexOperation.value] || "";
}


complexOperation.addEventListener(
    "change",
    updateOperationUI
);


complexInput.addEventListener(
    "input",
    updateExpressionExample
);


document
    .getElementById("simpleFunctionsToggle")
    .addEventListener("click", () => {

        document
            .getElementById("simpleFunctions")
            .classList.toggle("hidden");
    });


document
    .querySelectorAll("[data-simple-tab]")
    .forEach(tab => {

        tab.addEventListener("click", () => {

            document
                .querySelectorAll("[data-simple-tab]")
                .forEach(item =>
                    item.classList.remove("active")
                );

            tab.classList.add("active");


            document
                .getElementById("simpleTrigFunctions")
                .classList.add("hidden");

            document
                .getElementById("simpleLogFunctions")
                .classList.add("hidden");

            document
                .getElementById("simpleOtherFunctions")
                .classList.add("hidden");


            if (tab.dataset.simpleTab === "trig") {

                document
                    .getElementById("simpleTrigFunctions")
                    .classList.remove("hidden");

            } else if (
                tab.dataset.simpleTab === "log"
            ) {

                document
                    .getElementById("simpleLogFunctions")
                    .classList.remove("hidden");

            } else {

                document
                    .getElementById("simpleOtherFunctions")
                    .classList.remove("hidden");
            }
        });
    });


document
    .getElementById("complexFunctionsToggle")
    .addEventListener("click", () => {

        document
            .getElementById("complexFunctions")
            .classList.toggle("hidden");
    });


document
    .querySelectorAll("[data-complex-tab]")
    .forEach(tab => {

        tab.addEventListener("click", () => {

            document
                .querySelectorAll("[data-complex-tab]")
                .forEach(item =>
                    item.classList.remove("active")
                );

            tab.classList.add("active");


            document
                .getElementById("complexTrigFunctions")
                .classList.add("hidden");

            document
                .getElementById("complexLogFunctions")
                .classList.add("hidden");

            document
                .getElementById("complexOtherFunctions")
                .classList.add("hidden");


            if (tab.dataset.complexTab === "trig") {

                document
                    .getElementById("complexTrigFunctions")
                    .classList.remove("hidden");

            } else if (
                tab.dataset.complexTab === "log"
            ) {

                document
                    .getElementById("complexLogFunctions")
                    .classList.remove("hidden");

            } else {

                document
                    .getElementById("complexOtherFunctions")
                    .classList.remove("hidden");
            }
        });
    });


normalAngle.addEventListener(
    "change",
    () => {
        normalError.textContent = "";
    }
);


complexAngle.addEventListener(
    "change",
    () => {
        complexError.textContent = "";
    }
);


document.addEventListener(
    "keydown",
    event => {

        if (event.key === "Enter") {

            if (currentMode === "simple") {

                calculateSimple();

            } else {

                calculateComplexExpression();
            }
        }


        if (event.key === "Escape") {

            if (currentMode === "simple") {

                normalInput.value = "";
                normalResult.textContent = "0";
                normalError.textContent = "";

            } else {

                complexInput.value = "";
                complexResult.textContent = "0";
                complexError.textContent = "";

                updateExpressionExample();
            }
        }
    }
);


const themeToggle =
    document.getElementById("themeToggle");


function applyTheme(theme) {

    if (theme === "dark") {

        document.body.classList.add("dark");

        themeToggle.textContent = "☀";

    } else {

        document.body.classList.remove("dark");

        themeToggle.textContent = "☾";
    }
}


themeToggle.addEventListener(
    "click",
    () => {

        const isDark =
            document.body.classList.contains("dark");

        const newTheme =
            isDark ? "light" : "dark";

        localStorage.setItem(
            "calculator-theme",
            newTheme
        );

        applyTheme(newTheme);
    }
);


const savedTheme =
    localStorage.getItem("calculator-theme") ||
    "light";

applyTheme(savedTheme);


updateOperationUI();
updateExpressionExample();

normalAngle.value = "DEG";
complexAngle.value = "DEG";

normalInput.focus();