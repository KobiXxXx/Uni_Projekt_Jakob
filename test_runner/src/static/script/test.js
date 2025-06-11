function startHttpTest() {
    const progressElement = document.getElementById('httpTestProgress');
    const resultElement = document.getElementById('httpTestResult');
    const testSize = document.getElementById('testSize').value;
    resultElement.innerText = ''
    progressElement.innerHTML = '<span class="test-progress">Test in Progress...</span>';
    fetch('/trigger_http', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ size: testSize})
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === "NULL") {
            throw new Error('Response is NULL');
        }
        const message = document.createElement('div');
        message.innerText = 'Result: ' + data.message;
        progressElement.innerHTML = '<span class="test-completed">Test Completed</span>';
        resultElement.appendChild(message);
    })
    .catch(error => {
        const message = document.createElement('div');
        message.innerText = error;
        progressElement.innerText = 'Test failed';
        resultElement.appendChild(message);
    });
}

function startHealthCheckTest() {
    const progressElement = document.getElementById('healthCheckProgress');
    const resultElement = document.getElementById('healthCheckResult');
    const testSize = document.getElementById('testSize').value;
    resultElement.innerText = ''
    progressElement.innerHTML = '<span class="test-progress">Test in Progress...</span>';
    fetch('/trigger_health_check', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ size: testSize})
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === "NULL") {
            throw new Error('Response is NULL');
        }
        const message = document.createElement('div');
        message.innerText = 'Result: ' + data.message;
        progressElement.innerHTML = '<span class="test-completed">Test Completed</span>';
        resultElement.appendChild(message);
    })
    .catch(error => {
        const message = document.createElement('div');
        message.innerText = 'Error: ' + error;
        progressElement.innerText = 'Test failed';
        resultElement.appendChild(message);
    });
}

function startPerformanceTest() {
    const progressElement = document.getElementById('performanceTestProgress');
    const resultElement = document.getElementById('performanceTestResult');
    const testSize = document.getElementById('testSize').value;
    const x = document.getElementById('x').value;
    const y = document.getElementById('y').value;
    resultElement.innerText = ''
    progressElement.innerHTML = '<span class="test-progress">Test in Progress...</span>';
    fetch('/trigger_performance', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ size: testSize, x: x, y: y})
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === "NULL") {
            throw new Error('Response is NULL');
        }
        const message = document.createElement('div');
        message.innerText = 'Result: ' + JSON.stringify(data.message, null, 2);
        progressElement.innerHTML = '<span class="test-completed">Test Completed</span>';
        resultElement.appendChild(message);
    })
    .catch(error => {
        const message = document.createElement('div');
        message.innerText = error;
        progressElement.innerText = 'Test failed';
        resultElement.appendChild(message);
    });
}