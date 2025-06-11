let matrixId = localStorage.getItem('matrixId') ? parseInt(localStorage.getItem('matrixId')) : 0;
let matrixA = [];
let matrixB = [];
let calculationStartTime;

function generateMatrices() {
    const rowsA = parseInt(document.getElementById('rowsA').value);
    const colsA = parseInt(document.getElementById('colsA').value);
    const rowsB = parseInt(document.getElementById('rowsB').value);
    const colsB = parseInt(document.getElementById('colsB').value);

    if (colsA !== rowsB) {
        alert('Fehler: Die Anzahl der Spalten von Matrix A muss gleich der Anzahl der Zeilen von Matrix B sein.');
        return;
    }

    else if (colsA > 100 || rowsA > 100 || colsB > 100 || rowsB > 100) {
        alert('Fehler: Die Matrizen dürfen maximal 100 Zeilen und 100 Spalten haben.');
        return;
    }

    matrixA = generateMatrix('matrixA-content', rowsA, colsA);
    matrixB = generateMatrix('matrixB-content', rowsB, colsB);

    console.log('Matrix A:', matrixA);
    console.log('Matrix B:', matrixB);

    document.getElementById('result-section').style.display = 'none';
    document.getElementById('calculate-button').disabled = false;
}

function generateMatrix(matrixContentId, rows, cols) {
    const matrixContentDiv = document.getElementById(matrixContentId);
    let table = '<div class="matrix-table" style="grid-template-columns: repeat(' + Math.min(cols, 10) + ', 1fr);">';
    const matrix = [];
    for (let i = 0; i < rows; i++) {
        const row = [];
        for (let j = 0; j < cols; j++) {
            const randomNum = Math.floor(Math.random() * 10);
            row.push(randomNum);
            if (i < 10 && j < 10) {
                table += `<input type="text" value="${randomNum}">`;
            }
        }
        matrix.push(row);
    }
    if (rows > 10 || cols > 10) {
        table = '<p>Matrix ist zu groß, um angezeigt zu werden (maximal 10x10).</p>';
    }
    matrixContentDiv.innerHTML = table + '</div>';
    return matrix;
}

function sendMatricesToServer() {
    document.getElementById('calculation-time').textContent = '';
    calculationStartTime = Date.now();
    const resultMatrixDiv = document.getElementById('resultMatrix-div');
    resultMatrixDiv.style.display = 'none';

    matrixId++;
    localStorage.setItem('matrixId', matrixId);
    const body = JSON.stringify({ matrixA: matrixA, matrixB: matrixB, matrixId: matrixId });
    fetch('http://localhost:5000/process_matrices', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: body
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
        fetchMatrices();
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

function fetchMatrices() {
    const calculatingElement = document.getElementById('calculating');
    calculatingElement.style.display = 'block';

    const expectedDataCount = parseInt(document.getElementById('rowsA').value) * parseInt(document.getElementById('colsB').value);
    const startTime = Date.now();

    function checkData() {
        fetch(`http://localhost/api/v1/matrices?matrixID=${matrixId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data.length === expectedDataCount) {
                    calculatingElement.style.display = 'none';
                    displayResultMatrix(data);
                } else if (Date.now() - startTime < 3600000) {
                    setTimeout(checkData, 1000); // Check again after 1 second
                } else {
                    calculatingElement.style.display = 'none';
                    console.error('Error: Timeout after 1 hour');
                    alert('Fehler: Bitte versuchen Sie es erneut.');
                }
            })
            .catch(error => {
                console.error('Error fetching data:', error);
                setTimeout(checkData(), 5000);
            });
    }

    checkData();
}

function displayResultMatrix(data) {
    const calculationDuration = ((Date.now() - calculationStartTime) / 1000).toFixed(2);
    const matrix = [];
    data.forEach(([id, matrixID, i, j, result]) => {
        if (!matrix[i]) {
            matrix[i] = [];
        }
        matrix[i][j] = result;
    });

    console.log('Result:', matrix);
    const resultSection = document.getElementById('result-section');

    const resultMatrixDiv = document.getElementById('resultMatrix-div');
    resultMatrixDiv.className = 'matrix';
    resultMatrixDiv.innerHTML = '';
    resultMatrixDiv.style.display = 'block'; 

    const matrixContentDiv = document.createElement('div');
    matrixContentDiv.className = 'matrix-table';

    const resultH2 = document.createElement('h2');
    resultH2.textContent = 'Result';
    if (matrix.length > 10 || (matrix[0] && matrix[0].length > 10)) {
        matrixContentDiv.innerHTML = '<p>Matrix ist zu groß, um angezeigt zu werden (maximal 10x10).</p>';
    } else {
        matrixContentDiv.style.gridTemplateColumns = `repeat(${matrix[0].length}, 1fr)`;
        matrix.forEach(row => {
            row.forEach(value => {
                matrixContentDiv.innerHTML += `<input type="text" value="${value || 0}">`;
            });
        });
    }

    resultMatrixDiv.appendChild(resultH2);
    resultMatrixDiv.appendChild(matrixContentDiv);

    const durationElement = document.getElementById('calculation-time');
    durationElement.textContent = `This request took ${calculationDuration}s`;
    
    resultSection.style.display = 'block';
}
